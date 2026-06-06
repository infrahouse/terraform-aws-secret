locals {
  module_version = "1.1.1"

  secret_identifier = coalesce(var.secret_name, var.secret_name_prefix)

  # Validation: exactly one of secret_name or secret_name_prefix must be set
  secret_name_check = (
    (var.secret_name != null && var.secret_name_prefix == null) ||
    (var.secret_name == null && var.secret_name_prefix != null)
  )

  access_analyzer_actions = [
    "secretsmanager:DescribeSecret",
    "secretsmanager:GetResourcePolicy",
    "secretsmanager:ListSecrets",
  ]
  list_actions = [
    "secretsmanager:BatchGetSecretValue",
    "secretsmanager:ListSecrets",
  ]
  admin_actions = [
    "secretsmanager:CreateSecret",
    "secretsmanager:DeleteSecret",
    "secretsmanager:StopReplicationToReplica",
    "secretsmanager:ReplicateSecretToRegions",
    "secretsmanager:RemoveRegionsFromReplication",
  ]
  read_actions = [
    "secretsmanager:DescribeSecret",
    "secretsmanager:GetSecretValue",
    "secretsmanager:GetRandomPassword",
    "secretsmanager:ListSecretVersionIds",
    "secretsmanager:GetResourcePolicy",
  ]
  write_actions = [
    "secretsmanager:PutSecretValue",
    "secretsmanager:CancelRotateSecret",
    "secretsmanager:UpdateSecret",
    "secretsmanager:RestoreSecret",
    "secretsmanager:RotateSecret",
    "secretsmanager:UpdateSecretVersionStage",
  ]
  permission_management_actions = [
    "secretsmanager:DeleteResourcePolicy",
    "secretsmanager:PutResourcePolicy",
    "secretsmanager:ValidateResourcePolicy",
  ]
  tagging_actions = [
    "secretsmanager:TagResource",
    "secretsmanager:UntagResource",
  ]
  all_actions = ["*"]

  default_module_tags = {
    environment : var.environment
    service : var.service_name
    account : data.aws_caller_identity.current.account_id
    created_by_module : "infrahouse/secret/aws"
  }

  readers_only = var.readers != null ? (
    var.writers != null ? setsubtract(
      toset(var.readers),
      toset(var.writers)
    ) : var.readers
  ) : null

  all_role_arns = concat(
    var.admins == null ? [] : var.admins,
    var.readers == null ? [] : var.readers,
    var.writers == null ? [] : var.writers,
  )

  cross_account_arns = [
    for arn in local.all_role_arns : arn
    if can(split(":", arn)[4]) &&
    split(":", arn)[4] != data.aws_caller_identity.current.account_id
  ]

  cross_account_writers = [
    for arn in concat(
      var.admins == null ? [] : var.admins,
      var.writers == null ? [] : var.writers,
    ) : arn
    if can(split(":", arn)[4]) &&
    split(":", arn)[4] != data.aws_caller_identity.current.account_id
  ]

  cross_account_readers_only = [
    for arn in(var.readers == null ? [] : var.readers) : arn
    if can(split(":", arn)[4]) &&
    split(":", arn)[4] != data.aws_caller_identity.current.account_id &&
    !contains(local.cross_account_writers, arn)
  ]

  create_cmk = length(local.cross_account_arns) > 0 && var.kms_key_id == null

  effective_kms_key_id = local.create_cmk ? module.cross_account_key[0].kms_key_arn : var.kms_key_id
}
