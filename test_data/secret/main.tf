module "test" {
  source             = "../../"
  secret_description = "Foo description"
  secret_name        = "foo"
  admins = [
    "arn:aws:iam::303467602807:role/aws-reserved/sso.amazonaws.com/us-west-1/AWSReservedSSO_AWSAdministratorAccess_422821c726d81c14",
    var.role_arn
  ]
  writers = [
    var.role_arn
  ]
  readers = [
    var.role_arn
  ]
  secret_value = "bar"
}
