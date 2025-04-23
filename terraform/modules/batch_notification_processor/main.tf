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
      ENVIRONMENT   = var.environment
      REGION_NAME   = var.region
      DATABASE_USER = local.secrets["username"]
      DATABASE_PASS = local.secrets["password"]
      DATABASE_HOST = local.secrets["host"]
      DATABASE_SID  = local.secrets["dbname"]
      DATABASE_PORT = local.secrets["port"]
    }
  }

  tags = var.tags
}
