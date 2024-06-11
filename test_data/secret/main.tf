module "test" {
  source             = "../../"
  secret_description = "Foo description"
  secret_name        = var.secret_name
  secret_name_prefix = var.secret_name_prefix
  admins             = var.admins
  writers            = var.writers
  readers            = var.readers
  secret_value       = var.secret_value == "generate" ? random_password.value.result : var.secret_value
  tags               = var.tags
}

resource "random_password" "value" {
  length = 16
}
