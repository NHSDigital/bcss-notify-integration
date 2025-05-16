output "batch_notification_processor_arn" {
  value = aws_lambda_function.batch_notification_processor.arn
}

output "batch_notification_processor_name" {
  value = aws_lambda_function.batch_notification_processor.function_name
}

output "message_status_handler_arn" {
  value = aws_lambda_function.message_status_handler.arn
}

output "message_status_handler_name" {
  value = aws_lambda_function.message_status_handler.function_name
}
