# Data sources are defined here
data "aws_caller_identity" "current" {}

data "aws_iam_role" "caller_role" {

  name = split("/", split(":", data.aws_caller_identity.current.arn)[5])[1]
}
