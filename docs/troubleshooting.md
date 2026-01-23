# Troubleshooting

Common issues and solutions when using terraform-aws-secret.

## Access Denied Errors

### "AccessDeniedException" when reading secret

**Symptom:**
```
Error: AccessDeniedException: User: arn:aws:sts::... is not authorized to perform:
secretsmanager:GetSecretValue on resource: ...
```

**Solutions:**

1. Verify the role ARN is in the `readers`, `writers`, or `admins` list
2. Check for typos in the role ARN
3. If using SSO roles, ensure the wildcard pattern matches:
   ```hcl
   readers = [
     "arn:aws:iam::123456789012:role/AWSReservedSSO_Developers_*",
   ]
   ```

### "AccessDeniedException" with explicit deny

**Symptom:**
```
Error: ... with an explicit deny in a resource-based policy
```

**Cause:** The role is explicitly denied in the resource policy.

**Solution:** Ensure the role is not listed in multiple access lists. A role should be
in only one of `admins`, `readers`, or `writers`.

## Validation Errors

### "Exactly one of secret_name or secret_name_prefix must be set"

**Cause:** You specified both `secret_name` and `secret_name_prefix`, or neither.

**Solution:** Use exactly one:

```hcl
# Option 1: Fixed name
secret_name = "my-secret"

# Option 2: Auto-generated name with prefix
secret_name_prefix = "my-secret-"
```

### "environment must contain only lowercase letters, numbers, and underscores"

**Cause:** The `environment` value contains invalid characters.

**Solution:** Use only lowercase letters, numbers, and underscores:

```hcl
# Correct
environment = "production"
environment = "staging_us_west_2"

# Incorrect
environment = "Production"     # uppercase
environment = "us-west-2"      # hyphens
```

## Python/boto3 Errors

### "ModuleNotFoundError: No module named 'boto3'"

**Cause:** boto3 is not installed where Terraform runs.

**Solution:**
```bash
pip install boto3
```

### "Unable to locate credentials"

**Cause:** The Python script cannot find AWS credentials.

**Solution:** Ensure AWS credentials are available:

```bash
# Verify credentials
aws sts get-caller-identity

# If using profiles
export AWS_PROFILE=your-profile
```

## Secret Value Issues

### secret_value output is null

**Cause:** This is expected when:

1. `secret_value` input was null (placeholder workflow)
2. The secret contains "NoValue" placeholder

**Solution:** If using placeholder workflow, set the value. These are standard AWS Secrets
Manager secrets, so you can use the AWS CLI:

```bash
aws secretsmanager put-secret-value \
  --secret-id my-secret \
  --secret-string "actual-value"
```

Or use [infrahouse-toolkit](https://pypi.org/project/infrahouse-toolkit/) for convenience:

```bash
ih-secrets set my-secret
# You will be prompted to enter the secret value securely
```

Then run `terraform apply` to see the updated output.

### Terraform keeps changing the secret version

**Cause:** The `version_stages` attribute changes between applies.

**Solution:** This is normal behavior. The secret value is not changing, only the
version metadata.

## Deprecation Warnings

### "DEPRECATION WARNING: Using default value 'unknown' for service_name"

**Solution:** Explicitly set `service_name`:

```hcl
module "secret" {
  # ...
  service_name = "my-service"
}
```

## Getting Help

If you're still having issues:

1. Check the [GitHub Issues](https://github.com/infrahouse/terraform-aws-secret/issues)
2. [Contact Us](https://infrahouse.com/contact)