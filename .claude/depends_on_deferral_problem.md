# `data.external.secret_value` is unknown at plan time

## Problem

`secret_value` output is always unknown at Terraform plan time.
Any consumer that uses it in a `count` or `for_each` expression
gets "Invalid count argument".

## Root cause

`data_sources.tf:9-16`:

```hcl
data "external" "secret_value" {
  program = [
    "python", "${path.module}/assets/get_secret.py",
    data.aws_region.current.name,
    aws_secretsmanager_secret.secret.id,
    data.aws_iam_role.caller_role.arn
  ]
  depends_on = [
    aws_secretsmanager_secret_version.current
  ]
}
```

Terraform defers reading data sources that have `depends_on` on
managed resources -- it reads them during apply, not during plan.
The secret can already exist in AWS and the resource can have no
planned changes; Terraform still defers the read.

This makes `data.external.secret_value.result["SECRET_VALUE"]`
unknown at plan time, which propagates through the `secret_value`
output to every caller.

## Reproduction

In `terraform-aws-org-governance`, the caller does:

```hcl
# aws-control-root/iso27001-org-governance.tf
module "org-governance" {
  ...
  vanta_external_id = module.vanta-external-id.secret_value
}
```

And `vanta.tf` gates resources with:

```hcl
locals {
  vanta_enabled = var.vanta_external_id != null
}

resource "..." {
  count = local.vanta_enabled ? 1 : 0
}
```

`terraform plan` fails with "Invalid count argument" because
`var.vanta_external_id != null` evaluates to unknown.

## Possible fix

Remove the `depends_on` from the data source, or replace
`data "external"` with `data "aws_secretsmanager_secret_version"`
which can be read at plan time without deferral. The `depends_on`
exists to ensure the secret version resource is created before
reading -- a direct data source could use the resource's `secret_id`
attribute as an implicit dependency instead.

Evaluate impact on all consumers before changing.
