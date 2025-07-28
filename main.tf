
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
