# Terraform Infrastructure

This directory contains the **Terraform** configuration for provisioning cloud infrastructure in AWS. It follows a **modular approach** to ensure reusability, scalability, and separation of concerns.

## **Project Structure**

```
terraform/
├── backend/            # Remote state storage setup
│   ├── s3_backend.tf
│   └── dynamodb_locks.tf
├── modules/            # Reusable Terraform modules
│   ├── lambda_batch_processor/  # Module for Batch Processor Lambda
│   ├── lambda_request_handler/ # Module for Request Handler Lambda
│   ├── s3/                   # S3 bucket module
│   ├── sqs/                  # SQS queue module
│   ├── eventbridge/          # EventBridge rules module
│   ├── iam/                  # IAM roles and policies module
│   └── network/              # VPC, subnets, security groups module
├── environments/         # Environment-specific configurations
│   ├── dev/
│   └── prod/
├── providers.tf         # AWS provider configuration
└── versions.tf         # Terraform and provider version constraints
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
The `environments/` directory contains configuration files specific to each environment:
- **`dev/`**: Development configuration
- **`prod/`**: Production configuration

Each environment applies the required modules with environment-specific values.

### Terraform Remote State & State Locking

#### Overview
Terraform uses **Amazon S3** for remote state storage and **DynamoDB** for state locking.  
Each environment (e.g., `dev`, `staging`, `prod`) has its own state file to prevent conflicts and maintain isolation.

---

### Remote State Configuration

#### S3 Backend Setup (Per Environment)
Each environment has its own Terraform state file stored in an S3 bucket.

Example backend configuration (`backend.tf`):
```hcl
terraform {
  backend "s3" {
    bucket         = "bcss-terraform-nonprod-iac"                                    # Shared S3 bucket
    key            = "bcss/infrastructure/communication-management/terraform.tfstate" # Environment-specific state file
    region         = "eu-west-2"
    encrypt        = true
    dynamodb_table = "bcss-communication-management-terraform-lock-dev"              # State locking
  }
}