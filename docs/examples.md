# Examples

Common use cases for terraform-aws-secret.

## Database Password

Store a generated database password:

```hcl
resource "random_password" "db" {
  length  = 32
  special = true
}

module "db_password" {
  source  = "registry.infrahouse.com/infrahouse/secret/aws"
  version = "1.1.1"

  secret_name        = "postgres-password"
  secret_description = "PostgreSQL database password"
  secret_value       = random_password.db.result
  environment        = "production"
  service_name       = "database"

  readers = [
    aws_iam_role.app.arn,
  ]
  admins = [
    data.aws_iam_role.dba.arn,
  ]
}
```

## External API Key (Placeholder)

Create a secret for an API key that will be set manually:

```hcl
module "stripe_api_key" {
  source  = "registry.infrahouse.com/infrahouse/secret/aws"
  version = "1.1.1"

  secret_name        = "stripe-api-key"
  secret_description = "Stripe API key for payment processing"
  # secret_value omitted - will be set via AWS Console
  environment        = "production"
  service_name       = "payments"

  readers = [
    aws_iam_role.payment_service.arn,
  ]
  writers = [
    data.aws_iam_role.admin.arn,
  ]
}
```

After deployment, set the value. These are standard AWS Secrets Manager secrets, so you can use
the AWS CLI directly:

```bash
aws secretsmanager put-secret-value \
  --secret-id stripe-api-key \
  --secret-string "sk_live_..."
```

Or use [infrahouse-toolkit](https://pypi.org/project/infrahouse-toolkit/) for a more convenient
interactive experience:

```bash
ih-secrets set stripe-api-key
# You will be prompted to enter the secret value securely

# Or read from a file:
ih-secrets set stripe-api-key /path/to/secret-file
```

## SSO Role Access with Wildcards

Grant access to AWS SSO roles using wildcards:

```hcl
module "app_secret" {
  source  = "registry.infrahouse.com/infrahouse/secret/aws"
  version = "1.1.1"

  secret_name        = "app-config"
  secret_description = "Application configuration secrets"
  secret_value       = jsonencode(local.app_config)
  environment        = "production"
  service_name       = "webapp"

  readers = [
    "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/AWSReservedSSO_Developers_*",
  ]
  admins = [
    "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/AWSReservedSSO_Admin_*",
  ]
}
```

## ECS Task Secret

Provide secrets to an ECS task. Note: ECS injects secrets via the **task execution role**,
not the task role:

```hcl
module "api_token" {
  source  = "registry.infrahouse.com/infrahouse/secret/aws"
  version = "1.1.1"

  secret_name        = "external-api-token"
  secret_description = "Token for external API"
  secret_value       = var.api_token
  environment        = "production"
  service_name       = "worker"

  readers = [
    aws_iam_role.ecs_task_execution.arn,  # Execution role, not task role
  ]
}

resource "aws_ecs_task_definition" "worker" {
  # ...
  container_definitions = jsonencode([
    {
      name = "worker"
      secrets = [
        {
          name      = "API_TOKEN"
          valueFrom = module.api_token.secret_arn
        }
      ]
      # ...
    }
  ])
}
```

## Multiple Secrets with Prefix

Create multiple related secrets using name prefix:

```hcl
module "service_secrets" {
  for_each = toset(["api-key", "db-password", "jwt-secret"])

  source  = "registry.infrahouse.com/infrahouse/secret/aws"
  version = "1.1.1"

  secret_name_prefix = "myservice-${each.key}-"
  secret_description = "Secret: ${each.key}"
  environment        = var.environment
  service_name       = "myservice"

  readers = [
    aws_iam_role.service.arn,
  ]
}
```