# Terraform Infrastructure

This directory contains the **Terraform** configuration for provisioning cloud infrastructure in AWS. It follows a **modular approach** to ensure reusability, scalability, and separation of concerns.

## **Project Structure**

```
terraform/
├── backend.tf                  # Remote state storage setup
├── config                      # Environment-specific configuration
│   ├── development.config      # Development environment backend config
│   ├── development.tfvars      # Development environment terraform variables
│   ├── production.config       # Production environment backend config
│   └── production.tfvars       # Production environment terraform variables
├── modules/                    # Reusable Terraform modules
│   ├── lambdas/                # Module for Batch Processor and Message Status Lambdas
│   ├── lambda_layer/           # Module for lambda layer
│   ├── s3/                     # S3 bucket module
│   ├── sqs/                    # SQS queue module
│   ├── eventbridge/            # EventBridge rules module
│   ├── iam/                    # IAM roles and policies module
│   └── network/                # VPC, subnets, security groups module
├── production.tfvars           # Environment-specific configuration
├── providers.tf                # AWS provider configuration
└── versions.tf                 # Terraform and provider version constraints
```

### **Modules**
The `modules/` directory contains reusable Terraform modules:
- **Lambda (Batch Processor & Request Handler):** Deploys and configures AWS Lambda functions with necessary permissions and triggers.
- **S3:** Manages an S3 bucket for storing notification data.
- **SQS:** Defines the message queue for async communication.
- **EventBridge:** Sets up scheduled triggers for the Batch Notification Processor Lambda.
- **IAM:** Defines permissions for services like Lambda to interact with AWS services.
- **Network:** Configures networking (VPC, subnets, security groups) for Lambda functions.

### **Environments**
We maintain different tfvars files specific to each environment:
- **`config/development.tfvars`**: Development configuration
- **`config/production.tfvars`**: Production configuration

Each environment applies the required modules with environment-specific values.

### **Usage**
1. **Initialize Terraform**: Run `terraform init --backend-config=config/development.config` to initialize the working directory and download required providers.
2. **Plan Changes**: Use `terraform plan -var-file=config/development.tfvars` to see the changes that will be applied.
3. **Apply Changes**: Execute `terraform apply -var-file=config/development.tfvars` to apply the changes to the specified environment.

### Terraform Remote State & State Locking

#### Overview
Terraform uses **Amazon S3** for remote state storage.  
Each environment (e.g., `dev`, `prod`) has its own state file to prevent conflicts and maintain isolation.

---

### Remote State Configuration

#### S3 Backend Setup (Per Environment)
Each environment has its own Terraform state file stored in an S3 bucket.

Example backend configuration (`backend.tf`):
```hcl
terraform {
  backend "s3" {
    key            = "bcss/infrastructure/communication-management/terraform.tfstate" # Environment-specific state file
    region         = "eu-west-2"
  }
}
```
