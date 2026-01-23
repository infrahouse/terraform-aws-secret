# Basic example of terraform-aws-secret
#
# This example creates a simple secret with read access for an application role.

module "api_secret" {
  source = "../../"

  secret_name        = "example-api-key"
  secret_description = "Example API key for demonstration"
  secret_value       = "example-secret-value"
  environment        = "development"
  service_name       = "example-app"

  readers = [
    var.reader_role_arn,
  ]
}