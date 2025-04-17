output "batch_notification_processor_lambda_role_arn" {
  value = aws_iam_role.batch_notification_processor_lambda_role.arn
}

output "message_status_handler_lambda_role_arn" {
  value = aws_iam_role.message_status_handler_lambda_role.arn
}

