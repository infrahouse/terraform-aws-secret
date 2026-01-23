output "secret_arn" {
  description = "ARN of the created secret"
  value       = module.api_secret.secret_arn
}

output "secret_name" {
  description = "Name of the created secret"
  value       = module.api_secret.secret_name
}