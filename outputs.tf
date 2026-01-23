# Security Design Decision:
# secret_name, secret_arn, and secret_id are NOT marked as sensitive.
# These are identifiers, not secrets. Access control is enforced via IAM policies,
# not by obscuring resource names. Hiding identifiers would hinder debugging
# without providing real security benefit (security by obscurity).

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
  # External data source converts null to empty string, so we convert back to null
  value     = data.external.secret_value.result["SECRET_VALUE"] == "" ? null : data.external.secret_value.result["SECRET_VALUE"]
  sensitive = true
}
