check "service_name_deprecation" {
  assert {
    condition     = var.service_name != "unknown"
    error_message = "DEPRECATION WARNING: Using default value 'unknown' for service_name is deprecated and will be removed in v2.0. Please specify service_name explicitly."
  }
}

resource "null_resource" "validate_secret_name" {
  lifecycle {
    precondition {
      condition     = local.secret_name_check
      error_message = "Exactly one of secret_name or secret_name_prefix must be set (not both, not neither)"
    }
  }
}

resource "aws_secretsmanager_secret" "secret" {
  description             = var.secret_description
  name                    = var.secret_name
  name_prefix             = var.secret_name_prefix
  recovery_window_in_days = 0
  policy                  = data.aws_iam_policy_document.permission-policy.json
  tags = merge(
    {
      owner : var.owner == null ? data.aws_iam_role.caller_role.arn : var.owner
      module_version : local.module_version
    },
    var.tags,
    local.default_module_tags,
  )
}

resource "aws_secretsmanager_secret_version" "current" {
  secret_id     = aws_secretsmanager_secret.secret.id
  secret_string = var.secret_value == null ? "NoValue" : var.secret_value
  version_stages = [
    var.secret_value == null ? "INITIAL" : "AWSCURRENT"
  ]
}
