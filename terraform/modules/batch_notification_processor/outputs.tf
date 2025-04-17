output "batch_notification_processor_arn" {
  value = aws_lambda_function.batch_notification_processor.arn
}

output "batch_notification_processor_name" {
  value = aws_lambda_function.batch_notification_processor.function_name
}

