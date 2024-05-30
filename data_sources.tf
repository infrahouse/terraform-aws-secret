# Data sources are defined here
data "aws_caller_identity" "current" {}

data "aws_iam_role" "caller_role" {

  name = split("/", split(":", data.aws_caller_identity.current.arn)[5])[1]
}

data "aws_secretsmanager_secret_version" "secret" {
  count     = var.secret_value == null ? 0 : 1
  secret_id = aws_secretsmanager_secret.secret.id
  depends_on = [
    aws_secretsmanager_secret_version.current
  ]
}
