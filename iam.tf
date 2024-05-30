data "aws_iam_policy_document" "permission-policy" {
  statement {
    principals {
      identifiers = concat(var.admins == null ? [] : var.admins, [data.aws_iam_role.caller_role.arn])
      type        = "AWS"
    }
    actions = [
      "secretsmanager:*"
    ]
    resources = [
      "*"
    ]
  }


  dynamic "statement" {
    for_each = var.writers != null ? [{}] : []
    content {
      principals {
        identifiers = var.writers
        type        = "AWS"
      }
      actions = [
        "secretsmanager:PutSecretValue",
        "secretsmanager:RotateSecret",
        "secretsmanager:CancelRotateSecret",

      ]
      resources = [
        "*"
      ]
    }
  }

  dynamic "statement" {
    for_each = var.readers != null ? [{}] : []
    content {
      principals {
        identifiers = var.readers
        type        = "AWS"
      }
      actions = [
        "secretsmanager:GetSecretValue",
      ]
      resources = [
        "*"
      ]
    }
  }

  statement {
    effect = "Deny"
    principals {
      type        = "AWS"
      identifiers = ["*"]
    }
    actions = [
      "secretsmanager:*"
    ]
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
