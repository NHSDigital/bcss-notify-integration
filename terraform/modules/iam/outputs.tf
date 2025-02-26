output "batch_processor_lambda_role_arn" {
  value = aws_iam_role.batch_processor_lambda_role.arn
}

output "request_handler_lambda_role_arn" {
  value = aws_iam_role.request_handler_lambda_role.arn
}