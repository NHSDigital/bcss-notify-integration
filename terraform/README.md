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
└── versions.tf          # Terraform and provider version constraints
```

### **Modules**
The `modules/` directory contains reusable Terraform modules:
- **Lambda (Batch Processor & Request Handler):** Deploys and configures AWS Lambda functions with necessary permissions and triggers.
- **S3:** Manages an S3 bucket for storing CSV files.
- **SQS:** Defines the message queue for async communication.
- **EventBridge:** Sets up scheduled triggers for the Batch Processor Lambda.
- **IAM:** Defines permissions for services like Lambda to interact with S3, SQS, and OracleDB.
- **Network:** Configures networking (VPC, subnets, security groups) to allow Lambdas to connect to the Oracle database.

### **Environments**
The `environments/` directory contains configuration files specific to each environment:
- **`dev/`**: Development configuration
- **`prod/`**: Production configuration
Each environment applies the required modules with environment-specific values.

### **State Management** (TBC)
Terraform state is stored remotely to allow for collaboration:
- **S3 Backend (`backend/s3_backend.tf`)** - Stores Terraform state in S3.
- **DynamoDB (`backend/dynamodb_locks.tf`)** - Enables state locking to prevent simultaneous updates.
