module "cross_account_key" {
  count   = local.create_cmk ? 1 : 0
  source  = "registry.infrahouse.com/infrahouse/key/aws"
  version = "0.3.0"

  environment     = var.environment
  service_name    = var.service_name
  key_name        = "secret/${local.secret_identifier}"
  key_description = "CMK for cross-account access to secret ${local.secret_identifier}"

  key_users = concat(
    [data.aws_iam_role.caller_role.arn],
    var.admins == null ? [] : var.admins,
    local.cross_account_writers,
  )
  key_decrypt_only_users = local.cross_account_readers_only

  tags = var.tags
}
