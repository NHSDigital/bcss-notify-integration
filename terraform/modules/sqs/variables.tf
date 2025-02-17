variable "team" {
  type    = string
  default = "bcss"
}

variable "project" {
  type    = string
  default = "comms"
}

variable "environment" {
  type = string
}

variable "tags" {
  type        = map(string)
  description = "A map of tags to apply to the resource."
}