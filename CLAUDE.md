# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## First Steps

**Your first tool call in this repository MUST be reading .claude/CODING_STANDARD.md.
Do not read any other files, search, or take any actions until you have read it.**
This contains InfraHouse's comprehensive coding standards for Terraform, Python, and general formatting rules.

## Module Overview

`terraform-aws-secret` manages AWS Secrets Manager secrets with fine-grained IAM-based access control.
Users specify `admins`, `readers`, and `writers` role ARN lists; the module generates least-privilege
resource-based policies. It supports two workflows: providing `secret_value` at deploy time, or
omitting it to create a placeholder ("NoValue") that gets set externally via AWS Console/CLI.

### Key architectural detail

A Python script (`assets/get_secret.py`) is invoked as a Terraform `external` data source to read
the current secret value from AWS. This is required because native Terraform data sources cannot
distinguish the placeholder "NoValue" from a real value. The script returns empty string for the
placeholder, which the output converts to `null`. This means **Python 3 and boto3 must be available**
wherever Terraform runs.

## Commands

```bash
make bootstrap          # Install dependencies (pip) and git hooks
make test               # Run full test suite
make test-keep          # Run tests, keep AWS resources for debugging
make test-clean         # Run tests, destroy all resources after
make format             # terraform fmt -recursive && black tests
make lint               # Check formatting (black --check, terraform fmt -check)
make release-patch      # Bump patch version, update CHANGELOG, create tag
make release-minor      # Bump minor version
make release-major      # Bump major version
```

Run a single test or filter:
```bash
make test-keep TEST_PATH=tests/test_module.py TEST_FILTER="test_module_reads"
```

Default test region is `us-west-1`, override with `TEST_REGION=us-west-2`.

## Commit Messages

Commits must follow [Conventional Commits](https://www.conventionalcommits.org/) format.
A `hooks/commit-msg` hook enforces this. Valid types: `feat`, `fix`, `docs`, `style`,
`refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`, `security`.

Example: `feat: add recovery window variable`

## Version Management

Version is tracked in three places via `.bumpversion.cfg`:
- `locals.tf` (`module_version`)
- `README.md` (Quick Start example)
- `tests/conftest.py` (`MODULE_VERSION`)
- `docs/index.md`, `docs/getting-started.md`, `docs/examples.md`

Use `make release-*` targets — do not bump manually.

## Testing

Tests are **integration tests** that create real AWS infrastructure via `pytest-infrahouse`.
They assume an IAM role (`TEST_ROLE`) to provision resources.

Test root module lives in `test_data/secret/` — tests write `terraform.tfvars` and
`terraform.tf` dynamically per test case (to parametrize the AWS provider version).

Key fixtures come from `pytest-infrahouse`: `probe_role`, `keep_after`, `test_role_arn`,
`aws_region`, `boto3_session`, `secretsmanager_client`.

Tests cover: admin/reader/writer access policies, wildcard ARN matching, duplicate roles
across reader/writer lists, placeholder vs. known secret values, external value updates,
name prefix mode, and tag propagation.

## File Layout

| File | Purpose |
|------|---------|
| `main.tf` | Secret resource, secret version, name validation |
| `iam.tf` | Resource-based IAM policy (admin/reader/writer/deny statements) |
| `locals.tf` | Action lists, module version, default tags, readers-only set logic |
| `data_sources.tf` | Caller identity, region, caller role, external secret reader, Access Analyzer roles |
| `variables.tf` | All input variables |
| `outputs.tf` | secret_name, secret_arn, secret_id, secret_value |
| `terraform.tf` | Required providers and Terraform version |
| `assets/get_secret.py` | External data source script for reading secret values |

## IAM Policy Logic

The resource policy in `iam.tf` uses `ArnLike` conditions (supporting wildcards in role ARNs)
and builds four tiers:
1. **Admins** + caller role: full access (`*`)
2. **Writers**: read + write + list, explicit deny on admin/permission/tagging actions
3. **Readers-only** (readers minus writers): read only, explicit deny on everything else
4. **Catch-all deny**: denies all access to any principal not in the above lists

Access Analyzer service roles get a separate allow/deny pair scoped to `DescribeSecret`,
`GetResourcePolicy`, `ListSecrets`.

## Files Managed Externally

These files are managed by Terraform in the `github-control` repository — do not edit them directly:
- `.claude/CODING_STANDARD.md`
- `hooks/commit-msg`, `hooks/pre-commit`
- `.terraform-docs.yml`, `mkdocs.yml`, `cliff.toml`
