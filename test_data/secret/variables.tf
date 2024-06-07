variable "region" {}
variable "role_arn" {}

variable "admins" { default = null }
variable "writers" { default = null }
variable "readers" { default = null }
variable "secret_value" {
  default = "bar"
}
