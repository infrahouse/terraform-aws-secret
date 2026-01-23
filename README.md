# terraform-aws-secret

See the [Implementing Compliant Secrets with AWS Secrets Manager](https://infrahouse.com/blog/2024-09-29-compliant-secrets/) blog post.

```hcl
module "secret" {
  source  = "infrahouse/secret/aws"
  version = "1.1.1"
  
  secret_description = "API token to some service."
  secret_name        = "API_KEY"
  secret_value       = random_id.api_key.hex
  environment        = "production"
  writers      = [
    data.aws_iam_role.sso["AWSAdministratorAccess"].arn,
  ]
  readers = [
    data.aws_iam_role.sso["Developers"].arn,
    aws_iam_role.ecs_task.arn,
  ]
}
```

## Use Cases

This module supports two primary workflows for managing secrets:

### Use Case 1: Known Secret Value

When you know the secret value at deployment time (e.g., generated passwords, API keys from other Terraform resources):

```hcl
module "database_password" {
  source  = "infrahouse/secret/aws"
  version = "~> 1.1"

  secret_name        = "database-password"
  secret_description = "PostgreSQL database password"
  secret_value       = random_password.db.result  # Value known at apply time
  environment        = "production"
  service_name       = "myapp"
  readers            = [aws_iam_role.app.arn]
}
```

### Use Case 2: External Secret Value (Placeholder)

When the secret value comes from an external source (e.g., third-party API keys, manually obtained credentials):

```hcl
module "external_api_key" {
  source  = "infrahouse/secret/aws"
  version = "~> 1.1"

  secret_name        = "pypi-api-token"
  secret_description = "PyPI API token for package publishing"
  # secret_value omitted - will be set manually later
  environment        = "production"
  service_name       = "ci-pipeline"
  writers            = [data.aws_iam_role.admin.arn]
  readers            = [aws_iam_role.ci.arn]
}
```

In this workflow:
1. Terraform creates the secret with a placeholder value ("NoValue")
2. An administrator later sets the real value via AWS Console or CLI
3. The module's `secret_value` output automatically reflects the current value in AWS

This "placeholder" workflow is useful when:
- Obtaining API keys from third-party services that require manual registration
- Migrating existing secrets into Terraform management
- Secrets that must be rotated manually by security teams

## Prerequisites

This module requires **Python 3** and **boto3** to be installed where Terraform runs.
This is needed to read the current secret value from AWS (see [Design Decisions](/.claude/design-decisions.md)).

```bash
pip install boto3
```

<!-- BEGIN_TF_DOCS -->

## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | ~> 1.5 |
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | >= 5.11, < 7.0 |
| <a name="requirement_null"></a> [null](#requirement\_null) | ~> 3.0 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_aws"></a> [aws](#provider\_aws) | 6.28.0 |
| <a name="provider_external"></a> [external](#provider\_external) | 2.3.5 |
| <a name="provider_null"></a> [null](#provider\_null) | 3.2.4 |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [aws_secretsmanager_secret.secret](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/secretsmanager_secret) | resource |
| [aws_secretsmanager_secret_version.current](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/secretsmanager_secret_version) | resource |
| [null_resource.validate_secret_name](https://registry.terraform.io/providers/hashicorp/null/latest/docs/resources/resource) | resource |
| [aws_caller_identity.current](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/caller_identity) | data source |
| [aws_iam_policy_document.permission-policy](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy_document) | data source |
| [aws_iam_role.caller_role](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_role) | data source |
| [aws_iam_roles.access-analyzer](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_roles) | data source |
| [aws_region.current](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/region) | data source |
| [external_external.secret_value](https://registry.terraform.io/providers/hashicorp/external/latest/docs/data-sources/external) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_admins"></a> [admins](#input\_admins) | List of role ARNs that will have all permissions of the secret. | `list(string)` | `null` | no |
| <a name="input_environment"></a> [environment](#input\_environment) | Name of environment. | `string` | n/a | yes |
| <a name="input_owner"></a> [owner](#input\_owner) | A tag owner with this value will be placed on a secret. | `string` | `null` | no |
| <a name="input_readers"></a> [readers](#input\_readers) | List of role ARNs that will have read permissions of the secret. | `list(string)` | `null` | no |
| <a name="input_secret_description"></a> [secret\_description](#input\_secret\_description) | The secret description in AWS Secretsmanager. | `string` | n/a | yes |
| <a name="input_secret_name"></a> [secret\_name](#input\_secret\_name) | Name of the secret in AWS Secretsmanager. Either secret\_name or secret\_name\_prefix must be set. | `string` | `null` | no |
| <a name="input_secret_name_prefix"></a> [secret\_name\_prefix](#input\_secret\_name\_prefix) | Name prefix of the secret in AWS Secretsmanager. Either secret\_name or secret\_name\_prefix must be set. | `string` | `null` | no |
| <a name="input_secret_value"></a> [secret\_value](#input\_secret\_value) | Optional value of the secret. | `string` | `null` | no |
| <a name="input_service_name"></a> [service\_name](#input\_service\_name) | Descriptive name of a service that will use this secret.<br/>DEPRECATED: Default value "unknown" will be removed in v2.0. Please specify explicitly. | `string` | `"unknown"` | no |
| <a name="input_tags"></a> [tags](#input\_tags) | Tags to apply to secret and other resources the module creates. | `map(string)` | `{}` | no |
| <a name="input_writers"></a> [writers](#input\_writers) | List of role ARNs that will have write permissions of the secret. | `list(string)` | `null` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_secret_arn"></a> [secret\_arn](#output\_secret\_arn) | ARN of the created secret |
| <a name="output_secret_id"></a> [secret\_id](#output\_secret\_id) | ID of the created secret |
| <a name="output_secret_name"></a> [secret\_name](#output\_secret\_name) | Name of the created secret |
| <a name="output_secret_value"></a> [secret\_value](#output\_secret\_value) | The current secret value. If the value isn't set yet, return `null`. |
<!-- END_TF_DOCS -->
