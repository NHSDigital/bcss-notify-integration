variable "team" {
  type = string
}

variable "project" {
  type = string
}

variable "environment" {
  type = string
}

variable "kms_arn" {
  type        = string
  description = "ARN for the AWS KMS key used to encrypt the Lambda secrets"
}

variable "scheduler_arn" {
  type        = string
  description = "ARN for the AWS Scheduler used to schedule the Lambda function"
}

variable "secrets_arn" {
  type        = string
  description = "ARN for the AWS Secrets Manager secret containing the Lambda secrets"
}

variable "sqs_queue_arn" {
  type        = string
  description = "ARN for the BCSS Communication Management SQS Queue"
}

variable "message_status_handler_lambda_arn" {
  type        = string
  description = "ARN for the Message Status Handler Lambda function"
}

variable "notification_s3_bucket_arn" {
  type        = string
  description = "ARN for the BCSS Communication Management S3 Bucket"
}

variable "tags" {
  type        = map(string)
  description = "A map of tags to apply to the resource."
}
