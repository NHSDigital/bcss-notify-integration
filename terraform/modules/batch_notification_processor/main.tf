locals {
  filename = "function.zip"
  packages = "packages.zip"
  runtime  = "python3.13"
  secrets  = var.secrets

  project_root = "${path.module}/../../.."
  lambda_dir   = "${local.project_root}/batch_notification_processor"
  packages_dir = "$(pipenv --venv)/lib/${local.runtime}/site-packages"
  git_sha      = sha256(file("${local.project_root}/.git/refs/remotes/origin/main"))
}

resource "null_resource" "packages_zipfile" {
  provisioner "local-exec" {
    command     = "${path.module}/../../scripts/packages.sh ${path.module}/build/ ${local.packages_dir} ${local.packages}"
    working_dir = path.module
  }
  triggers = {
    always_run = "${sha256(file("${local.project_root}/Pipfile.lock"))}"
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

resource "aws_lambda_function" "batch_notification_processor" {
  depends_on       = [null_resource.lambda_zip]
  filename         = "${path.module}/${local.filename}"
  function_name    = "${var.team}-${var.project}-batch-notification-processor-${var.environment}"
  handler          = "lambda_function.lambda_handler"
  memory_size      = 128
  role             = var.batch_notification_processor_lambda_role_arn
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
      OAUTH_TOKEN_URL = local.secrets["oauth_token_url"]
      REGION_NAME     = var.region
      SECRET_ARN      = var.secrets_arn

      LAMBDA_STATUS_CHECK_ARN      = var.message_status_handler_lambda_arn
      LAMBDA_STATUS_CHECK_ROLE_ARN = var.message_status_handler_lambda_role_arn

      PARAMETERS_SECRETS_EXTENSION_CACHE_ENABLED = "true"
      PARAMETERS_SECRETS_EXTENSION_LOG_LEVEL     = "debug"
    }
  }

  tags = var.tags
}

resource "null_resource" "remove_zipfiles" {
  depends_on = [aws_lambda_function.batch_notification_processor]
  provisioner "local-exec" {
    command     = "rm -f ${path.module}/*.zip"
    working_dir = path.module
  }
}
