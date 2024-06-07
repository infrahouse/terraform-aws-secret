
resource "aws_secretsmanager_secret" "secret" {
  description             = var.secret_description
  name                    = var.secret_name
  recovery_window_in_days = 0
  policy                  = data.aws_iam_policy_document.permission-policy.json
  tags = {
    owner : var.owner == null ? data.aws_iam_role.caller_role.arn : var.owner
  }
}

resource "aws_secretsmanager_secret_version" "current" {
  secret_id     = aws_secretsmanager_secret.secret.id
  secret_string = var.secret_value == null ? "NoValue" : var.secret_value
  version_stages = [
    var.secret_value == null ? "INITIAL" : "AWSCURRENT"
  ]
}
