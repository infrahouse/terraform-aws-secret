data "aws_caller_identity" "this" {}
data "aws_iam_roles" "sso-admin" {
  name_regex  = "AWSReservedSSO_AWSAdministratorAccess_.*"
  path_prefix = "/aws-reserved/sso.amazonaws.com/"
}
