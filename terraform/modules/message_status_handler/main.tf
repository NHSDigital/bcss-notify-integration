locals {
  filename = "function.zip"
  packages = "packages.zip"
  runtime  = "python3.13"
  secrets  = var.secrets

  project_root = "${path.module}/../../.."
  lambda_dir   = "${local.project_root}/message_status_handler"
  packages_dir = "$(pipenv --venv)/lib/${local.runtime}/site-packages"
  git_sha      = sha256(file("${local.project_root}/.git/refs/remotes/origin/main"))
}

resource "null_resource" "packages_zipfile" {
  provisioner "local-exec" {
    command     = "${path.module}/../../scripts/packages.sh ${path.module}/build/ ${local.packages_dir} ${local.packages}"
    working_dir = path.module
  }
  triggers = {
    always_run = "${sha256(file("${path.module}/../../../Pipfile.lock"))}"
  }
}

resource "aws_lambda_layer_version" "python_packages" {
  depends_on          = [null_resource.packages_zipfile]
  layer_name          = "${var.team}-${var.project}-python-packages-${var.environment}"
  compatible_runtimes = [local.runtime]
  filename            = "${path.module}/${local.packages}"
}

resource "null_resource" "lambda_zip" {
  provisioner "local-exec" {
    command     = "${path.module}/../../scripts/lambda.sh ${path.module}/build/ ${local.lambda_dir} ${local.filename}"
    working_dir = path.module
  }
  triggers = {
    always_run = local.git_sha
  }
}

resource "aws_lambda_function" "message_status_handler" {
  filename         = "${path.module}/${local.filename}"
  function_name    = "${var.team}-${var.project}-message-status-handler-${var.environment}"
  handler          = "scheduled_lambda_function.lambda_handler"
  memory_size      = 128
  role             = var.message_status_handler_lambda_role_arn
  runtime          = local.runtime
  source_code_hash = local.git_sha
  timeout          = 300

  vpc_config {
    subnet_ids         = var.subnet_ids
    security_group_ids = [var.security_group]
  }

  layers = [
    var.parameters_and_secrets_lambda_extension_arn,
    aws_lambda_layer_version.python_packages.arn
  ]

  environment {
    variables = {
      COMMGT_BASE_URL = local.secrets["commgt_base_url"]
      DATABASE_PORT   = local.secrets["database_port"]
      ENVIRONMENT     = var.environment
      REGION_NAME     = var.region
      SECRET_ARN      = var.secrets_arn

      PARAMETERS_SECRETS_EXTENSION_CACHE_ENABLED = "true"
      PARAMETERS_SECRETS_EXTENSION_LOG_LEVEL     = "debug"
    }
  }

  tags = var.tags
}

resource "aws_lambda_event_source_mapping" "sqs_trigger" {
  event_source_arn = var.sqs_queue_arn
  function_name    = aws_lambda_function.message_status_handler.function_name
  batch_size       = 10 # Adjust as needed
}

resource "aws_lambda_permission" "allow_sqs_to_call_lambda" {
  statement_id  = "AllowSQSInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.message_status_handler.function_name
  principal     = "sqs.amazonaws.com"
  source_arn    = var.sqs_queue_arn
}

resource "null_resource" "remove_zipfiles" {
  depends_on = [aws_lambda_function.message_status_handler]
  provisioner "local-exec" {
    command     = "rm -f ${path.module}/*.zip"
    working_dir = path.module
  }
}
