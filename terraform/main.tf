data "aws_secretsmanager_secret_version" "lambda_secrets" {
  secret_id = var.secrets_arn
}

module "lambda_layer" {
  source      = "./modules/lambda_layer"
  team        = var.team
  project     = var.project
  environment = var.environment
  region      = var.region
}

module "lambdas" {
  source      = "./modules/lambdas"
  team        = var.team
  project     = var.project
  environment = var.environment
  region      = var.region
  tags        = var.tags

  subnet_ids     = module.network.private_subnet_ids
  security_group = module.network.security_group
  secrets        = jsondecode(data.aws_secretsmanager_secret_version.lambda_secrets.secret_string)
  secrets_arn    = var.secrets_arn
  sqs_queue_arn  = module.sqs.sqs_queue_arn

  batch_notification_processor_lambda_role_arn = module.iam.batch_notification_processor_lambda_role_arn
  message_status_handler_lambda_role_arn       = module.iam.message_status_handler_lambda_role_arn
  python_packages_layer_arn                    = module.lambda_layer.python_packages_layer_arn
}

module "s3" {
  source      = "./modules/s3"
  team        = var.team
  project     = var.project
  environment = var.environment
  tags        = var.tags
}

module "sqs" {
  source      = "./modules/sqs"
  team        = var.team
  project     = var.project
  environment = var.environment
  tags        = var.tags
}

module "eventbridge" {
  source      = "./modules/eventbridge"
  team        = var.team
  project     = var.project
  environment = var.environment

  batch_notification_processor_lambda_arn  = module.lambdas.batch_notification_processor_arn
  batch_notification_processor_lambda_name = module.lambdas.batch_notification_processor_name
  message_status_handler_lambda_arn        = module.lambdas.message_status_handler_arn
  message_status_handler_lambda_name       = module.lambdas.message_status_handler_name
}

module "iam" {
  source                     = "./modules/iam"
  team                       = var.team
  project                    = var.project
  environment                = var.environment
  kms_arn                    = var.kms_arn
  scheduler_arn              = var.scheduler_arn
  secrets_arn                = var.secrets_arn
  sqs_queue_arn              = module.sqs.sqs_queue_arn
  notification_s3_bucket_arn = module.s3.bucket_arn
  tags                       = var.tags

  message_status_handler_lambda_arn = module.lambdas.message_status_handler_arn
}

module "network" {
  source = "./modules/network"
}

