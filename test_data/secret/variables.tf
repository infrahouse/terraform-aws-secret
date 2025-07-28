variable "region" {}
variable "role_arn" {
  default = null
}

variable "admins" { default = [] }
variable "writers" { default = [] }
variable "readers" { default = [] }
variable "secret_name" {
  default = "foo"
}
variable "secret_name_prefix" { default = null }
variable "secret_value" {
  default = "bar"
}
variable "tags" { default = null }
