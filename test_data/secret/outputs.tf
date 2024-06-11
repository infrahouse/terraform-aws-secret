output "secret_value" {
  value     = module.test.secret_value
  sensitive = true
}

output "secret_arn" {
  value = module.test.secret_arn
}

output "secret_name" {
  value = module.test.secret_name
}
