# Data sources are defined here
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

data "aws_iam_role" "caller_role" {
  name = split("/", split(":", data.aws_caller_identity.current.arn)[5])[1]
}

data "external" "secret_value" {
  program = [
    "python", "${path.module}/assets/get_secret.py", data.aws_region.current.name, aws_secretsmanager_secret.secret.id, data.aws_iam_role.caller_role.arn
  ]
  depends_on = [
    aws_secretsmanager_secret_version.current
  ]
}
