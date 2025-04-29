locals {
  date_str = formatdate("YYYYMMDDHHmmss", timestamp())
  filename = "function-${local.date_str}.zip"
  runtime  = "python3.13"
  secrets  = var.secrets

  lambda_dir   = "${path.module}/../../../batch_notification_processor"
  packages_dir = "$(pipenv --venv)/lib/${local.runtime}/site-packages"
}

resource "null_resource" "zipfile" {
  provisioner "local-exec" {
    command     = "${path.module}/../../scripts/build_lambda.sh ${path.module}/build/ ${local.lambda_dir} ${local.packages_dir} ${local.filename}"
    working_dir = path.module
  }
  triggers = {
    always_run = "${timestamp()}"
  }
}

resource "aws_lambda_function" "batch_notification_processor" {
  depends_on    = [null_resource.zipfile]
  function_name = "${var.team}-${var.project}-batch-notification-processor-${var.environment}"
  handler       = "lambda_function.lambda_handler" # File.function
  runtime       = local.runtime
  filename      = "${path.module}/${local.filename}"
  role          = var.batch_notification_processor_lambda_role_arn

  timeout     = 300
  memory_size = 128

  vpc_config {
    subnet_ids         = var.subnet_ids
    security_group_ids = [var.security_group]
  }

  environment {
    variables = {
      COMMGT_BASE_URL = local.secrets["commgt_base_url"]
      DATABASE_PORT   = local.secrets["database_port"]
      ENVIRONMENT     = var.environment
      OAUTH_TOKEN_URL = local.secrets["oauth_token_url"]
      REGION_NAME     = var.region

      LAMBDA_STATUS_CHECK_ARN      = var.message_status_handler_lambda_arn
      LAMBDA_STATUS_CHECK_ROLE_ARN = var.message_status_handler_lambda_role_arn
    }
  }

  tags = var.tags
}
