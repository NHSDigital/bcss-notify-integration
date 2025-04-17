resource "null_resource" "zipfile" {
  provisioner "local-exec" {
    command     = <<EOT
      mkdir build
      cp ../../../batch_notification_processor/*.py build/
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
resource "aws_lambda_function" "batch_notification_processor" {
  depends_on       = [null_resource.zipfile]
  function_name    = "${var.team}-${var.project}-batch-notification-processor-${var.environment}"
  handler          = "lambda_function.lambda_handler" # File.function
  runtime          = "python3.12"
  filename         = "${path.module}/lambda_function.zip"
  source_code_hash = filebase64sha256("${path.module}/lambda_function.zip")
  role             = var.batch_notification_processor_lambda_role_arn

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

