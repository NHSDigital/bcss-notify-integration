terraform {
  backend "s3" {
    bucket         = "bcss-terraform-nonprod-iac"
    key            = "bcss/infrastructure/communication-management/terraform.tfstate"
    region         = "eu-west-2"
    dynamodb_table = "bcss-comms-manager-terraform-lock-dev"
  }
}

