variable "team" {
  type    = string
  default = "bcss"
}

variable "project" {
  type    = string
  default = "comms"
}

variable "environment" {
  type    = string
  default = "dev"
}

variable "region" {
  type    = string
  default = "eu-west-2"
}

variable "secrets_arn" {
  type    = string
  default = "arn:aws:secretsmanager:eu-west-2:123456789012:secret:bcss-nonprod-secrets-123456"
}

variable "tags" {
  type = map(string)
  default = {
    Service = "bcss"
  }
  description = "A map of tags to apply to the resource."
}

