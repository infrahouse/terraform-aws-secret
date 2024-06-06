provider "aws" {
  assume_role {
    role_arn = var.role_arn
  }
  region = var.region
  default_tags {
    tags = {
      "created_by" : "infrahouse/terraform-aws-secret" # GitHub repository that created a resource
    }

  }
}
