resource "null_resource" "zipfile" {
  provisioner "local-exec" {
    command     = <<EOT
      mkdir build
      cp ../../../message_status_handler/*.py build/
      cp -r $(pipenv --venv)/lib/python3.11/site-packages/* build/
      cd build
      rm -rf __pycache__
      rm -rf _pytest
      chmod -R 644 $(find . -type f)
      chmod -R 755 $(find . -type d)
      zip -r ../lambda_function.zip * -x *.zip
      cd ..
      rm -rf build
    EOT
    working_dir = path.module
  }
  triggers = {
    always_run = "${timestamp()}"
  }
}
resource "aws_lambda_function" "message_status_handler" {
  function_name    = "${var.team}-${var.project}-message-status-handler-${var.environment}"
  handler          = "scheduled_lambda_function.lambda_handler"
  runtime          = "python3.12"
  filename         = "${path.module}/lambda_function.zip"
  source_code_hash = filebase64sha256("${path.module}/lambda_function.zip")
  role             = var.message_status_handler_lambda_role_arn

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

