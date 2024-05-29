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
  description = "Name of the secret in AWS Secretsmanager."
  type        = string
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
