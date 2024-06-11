variable "region" {}
variable "role_arn" {}

variable "admins" { default = null }
variable "writers" { default = null }
variable "readers" { default = null }
variable "secret_name" {
  default = "foo"
}
variable "secret_name_prefix" { default = null }
variable "secret_value" {
  default = "bar"
}
variable "tags" { default = null }
