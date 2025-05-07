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
  default = "prod"
}

variable "region" {
  type    = string
  default = "eu-west-2"
}

variable "kms_arn" {
  type    = string
  default = "arn:aws:kms:eu-west-2:123456789012:key/fe1a2b3c-4d5e-6f7g-8h9i-j0k1l2m3n4o5"
}

variable "scheduler_arn" {
  type    = string
  default = "arn:aws:scheduler:eu-west-2:123456789012:schedule/bcss-scheduler"
}

variable "secrets_arn" {
  type    = string
  default = "arn:aws:secretsmanager:eu-west-2:123456789012:secret:TBC"
}

variable "tags" {
  type = map(string)
  default = {
    Service = "bcss"
  }
  description = "A map of tags to apply to the resource."
}

