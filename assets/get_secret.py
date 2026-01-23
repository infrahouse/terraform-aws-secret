import json
import sys

import boto3
from botocore.exceptions import ClientError


def get_secret(secretsmanager_client, secret_id):
    """
    Retrieve a value of a secret by its name.

    Returns empty string if the secret doesn't exist or contains the placeholder
    value "NoValue" (indicating secret_value input was null and no external value
    has been set yet). Terraform output converts empty string to null.

    Note: Terraform external data source requires all values to be strings,
    so we cannot return None/null directly.
    """
    try:
        response = secretsmanager_client.get_secret_value(
            SecretId=secret_id,
        )
        value = response["SecretString"]
        # Return empty string for placeholder - Terraform output converts to null
        if value == "NoValue":
            return ""
        return value
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            return ""
        raise


def get_client(region, role_arn):
    sts = boto3.client("sts")

    # Get current caller identity to check if we're already using the target role
    caller_identity = sts.get_caller_identity()
    current_arn = caller_identity["Arn"]

    # Extract role name from the target role ARN
    # Format: arn:aws:iam::{account}:role/{path}/{role-name}
    # Role name is the last part after the final /
    target_role_name = role_arn.split("/")[-1]

    # Check if we're already using the target role
    # For assumed roles, the ARN format is:
    # arn:aws:sts::{account}:assumed-role/{role-name}/{session-name}
    # This handles:
    # - AWS SSO users (assumed-role ARN contains the role name)
    # - Regular IAM roles already in use
    # - Any scenario where re-assuming the same role is unnecessary
    if f"assumed-role/{target_role_name}/" in current_arn:
        # Already using the target role, use current session
        session = boto3.Session(region_name=region)
        return session.client("secretsmanager")

    # Different role - need to assume it (existing behavior)
    iam_role = sts.assume_role(
        RoleArn=role_arn, RoleSessionName="terraform-aws-secret-data-source"
    )
    session = boto3.Session(
        region_name=region,
        aws_access_key_id=iam_role["Credentials"]["AccessKeyId"],
        aws_secret_access_key=iam_role["Credentials"]["SecretAccessKey"],
        aws_session_token=iam_role["Credentials"]["SessionToken"],
    )
    return session.client("secretsmanager")


if __name__ == "__main__":

    print(
        json.dumps(
            {
                "SECRET_VALUE": get_secret(
                    get_client(region=sys.argv[1], role_arn=sys.argv[3]),
                    secret_id=sys.argv[2],
                )
            }
        )
    )
