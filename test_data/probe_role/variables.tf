variable "region" {}
variable "role_arn" {}

variable "trusted_arns" {
  description = "List of ARNs allowed to assume the probe role"
  type        = list(string)
}
