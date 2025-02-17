output "batch_processor_arn" {
  value = aws_lambda_function.batch_processor.arn
}

output "batch_processor_name" {
  value = aws_lambda_function.batch_processor.function_name
}