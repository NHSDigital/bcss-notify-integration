locals {
  runtime = "python3.13"
  secrets = var.secrets

  build_trigger = sha256(timestamp())
}

resource "null_resource" "batch_notification_processor_lambda_zip" {
  provisioner "local-exec" {
    command     = "./build.sh batch_notification_processor"
    working_dir = path.module
  }
  triggers = {
    always_run = local.build_trigger
  }
}

resource "aws_lambda_function" "batch_notification_processor" {
  depends_on       = [null_resource.batch_notification_processor_lambda_zip]
  filename         = "${path.module}/batch_notification_processor.zip"
  function_name    = "${var.team}-${var.project}-batch-notification-processor-${var.environment}"
  handler          = "lambda_function.lambda_handler"
  memory_size      = 256
  role             = var.batch_notification_processor_lambda_role_arn
  runtime          = local.runtime
  source_code_hash = local.build_trigger
  timeout          = 300

  vpc_config {
    subnet_ids         = var.subnet_ids
    security_group_ids = [var.security_group]
  }

  layers = [
    var.parameters_and_secrets_lambda_extension_arn,
    var.python_packages_layer_arn
  ]

  environment {
    variables = {
      COMMGT_BASE_URL = local.secrets["commgt_base_url"]
      DATABASE_PORT   = local.secrets["database_port"]
      ENVIRONMENT     = var.environment
      OAUTH_TOKEN_URL = local.secrets["oauth_token_url"]
      REGION_NAME     = var.region
      SECRET_ARN      = var.secrets_arn

      LAMBDA_STATUS_CHECK_ARN      = aws_lambda_function.message_status_handler.arn
      LAMBDA_STATUS_CHECK_ROLE_ARN = var.message_status_handler_lambda_role_arn

      PARAMETERS_SECRETS_EXTENSION_CACHE_ENABLED = "true"
      PARAMETERS_SECRETS_EXTENSION_LOG_LEVEL     = "debug"
    }
  }

  tags = var.tags
}

resource "null_resource" "message_status_handler_lambda_zip" {
  provisioner "local-exec" {
    command     = "./build.sh message_status_handler"
    working_dir = path.module
  }
  triggers = {
    always_run = local.build_trigger
  }
}

resource "aws_lambda_function" "message_status_handler" {
  depends_on       = [null_resource.message_status_handler_lambda_zip]
  filename         = "${path.module}/message_status_handler.zip"
  function_name    = "${var.team}-${var.project}-message-status-handler-${var.environment}"
  handler          = "scheduled_lambda_function.lambda_handler"
  memory_size      = 128
  role             = var.message_status_handler_lambda_role_arn
  runtime          = local.runtime
  source_code_hash = local.build_trigger
  timeout          = 300

  vpc_config {
    subnet_ids         = var.subnet_ids
    security_group_ids = [var.security_group]
  }

  layers = [
    var.parameters_and_secrets_lambda_extension_arn,
    var.python_packages_layer_arn
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
