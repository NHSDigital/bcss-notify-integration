variable "team" {
  type = string
}

variable "project" {
  type = string
}

variable "environment" {
  type = string
}

variable "tags" {
  type        = map(string)
  description = "A map of tags to apply to the resource."
}