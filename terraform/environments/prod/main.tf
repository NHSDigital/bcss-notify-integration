module "batch_notification_processor" {
  source                          = "../../modules/batch_notification_processor"
  team                            = var.team
  project                         = var.project
  environment                     = var.environment
  batch_processor_lambda_role_arn = module.iam.batch_processor_lambda_role_arn
  tags                            = var.tags
  subnet_ids                      = module.network.private_subnet_ids
  security_group                  = module.network.security_group
}

module "lambda_request_handler" {
  source                          = "../../modules/lambda_request_handler"
  team                            = var.team
  project                         = var.project
  environment                     = var.environment
  request_handler_lambda_role_arn = module.iam.request_handler_lambda_role_arn
  tags                            = var.tags
  sqs_queue_arn                   = module.sqs.sqs_queue_arn
  subnet_ids                      = module.network.private_subnet_ids
  security_group                  = module.network.security_group
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
  source                      = "../../modules/eventbridge"
  team                        = var.team
  project                     = var.project
  environment                 = var.environment
  batch_processor_lambda_arn  = module.batch_notification_processor.batch_processor_arn
  batch_processor_lambda_name = module.batch_notification_processor.batch_processor_name
}

module "iam" {
  source                     = "../../modules/iam"
  team                       = var.team
  project                    = var.project
  environment                = var.environment
  sqs_queue_arn              = module.sqs.sqs_queue_arn
  notification_s3_bucket_arn = module.s3.bucket_arn
  tags                       = var.tags
}

module "network" {
  source = "../../modules/network"
}