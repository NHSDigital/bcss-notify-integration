data "aws_secretsmanager_secret_version" "lambda_secrets" {
  secret_id = var.secrets_arn
}

module "batch_notification_processor" {
  source         = "../../modules/batch_notification_processor"
  team           = var.team
  project        = var.project
  environment    = var.environment
  secrets        = jsondecode(data.aws_secretsmanager_secret_version.lambda_secrets.secret_string)
  secrets_arn    = var.secrets_arn
  region         = var.region
  tags           = var.tags
  subnet_ids     = module.network.private_subnet_ids
  security_group = module.network.security_group

  batch_notification_processor_lambda_role_arn = module.iam.batch_notification_processor_lambda_role_arn
  message_status_handler_lambda_arn            = module.message_status_handler.message_status_handler_arn
  message_status_handler_lambda_role_arn       = module.iam.message_status_handler_lambda_role_arn
}

module "message_status_handler" {
  source         = "../../modules/message_status_handler"
  team           = var.team
  project        = var.project
  environment    = var.environment
  secrets        = jsondecode(data.aws_secretsmanager_secret_version.lambda_secrets.secret_string)
  secrets_arn    = var.secrets_arn
  region         = var.region
  tags           = var.tags
  sqs_queue_arn  = module.sqs.sqs_queue_arn
  subnet_ids     = module.network.private_subnet_ids
  security_group = module.network.security_group

  message_status_handler_lambda_role_arn = module.iam.message_status_handler_lambda_role_arn
}

module "s3" {
  source      = "../../modules/s3"
  team        = var.team
  project     = var.project
  environment = var.environment
  tags        = var.tags
}

module "sqs" {
  source      = "../../modules/sqs"
  team        = var.team
  project     = var.project
  environment = var.environment
  tags        = var.tags
}

module "eventbridge" {
  source      = "../../modules/eventbridge"
  team        = var.team
  project     = var.project
  environment = var.environment

  batch_notification_processor_lambda_arn  = module.batch_notification_processor.batch_notification_processor_arn
  batch_notification_processor_lambda_name = module.batch_notification_processor.batch_notification_processor_name
}

module "iam" {
  source                     = "../../modules/iam"
  team                       = var.team
  project                    = var.project
  environment                = var.environment
  kms_arn                    = var.kms_arn
  secrets_arn                = var.secrets_arn
  sqs_queue_arn              = module.sqs.sqs_queue_arn
  notification_s3_bucket_arn = module.s3.bucket_arn
  tags                       = var.tags
}

module "network" {
  source = "../../modules/network"
}

