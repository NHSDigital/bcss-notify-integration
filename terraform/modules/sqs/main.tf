resource "aws_sqs_queue" "sqs_queue" {
  name                       = "${var.team}-${var.project}-sqs-${var.environment}"
  delay_seconds              = 0
  max_message_size           = 262144
  message_retention_seconds  = 345600
  receive_wait_time_seconds  = 0
  visibility_timeout_seconds = 300
  tags                       = var.tags
}