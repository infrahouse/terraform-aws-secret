data "aws_iam_policy_document" "permissions" {
  statement {
    actions = [
      "secretsmanager:*"
    ]
    resources = [
      "*"
    ]
  }
}

data "aws_iam_policy_document" "trust" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "AWS"
      identifiers = var.trusted_arns
    }
  }
}
