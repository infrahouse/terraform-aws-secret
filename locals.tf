locals {
  module_version = "1.1.1"

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
}
