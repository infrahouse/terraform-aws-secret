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
}

variable "tags" {
  description = "Tags to apply to secret and other resources the module creates."
  type        = map(string)
  default     = {}
}
