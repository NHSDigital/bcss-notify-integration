terraform {
  backend "s3" {
    key    = "bcss/infrastructure/communication-management/terraform.tfstate"
    region = "eu-west-2"
  }
}

