variable "admins" {
  description = "List of role ARNs that will have all permissions of the secret."
  default     = null
  type        = list(string)
}

variable "owner" {
  description = "A tag owner with this value will be placed on a secret."
  default     = null
  type        = string
}

variable "readers" {
  description = "List of role ARNs that will have read permissions of the secret."
  default     = null
  type        = list(string)
}

variable "writers" {
  description = "List of role ARNs that will have write permissions of the secret."
  default     = null
  type        = list(string)
}

variable "secret_name" {
  description = "Name of the secret in AWS Secretsmanager. Either secret_name or secret_name_prefix must be set."
  type        = string
  default     = null
}

variable "secret_name_prefix" {
  description = "Name prefix of the secret in AWS Secretsmanager. Either secret_name or secret_name_prefix must be set."
  type        = string
  default     = null
}

variable "secret_description" {
  description = "The secret description in AWS Secretsmanager."
  type        = string
}

variable "secret_value" {
  description = "Optional value of the secret."
  type        = string
  default     = null
  sensitive   = true
}

variable "environment" {
  description = "Name of environment."
  type        = string

  validation {
    condition     = can(regex("^[a-z0-9_]+$", var.environment))
    error_message = "environment must contain only lowercase letters, numbers, and underscores (no hyphens). Got: ${var.environment}"
  }
}

variable "service_name" {
  description = <<-EOT
    Descriptive name of a service that will use this secret.
    DEPRECATED: Default value "unknown" will be removed in v2.0. Please specify explicitly.
  EOT
  type        = string
  default     = "unknown"
}

variable "kms_key_id" {
  description = <<-EOT
    ARN or ID of a customer-managed KMS key to encrypt the secret.
    When null (default), the secret uses the AWS-managed key
    (aws/secretsmanager), unless create_cross_account_cmk is true, in which
    case the module creates a CMK for cross-account access.
    Set this explicitly to use your own CMK for compliance requirements
    or custom key policy control. Takes precedence over
    create_cross_account_cmk.
  EOT
  type        = string
  default     = null
}

variable "create_cross_account_cmk" {
  description = <<-EOT
    Whether to create a customer-managed KMS key for cross-account secret access.
    Defaults to false: the secret uses the AWS-managed key (aws/secretsmanager),
    matching pre-1.2.0 behavior. Set to true when readers/writers live in another
    AWS account and need to decrypt the secret, since the AWS-managed key cannot be
    shared cross-account.

    Note: this is an explicit flag rather than auto-detection because deciding it
    from role ARN account IDs requires those ARNs to be known at plan time. When an
    ARN is computed in the same apply (e.g. an instance role created alongside the
    secret), auto-detection produced an unknown value and broke `terraform apply`
    with "Invalid count argument" (#49).

    Ignored when kms_key_id is set.
  EOT
  type        = bool
  default     = false
}

variable "tags" {
  description = "Tags to apply to secret and other resources the module creates."
  type        = map(string)
  default     = {}
}
