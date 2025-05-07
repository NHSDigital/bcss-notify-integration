team = "bcss"

project = "comms"

environment = "prod"
# TODO: ARNs TBC
kms_arn       = "arn:aws:kms:eu-west-2:730319765130:key/25da03db-7a99-4a15-bc38-2bf757f27fca"
scheduler_arn = "arn:aws:scheduler:eu-west-2:730319765130:schedule/default/lambda_status_check"
secrets_arn   = "arn:aws:secretsmanager:eu-west-2:730319765130:secret:TBC"
region        = "eu-west-2"


region      = "eu-west-2"

tags = {
  "Service" = "bcss"
}

