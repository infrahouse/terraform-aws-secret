resource "aws_iam_role" "probe" {
  assume_role_policy = data.aws_iam_policy_document.trust.json
}

resource "aws_iam_role_policy" "probe" {
  policy = data.aws_iam_policy_document.permissions.json
  role   = aws_iam_role.probe.id
}
