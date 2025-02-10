resource "aws_s3_bucket" "s3_bucket" {
  bucket = "${var.team}-${var.project}-s3-${var.environment}"
  tags   = var.tags
}