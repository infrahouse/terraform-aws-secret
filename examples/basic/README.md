# Basic Example

This example demonstrates basic usage of the terraform-aws-secret module.

## Usage

```bash
terraform init
terraform plan -var="reader_role_arn=arn:aws:iam::123456789012:role/MyAppRole"
terraform apply -var="reader_role_arn=arn:aws:iam::123456789012:role/MyAppRole"
```

## Requirements

- Terraform >= 1.5
- AWS Provider >= 5.11
- Python 3 with boto3 installed

## Inputs

| Name | Description | Type | Required |
|------|-------------|------|----------|
| reader_role_arn | ARN of the IAM role that should have read access | string | yes |

## Outputs

| Name | Description |
|------|-------------|
| secret_arn | ARN of the created secret |
| secret_name | Name of the created secret |