# terraform-aws-secret

Terraform module for managing AWS Secrets Manager secrets with fine-grained IAM-based access control.

## Overview

This module simplifies the creation and management of AWS Secrets Manager secrets by providing:

- **Role-based access control** through simple `admins`, `readers`, and `writers` lists
- **Automatic IAM policy generation** with least-privilege principles
- **Flexible secret values** - provide at deploy time or set externally via AWS Console/CLI
- **Compliance-ready tagging** for audit trails and cost tracking

## Features

- **Fine-grained access control** - Separate admin, reader, and writer roles
- **Wildcard support** - Use wildcards in role ARNs for dynamic matching (e.g., SSO roles)
- **Placeholder workflow** - Create secrets without values, set them later externally
- **Automatic tagging** - Environment, service, owner, and module version tags
- **AWS Provider v5 & v6 support** - Compatible with both provider versions

## Quick Start

```hcl
module "api_secret" {
  source  = "registry.infrahouse.com/infrahouse/secret/aws"
  version = "1.1.1"

  secret_name        = "my-api-key"
  secret_description = "API key for external service"
  secret_value       = var.api_key
  environment        = "production"
  service_name       = "my-service"

  readers = [
    aws_iam_role.app.arn,
  ]
  writers = [
    data.aws_iam_role.admin.arn,
  ]
}
```

## Next Steps

- [Getting Started](getting-started.md) - Prerequisites and first deployment
- [Configuration](configuration.md) - All variables explained
- [Examples](examples.md) - Common use cases
- [Architecture](architecture.md) - How it works