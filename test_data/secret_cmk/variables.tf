variable "region" {}
variable "role_arn" {
  default = null
}
variable "consumer_role_arn" {}
variable "secret_name" {
  default = "foo"
}
variable "secret_value" {
  default = "bar"
}
