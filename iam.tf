data "aws_iam_policy_document" "permission-policy" {
  statement {
    principals {
      identifiers = ["*"]
      type        = "AWS"
    }
    condition {
      test     = "ArnLike"
      values   = concat(var.admins == null ? [] : var.admins, [data.aws_iam_role.caller_role.arn])
      variable = "aws:PrincipalArn"
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
        identifiers = ["*"]
        type        = "AWS"
      }
      condition {
        test     = "ArnLike"
        values   = var.writers
        variable = "aws:PrincipalArn"
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
        identifiers = ["*"]
        type        = "AWS"
      }
      condition {
        test     = "ArnLike"
        values   = var.writers
        variable = "aws:PrincipalArn"
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
        identifiers = ["*"]
        type        = "AWS"
      }
      condition {
        test     = "ArnLike"
        values   = local.readers_only
        variable = "aws:PrincipalArn"
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
        identifiers = ["*"]
        type        = "AWS"
      }
      condition {
        test     = "ArnLike"
        values   = local.readers_only
        variable = "aws:PrincipalArn"
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

  # Access Analyzer permissions
  statement {
    effect = "Allow"
    principals {
      type = "AWS"
      identifiers = [
        data.aws_iam_role.accessanalyzer.arn
      ]
    }
    actions   = local.access_analyzer_actions
    resources = ["*"]
  }

  statement {
    effect = "Deny"
    principals {
      type = "AWS"
      identifiers = [
        data.aws_iam_role.accessanalyzer.arn
      ]
    }
    actions = setsubtract(
      concat(
        local.list_actions,
        local.read_actions,
        local.write_actions,
        local.admin_actions,
        local.permission_management_actions,
        local.tagging_actions,
      ),
      local.access_analyzer_actions
    )
    resources = ["*"]
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
      test = "ArnNotLike"
      values = concat(
        [
          data.aws_iam_role.caller_role.arn,
          data.aws_iam_role.accessanalyzer.arn
        ],
        var.admins == null ? [] : var.admins,
        var.writers == null ? [] : var.writers,
        var.readers == null ? [] : var.readers
      )
      variable = "aws:PrincipalArn"
    }
  }
}
