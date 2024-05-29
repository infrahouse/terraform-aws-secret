output "secret_name" {
  description = "Name of the created secret"
  value       = aws_secretsmanager_secret.secret.name
}

output "secret_arn" {
  description = "ARN of the created secret"
  value       = aws_secretsmanager_secret.secret.arn
}
