variable "team" {
  type = string
}

variable "project" {
  type = string
}

variable "environment" {
  type = string
}

variable "region" {
  type = string
}

variable "secrets" {
  type        = map(string)
  description = "Lambda secretsmanager secrets"
}

variable "secrets_arn" {
  type        = string
  description = "ARN for the AWS Secrets Manager secret containing the Lambda secrets"
}

variable "batch_notification_processor_lambda_role_arn" {
  type        = string
  description = "ARN for the batch processor lambda role"
}

variable "message_status_handler_lambda_role_arn" {
  type        = string
  description = "ARN for the batch processor lambda role"
}

variable "parameters_and_secrets_lambda_extension_arn" {
  type        = string
  description = "ARN for the parameters and secrets lambda extension"
  default     = "arn:aws:lambda:eu-west-2:133256977650:layer:AWS-Parameters-and-Secrets-Lambda-Extension:12"
}

variable "python_packages_layer_arn" {
  type        = string
  description = "ARN for the Python packages layer"
}

variable "tags" {
  type        = map(string)
  description = "A map of tags to apply to the resource."
}

variable "sqs_queue_arn" {
  type        = string
  description = "ARN for the SQS Queue"
}

variable "subnet_ids" {
  type        = list(string)
  description = "Ids for subnets"
}

variable "security_group" {
  type        = string
  description = "Id for security group"
}

