module "test" {
  source             = "../../"
  secret_description = "Foo CMK description"
  secret_name        = var.secret_name
  writers            = [var.consumer_role_arn]
  secret_value       = var.secret_value
  environment        = "development"
  service_name       = "secret-cmk-test"
}
