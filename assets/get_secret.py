import json
import sys

import boto3
from botocore.exceptions import ClientError


def get_secret(secretsmanager_client, secret_id):
    """
    Retrieve a value of a secret by its name.
    """
    try:
        response = secretsmanager_client.get_secret_value(
            SecretId=secret_id,
        )
        return response["SecretString"]
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            return None
        raise


def get_client(region, role_arn):
    sts = boto3.client("sts")
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
