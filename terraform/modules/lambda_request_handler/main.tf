resource "aws_lambda_function" "request_handler" {
  function_name    = "${var.team}-${var.project}-request-handler-${var.environment}"
  handler          = "lambda_function.lambda_handler"
  runtime          = "python3.12"
  filename         = "../../../lambda_function.zip"
  source_code_hash = filebase64sha256("../../../lambda_function.zip")
  role             = var.request_handler_lambda_role_arn

  timeout     = 300
  memory_size = 128

  vpc_config {
    subnet_ids         = var.subnet_ids
    security_group_ids = [var.security_group]
  }

  environment {
    variables = {
      ENVIRONMENT = var.project
    }
  }

  tags = var.tags
}

resource "aws_lambda_event_source_mapping" "sqs_trigger" {
  event_source_arn = var.sqs_queue_arn
  function_name    = aws_lambda_function.request_handler.function_name
  batch_size       = 10 # Adjust as needed
}

resource "aws_lambda_permission" "allow_sqs_to_call_lambda" {
  statement_id  = "AllowSQSInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.request_handler.function_name
  principal     = "sqs.amazonaws.com"
  source_arn    = var.sqs_queue_arn
}