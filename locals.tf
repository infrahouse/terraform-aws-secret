locals {
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
  all_actions = concat(
    local.list_actions,
    local.admin_actions,
    local.read_actions,
    local.write_actions,
    local.permission_management_actions,
    local.tagging_actions
  )
}
