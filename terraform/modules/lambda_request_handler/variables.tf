variable "team" {
  type = string
}

variable "project" {
  type = string
}

variable "environment" {
  type = string
}

variable "request_handler_lambda_role_arn" {
  type        = string
  description = "ARN for the batch processor lambda role"
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