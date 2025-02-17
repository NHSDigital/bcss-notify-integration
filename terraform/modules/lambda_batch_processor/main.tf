resource "aws_lambda_function" "batch_processor" {
  function_name    = "${var.team}-${var.project}-batch-processor-${var.environment}"
  handler          = "lambda_function.lambda_handler" # File.function
  runtime          = "python3.12"
  filename         = "../../../lambda_function.zip"
  source_code_hash = filebase64sha256("../../../lambda_function.zip")
  role             = var.batch_processor_lambda_role_arn

  timeout     = 300
  memory_size = 128

  vpc_config {
    subnet_ids         = var.subnet_ids
    security_group_ids = [var.security_group]
  }

  environment {
    variables = {
      ENVIRONMENT = var.environment
    }
  }

  tags = var.tags
}