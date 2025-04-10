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

variable "tags" {
  type = map(string)
  default = {
    Service = "bcss"
  }
  description = "A map of tags to apply to the resource"
}