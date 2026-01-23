# Configuration

This page documents all variables and outputs for the terraform-aws-secret module.

## Required Variables

### secret_description

The description for the secret in AWS Secrets Manager.

```hcl
secret_description = "Database password for production PostgreSQL"
```

### environment

Name of the environment. Must contain only lowercase letters, numbers, and underscores.

```hcl
environment = "production"
```

## Secret Naming

You must specify exactly one of `secret_name` or `secret_name_prefix`.

### secret_name

Fixed name for the secret:

```hcl
secret_name = "database-password"
```

### secret_name_prefix

Prefix for auto-generated secret names (useful for multiple instances):

```hcl
secret_name_prefix = "api-key-"
# Results in names like: api-key-20240101120000
```

## Secret Value

### secret_value

The secret value to store. If omitted, creates a placeholder for external management.

```hcl
# Option 1: Provide value directly
secret_value = var.database_password

# Option 2: Use generated password
secret_value = random_password.db.result

# Option 3: Omit for external management (placeholder workflow)
# secret_value = null  # Default
```

## Access Control

### admins

List of IAM role ARNs with full permissions (read, write, delete):

```hcl
admins = [
  "arn:aws:iam::123456789012:role/SecretAdmins",
]
```

### readers

List of IAM role ARNs with read-only access:

```hcl
readers = [
  "arn:aws:iam::123456789012:role/MyApp",
  "arn:aws:iam::123456789012:role/AWSReservedSSO_Developers_*",  # Wildcard
]
```

### writers

List of IAM role ARNs with read and write access (no delete):

```hcl
writers = [
  "arn:aws:iam::123456789012:role/CI-Pipeline",
]
```

## Tagging

### service_name

Descriptive name of the service using this secret:

```hcl
service_name = "payment-service"
```

!!! warning "Deprecation Notice"
    The default value "unknown" is deprecated and will be removed in v2.0.
    Always specify `service_name` explicitly.

### owner

Override the automatic owner tag (defaults to caller role ARN):

```hcl
owner = "team-platform@company.com"
```

### tags

Additional tags to apply:

```hcl
tags = {
  CostCenter = "engineering"
  Project    = "website-redesign"
}
```

## Outputs

| Output | Description |
|--------|-------------|
| `secret_arn` | ARN of the created secret |
| `secret_name` | Name of the secret |
| `secret_id` | ID of the secret |
| `secret_value` | Current secret value (sensitive, null if not set) |