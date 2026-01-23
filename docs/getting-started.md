# Getting Started

This guide walks you through deploying your first secret with terraform-aws-secret.

## Prerequisites

### Terraform

- Terraform >= 1.5

### Python

This module requires **Python 3** and **boto3** where Terraform runs:

```bash
pip install boto3
```

This is needed to read the current secret value from AWS Secrets Manager.

### AWS Provider Configuration

Configure the AWS provider with appropriate credentials:

```hcl
provider "aws" {
  region = "us-west-2"

  default_tags {
    tags = {
      created_by = "terraform"
    }
  }
}
```

## First Deployment

### Step 1: Create the Module Configuration

```hcl
module "my_secret" {
  source  = "registry.infrahouse.com/infrahouse/secret/aws"
  version = "1.1.1"

  secret_name        = "my-first-secret"
  secret_description = "My first secret managed by Terraform"
  secret_value       = "super-secret-value"
  environment        = "development"
  service_name       = "my-app"

  readers = [
    "arn:aws:iam::123456789012:role/my-app-role",
  ]
}
```

### Step 2: Initialize and Apply

```bash
terraform init
terraform plan
terraform apply
```

### Step 3: Verify

Check the outputs:

```bash
terraform output secret_arn
terraform output secret_name
```

## Next Steps

- [Configuration](configuration.md) - Learn about all available variables
- [Examples](examples.md) - See common use cases
- [Architecture](architecture.md) - Understand how the module works