data "aws_iam_policy_document" "permission-policy" {
  statement {
    principals {
      identifiers = concat(var.admins == null ? [] : var.admins, [data.aws_iam_role.caller_role.arn])
      type        = "AWS"
    }
    actions = local.all_actions
    resources = [
      "*"
    ]
  }

  ## Writers
  dynamic "statement" {
    for_each = var.writers != null ? [{}] : []
    content {
      principals {
        identifiers = var.writers
        type        = "AWS"
      }
      actions = concat(
        local.list_actions,
        local.read_actions,
        local.write_actions
      )
      resources = [
        "*"
      ]
    }
  }

  dynamic "statement" {
    for_each = var.writers != null ? [{}] : []
    content {
      effect = "Deny"
      principals {
        identifiers = var.writers
        type        = "AWS"
      }
      actions = concat(
        local.admin_actions,
        local.permission_management_actions,
        local.tagging_actions
      )
      resources = [
        "*"
      ]
    }
  }

  ## Readers
  dynamic "statement" {
    for_each = var.readers != null ? [{}] : []
    content {
      principals {
        identifiers = var.readers
        type        = "AWS"
      }
      actions = local.read_actions
      resources = [
        "*"
      ]
    }
  }

  dynamic "statement" {
    for_each = var.readers != null ? [{}] : []
    content {
      effect = "Deny"
      principals {
        identifiers = var.readers
        type        = "AWS"
      }
      actions = concat(
        local.list_actions,
        local.admin_actions,
        local.write_actions,
        local.permission_management_actions,
        local.tagging_actions
      )
      resources = [
        "*"
      ]
    }
  }

  ## The rest
  statement {
    effect = "Deny"
    principals {
      type        = "AWS"
      identifiers = ["*"]
    }
    actions = local.all_actions
    resources = [
      "*"
    ]
    condition {
      test = "StringNotLike"
      values = concat(
        [data.aws_iam_role.caller_role.arn],
        var.admins == null ? [] : var.admins,
        var.writers == null ? [] : var.writers,
        var.readers == null ? [] : var.readers
      )
      variable = "aws:PrincipalArn"
    }
  }
}
