# Design Decisions

This document explains key architectural decisions made in the
terraform-aws-secret module.

## External Data Source for Secret Value Retrieval

### Decision

Use a Python script (`assets/get_secret.py`) with Terraform's `external`
data source to read the current secret value from AWS Secrets Manager.

### Context

The module supports two workflows:

1. **Known value**: User provides `secret_value` at deployment time
2. **Placeholder**: User omits `secret_value`, creates secret structure,
   and sets the real value later via AWS Console/CLI

For the placeholder workflow, we need the `secret_value` output to reflect
the *actual current value* in AWS, not what Terraform originally deployed.

### Problem

When `secret_value` is null, Terraform creates a version with
`secret_string = "NoValue"` and `version_stages = ["INITIAL"]`.
However, AWS automatically assigns `AWSCURRENT` to the first version
of any secret, so the version actually has both labels.

The challenge is distinguishing between:
- Placeholder state: secret contains "NoValue" (user hasn't set real value yet)
- Real value state: secret contains actual credential (user set it externally)

Native Terraform approaches don't work well:

**Attempt 1: Use `aws_secretsmanager_secret_version` data source**
```hcl
data "aws_secretsmanager_secret_version" "current" {
  secret_id = aws_secretsmanager_secret.secret.id
}
```
**Problem**: Returns "NoValue" which could be accidentally used as an actual
credential. No way to distinguish placeholder from real value in Terraform.

**Attempt 2: Check value in Terraform**
```hcl
output "secret_value" {
  value = (
    data.aws_secretsmanager_secret_version.current.secret_string == "NoValue"
    ? null
    : data.aws_secretsmanager_secret_version.current.secret_string
  )
}
```
**Problem**: The data source stores "NoValue" in Terraform state, which is
undesirable. Also adds complexity to the output.

### Solution

The Python script:
1. Calls AWS `GetSecretValue` API
2. Checks if the returned value is "NoValue" (placeholder)
3. Returns `null` for placeholder, actual value otherwise

This approach:
- Returns idiomatic `null` for "not set yet" state
- Prevents accidental use of "NoValue" as a real credential
- Keeps placeholder detection logic in one place

### Trade-offs

**Pros:**
- Enables the placeholder workflow (essential for external secrets)
- Output always reflects actual AWS state
- Graceful handling of "no value yet" case

**Cons:**
- Requires Python 3 and boto3 where Terraform runs
- Additional external dependency
- Slightly more complex than pure Terraform

### Alternatives Considered

1. **Remove `secret_value` output entirely**: Users would need to read
   secrets via AWS SDK at runtime. Rejected because it breaks module
   composition (passing secrets to other Terraform resources).

2. **Always use AWSCURRENT stage**: Would require users to provide a value,
   even if temporary. Rejected because it defeats the placeholder workflow
   purpose.

3. **Make the output optional via variable**: Could add
   `enable_secret_value_output` flag. Not implemented yet, but could be
   added if users need to run without Python/boto3.

### References

- [AWS Secrets Manager GetSecretValue API](https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html)
- [Terraform External Data Source](https://registry.terraform.io/providers/hashicorp/external/latest/docs/data-sources/external)
- [HashiCorp Discussion: Secret Version Behavior](https://discuss.hashicorp.com/t/confused-about-aws-secretsmanager-secret-version-resource-behaviour/52026)

---

## Secret Identifiers Not Marked as Sensitive

### Decision

The outputs `secret_name`, `secret_arn`, and `secret_id` are NOT marked
as `sensitive = true`.

### Rationale

These are identifiers, not secrets. Security is enforced via IAM policies,
not by obscuring resource names. Knowing the ARN of a secret does not grant
access to its value.

Marking identifiers as sensitive would:
- Hinder debugging (values hidden in plan output)
- Provide false sense of security (security by obscurity)
- Not prevent actual unauthorized access

Access control is the responsibility of IAM policies configured via
`admins`, `readers`, and `writers` variables.

---

## Zero Recovery Window

### Decision

The module uses `recovery_window_in_days = 0` (immediate deletion).

### Rationale

1. **Incident occurs either way**: When a secret is deleted, applications
   lose access immediately regardless of recovery window. The recovery
   window only affects whether you can *restore* the secret later.

2. **Terraform workflow**: Immediate deletion allows recreating a secret
   with the same name without waiting. This is important for destroy/recreate
   cycles.

3. **User request**: If users need recovery windows, they can request it
   as a configurable option. Following YAGNI (You Aren't Gonna Need It)
   principle.

### Future Consideration

Could add a `recovery_window_in_days` variable if users request it.
Default would remain 0 for backward compatibility.