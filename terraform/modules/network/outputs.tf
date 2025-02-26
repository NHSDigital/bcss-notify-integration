output "private_subnet_ids" {
  value       = data.aws_subnets.private.ids
  description = "List of private subnet IDs"
}

output "security_group" {
  value       = data.aws_security_group.lambda.id
  description = "List of private subnet IDs"
}