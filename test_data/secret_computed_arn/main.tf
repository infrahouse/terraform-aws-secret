# Regression coverage for issue #49.
#
# The reader is the ARN of an IAM role created in this same apply, so its value is
# unknown at plan time. Before the fix, the module inspected the account ID inside
# this ARN to decide whether to create a cross-account CMK, which made
# module.cross_account_key's count unknown and failed with "Invalid count argument".
# With create_cross_account_cmk defaulting to false, no ARN inspection gates the
# count, so plan/apply must succeed.

data "aws_iam_policy_document" "assume_role" {
  statement {
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "reader" {
  name_prefix        = "secret-49-reader-"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
}

module "test" {
  source             = "../../"
  secret_description = "Computed-ARN reader regression (#49)"
  secret_name        = var.secret_name
  secret_value       = "bar"
  environment        = "development"
  service_name       = "secret-computed-arn-test"

  # Unknown at plan time — this is the value that used to break count.
  readers = [aws_iam_role.reader.arn]
}
