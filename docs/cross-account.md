# Cross-Account Secret Access

This guide explains how to share a secret from one AWS account (the **owner**) with
a role in another AWS account (the **consumer**).

## Overview

![Cross-Account Architecture](images/cross-account.svg)

Cross-account secret access requires three things to be true simultaneously:

1. **Resource policy** on the secret allows the consumer role (handled by this module
   when you add the consumer role ARN to `writers` or `readers`).
2. **KMS key policy** on a customer-managed key (CMK) allows the consumer role to
   decrypt. The module creates this CMK when you set `create_cross_account_cmk = true`.
3. **Identity policy** on the consumer role in the consumer account grants
   `secretsmanager:GetSecretValue` and `kms:Decrypt` scoped to the owner account's
   resources.

## Accounts in This Guide

Throughout the examples below:

| Account                  | ID               | Role                              |
|--------------------------|------------------|-----------------------------------|
| **Owner** (Account A)    | `111111111111`   | Holds the secret and the CMK      |
| **Consumer** (Account B) | `222222222222`   | Accesses the secret cross-account |

## Owner Account Setup

The owner account (`111111111111`) creates the secret. Add the consumer role ARN to
`writers` (or `readers`) and set `create_cross_account_cmk = true` so the module
provisions a CMK with the right key policy:

```hcl
module "shared_secret" {
  source  = "registry.infrahouse.com/infrahouse/secret/aws"
  version = "1.3.0"

  secret_name        = "cross-account-config"
  secret_description = "Configuration shared with the consumer account"
  secret_value       = "super-secret-value"
  environment        = "production"
  service_name       = "shared-secret"

  writers                  = ["arn:aws:iam::222222222222:role/secret-consumer"]
  create_cross_account_cmk = true
}
```

That's it. With `create_cross_account_cmk = true`, the module:

- Creates a CMK with a key policy granting any consumer role in `writers`/`readers`
  (i.e. ARNs whose account differs from the owner account) `kms:Decrypt` and
  `kms:GenerateDataKey*`
- Encrypts the secret with that CMK
- Generates a resource policy granting the consumer role read/write access

> **Why isn't this auto-detected?** Earlier versions inferred cross-account access by
> reading the account ID out of each role ARN. That breaks when an ARN is computed in
> the same apply (e.g. an instance role created alongside the secret): the value is
> unknown at plan time, so Terraform can't decide whether to create the key and fails
> with `Invalid count argument`. The explicit flag avoids that entirely. See
> [issue #49](https://github.com/infrahouse/terraform-aws-secret/issues/49).

The CMK ARN is available via `module.shared_secret.kms_key_id` — the consumer
account needs it for scoping its identity policy.

!!! warning "The consumer role must exist before you apply the owner side"
    When `create_cross_account_cmk = true`, the module writes the consumer role
    ARNs into the **CMK key policy**. AWS KMS validates every principal named in a
    key policy and rejects ARNs that don't yet exist, so the owner-side apply fails
    with:

    ```
    MalformedPolicyDocumentException: Policy contains a statement with
    one or more invalid principals.
    ```

    This is a KMS-specific rule — see
    [PutKeyPolicy](https://docs.aws.amazon.com/kms/latest/APIReference/API_PutKeyPolicy.html).
    The secret's **resource policy** is *not* affected: it matches the consumer with
    an `ArnLike` condition on `aws:PrincipalArn`, which is evaluated per request and
    never requires the role to exist at apply time.

    The practical consequence is an ordering dependency between the two accounts:

    1. The **consumer** account creates the IAM role first and hands over its ARN.
    2. The **owner** account adds that ARN to `writers`/`readers`, sets
       `create_cross_account_cmk = true`, and applies.

    If the consumer role is later deleted, subsequent owner-side applies keep failing
    the same way until the role is recreated or removed from `writers`/`readers`.

!!! note "Grant specific roles, never `:root`"
    Add the individual consumer role ARNs to `writers`/`readers` rather than the
    account root (`arn:aws:iam::222222222222:root`). The module scopes both the
    resource policy and the CMK key policy to exactly those ARNs, following least
    privilege — this protects the consumer account from a misconfiguration where an
    unexpected identity in that account gains access to the secret. Granting `:root`
    would also sidestep the existence check above, but at the cost of exposing the
    secret to every principal in the consumer account.

!!! note "Bring your own CMK"
    If you need custom key policy settings, create a CMK separately and pass
    it via `kms_key_id`. The module skips auto-creation when `kms_key_id`
    is provided.

## Consumer Account Setup

The consumer account (`222222222222`) creates an IAM role with a trust policy
and an identity policy.

### Trust Policy

The trust policy controls who can assume the consumer role.

!!! warning "Replace the principal below with your own trusted role"
    The example trusts `secret-tester` from the owner account. Your trust
    policy must reference the principal that actually needs to assume this
    role — an EC2 instance role, a Lambda execution role, an SSO role, etc.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::111111111111:role/secret-tester"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

### Identity Policy

The identity policy needs two statements: one for Secrets Manager, one for KMS.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "SecretRW",
      "Effect": "Allow",
      "Action": [
        "secretsmanager:PutSecretValue",
        "secretsmanager:GetSecretValue",
        "secretsmanager:DescribeSecret"
      ],
      "Resource": "arn:aws:secretsmanager:us-west-1:111111111111:secret:*"
    },
    {
      "Sid": "UseCmkViaSecretsManager",
      "Effect": "Allow",
      "Action": [
        "kms:GenerateDataKey",
        "kms:Encrypt",
        "kms:DescribeKey",
        "kms:Decrypt"
      ],
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "kms:ViaService": "secretsmanager.us-west-1.amazonaws.com"
        }
      }
    }
  ]
}
```

!!! note "Scope resources tightly"
    The example uses `secret:*` for brevity. In production, scope the
    Secrets Manager resource to the specific secret ARN if known at plan
    time.

!!! note "kms:ViaService condition"
    The `kms:ViaService` condition ensures the KMS key can only be used
    through Secrets Manager, not for arbitrary encrypt/decrypt operations.

## Access Pattern

Once both sides are deployed, the consumer role can access the secret:

=== "Python (infrahouse-core)"

    ```python
    from infrahouse_core.aws.secretsmanager import Secret

    secret = Secret(
        "arn:aws:secretsmanager:us-west-1:111111111111:secret:cross-account-config-AbCdEf",
        region="us-west-1",
        role_arn="arn:aws:iam::222222222222:role/secret-consumer",
    )

    # Read
    value = secret.value

    # Write
    secret.update("new-value")
    ```

=== "AWS CLI"

    ```bash
    # Assume the consumer role first
    eval $(aws sts assume-role \
      --role-arn arn:aws:iam::222222222222:role/secret-consumer \
      --role-session-name cross-account \
      --query 'Credentials.[AccessKeyId,SecretAccessKey,SessionToken]' \
      --output text \
      | awk '{printf "export AWS_ACCESS_KEY_ID=%s AWS_SECRET_ACCESS_KEY=%s AWS_SESSION_TOKEN=%s", $1, $2, $3}')

    # Read the secret by ARN (short names resolve against the caller's account)
    aws secretsmanager get-secret-value \
      --secret-id arn:aws:secretsmanager:us-west-1:111111111111:secret:cross-account-config-AbCdEf \
      --query SecretString --output text
    ```

!!! warning "Use the full ARN, not the short name"
    Cross-account callers **must** reference the secret by its full ARN.
    A short name like `cross-account-config` resolves against the caller's
    own account, not the owner account.

## Troubleshooting

### AccessDeniedException: no identity-based policy allows the action

The consumer role's identity policy is missing or doesn't cover the action.
Verify the policy is attached and the resource ARN matches:

```bash
aws iam get-role-policy \
  --role-name secret-consumer \
  --policy-name cross-account-secret-access
```

### AccessDeniedException: explicit deny in a resource-based policy

The consumer role ARN is not in the secret's `writers` or `readers` list.
Check the resource policy on the secret:

```bash
aws secretsmanager get-resource-policy --secret-id <secret-arn>
```

### MalformedPolicyDocumentException: invalid principals (owner-side apply)

The owner-side apply fails while creating or updating the CMK because a consumer
role ARN in `writers`/`readers` does not exist. KMS refuses to save a key policy
that names a non-existent principal. Make sure every consumer role exists before
you apply, then re-run. The secret's resource policy is unaffected because it
matches `aws:PrincipalArn` with `ArnLike` rather than naming the principal
directly. See [The consumer role must exist before you apply](#owner-account-setup).

### KMS AccessDeniedException

The CMK key policy doesn't include the consumer role. Check the key policy on the
module-created CMK:

```bash
aws kms get-key-policy --key-id <key-arn> --policy-name default
```

### Stale reads after PutSecretValue

Cross-account reads may show the old value for a few seconds after a write
due to eventual consistency. Retry with a short delay if your workflow
requires read-after-write consistency.

## Complete Example

See [`test_data/secret_cmk/`](https://github.com/infrahouse/terraform-aws-secret/tree/main/test_data/secret_cmk)
for a working owner-side example with cross-account writer access.
