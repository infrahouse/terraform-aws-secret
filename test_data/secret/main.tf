module "test" {
  source             = "../../"
  secret_description = "Foo description"
  secret_name        = "foo"
  admins             = var.admins
  writers            = var.writers
  readers            = var.readers
  secret_value       = "bar"
}
