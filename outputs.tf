output "secret_name" {
  description = "Name of the created secret"
  value       = aws_secretsmanager_secret.secret.name
}

output "secret_arn" {
  description = "ARN of the created secret"
  value       = aws_secretsmanager_secret.secret.arn
}

output "secret_id" {
  description = "ID of the created secret"
  value       = aws_secretsmanager_secret.secret.id
}

output "secret_value" {
  description = "The current secret value. If the value isn't set yet, return `null`."
  value       = length(data.aws_secretsmanager_secret_version.secret) > 0 ? data.aws_secretsmanager_secret_version.secret[0].secret_string : null
  sensitive   = true
}
