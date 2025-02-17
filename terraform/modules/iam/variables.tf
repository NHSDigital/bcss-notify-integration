variable "team" {
  type = string
}

variable "project" {
  type = string
}

variable "environment" {
  type = string
}

variable "sqs_queue_arn" {
  type        = string
  description = "ARN for the BCSS Comms SQS Queue"
}

variable "comms_s3_bucket_arn" {
  type        = string
  description = "ARN for the BCSS Comms S3 Bucket"
}

variable "tags" {
  type        = map(string)
  description = "A map of tags to apply to the resource."
}
