output "secret_value" {
  value     = module.test.secret_value
  sensitive = true
}
