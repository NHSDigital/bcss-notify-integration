locals {
  runtime       = "python3.13"
  project_root  = "${path.module}/../../.."
  build_trigger = sha256(timestamp())
}

resource "null_resource" "packages_zipfile" {
  provisioner "local-exec" {
    command     = "./build.sh"
    working_dir = path.module
  }
  triggers = {
    always_run = local.build_trigger
  }
}

resource "aws_lambda_layer_version" "python_packages" {
  depends_on          = [null_resource.packages_zipfile]
  layer_name          = "${var.team}-${var.project}-python-packages-${var.environment}"
  compatible_runtimes = [local.runtime]
  filename            = "${path.module}/packages.zip"
  source_code_hash    = local.build_trigger
}
