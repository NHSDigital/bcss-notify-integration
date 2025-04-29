locals {
  date_str = formatdate("YYYYMMDDHHmmss", timestamp())
  filename = "function-${local.date_str}.zip"
  packages = "packages-${local.date_str}.zip"
  runtime  = "python3.13"
  secrets  = var.secrets

  lambda_dir   = "${path.module}/../../../message_status_handler"
  packages_dir = "$(pipenv --venv)/lib/${local.runtime}/site-packages"
}

resource "null_resource" "packages_zipfile" {
  provisioner "local-exec" {
    command     = "${path.module}/../../scripts/packages.sh ${path.module}/build/ ${local.packages_dir} ${local.packages}"
    working_dir = path.module
  }
  triggers = {
    always_run = "${timestamp()}"
  }
}

resource "aws_lambda_layer_version" "python_packages" {
  depends_on          = [null_resource.packages_zipfile]
  layer_name          = "${var.team}-${var.project}-python-packages-${var.environment}"
  compatible_runtimes = [local.runtime]
  filename            = "${path.module}/${local.packages}"
}

resource "null_resource" "zipfile" {
  provisioner "local-exec" {
    command     = "${path.module}/../../scripts/lambda.sh ${path.module}/build/ ${local.lambda_dir} ${local.filename}"
    working_dir = path.module
  }
  triggers = {
    always_run = "${timestamp()}"
  }
}

resource "aws_lambda_function" "message_status_handler" {
  depends_on    = [null_resource.zipfile]
  function_name = "${var.team}-${var.project}-message-status-handler-${var.environment}"
  handler       = "scheduled_lambda_function.lambda_handler"
  runtime       = local.runtime
  filename      = "${path.module}/${local.filename}"
  role          = var.message_status_handler_lambda_role_arn

  timeout     = 300
  memory_size = 128

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
