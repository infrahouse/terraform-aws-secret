# Data sources are defined here
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

data "aws_iam_role" "caller_role" {
  name = split("/", split(":", data.aws_caller_identity.current.arn)[5])[1]
}

# Retrieves the current secret value from AWS Secrets Manager.
# Returns null if secret_value input was null (placeholder "NoValue" in AWS).
# Returns the actual value after user sets it via AWS Console/CLI.
# This enables the "external update" workflow. See README for use cases.
data "external" "secret_value" {
  program = [
    "python", "${path.module}/assets/get_secret.py", data.aws_region.current.name,
    aws_secretsmanager_secret.secret.id, data.aws_iam_role.caller_role.arn
  ]
  depends_on = [
    aws_secretsmanager_secret_version.current
  ]
}

data "aws_iam_roles" "access-analyzer" {
  name_regex  = "AWSServiceRoleForAccessAnalyzer"
  path_prefix = "/aws-service-role/access-analyzer.amazonaws.com/"
}
