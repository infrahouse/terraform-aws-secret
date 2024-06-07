module "test" {
  source             = "../../"
  secret_description = "Foo description"
  secret_name        = "foo"
  admins             = var.admins
  writers            = var.writers
  readers            = var.readers
  secret_value       = var.secret_value == "generate" ? random_password.value.result : var.secret_value
}

resource "random_password" "value" {
  length = 16
}
