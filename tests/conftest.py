from textwrap import dedent

import boto3
import pytest
import logging
from os import path as osp

from infrahouse_core.logging import setup_logging
from pytest_infrahouse import terraform_apply

MODULE_VERSION = "1.0.3"
# TEST_ROLE_ARN = "arn:aws:iam::303467602807:role/secret-tester"
DEFAULT_PROGRESS_INTERVAL = 10

LOG = logging.getLogger(__name__)
TERRAFORM_ROOT_DIR = "test_data"


setup_logging(LOG, debug=True)


def get_secretsmanager_client_by_role(role_name, test_role_arn, region):
    response = boto3.client("sts").assume_role(
        RoleArn=role_name, RoleSessionName=test_role_arn.split("/")[1]
    )
    # noinspection PyUnresolvedReferences
    return boto3.Session(
        aws_access_key_id=response["Credentials"]["AccessKeyId"],
        aws_secret_access_key=response["Credentials"]["SecretAccessKey"],
        aws_session_token=response["Credentials"]["SessionToken"],
    ).client("secretsmanager", region_name=region)


@pytest.fixture()
def probe_role(boto3_session, keep_after, test_role_arn, aws_region):
    terraform_module_dir = osp.join(TERRAFORM_ROOT_DIR, "probe_role")
    # Create service network
    with open(osp.join(terraform_module_dir, "terraform.tfvars"), "w") as fp:
        fp.write(
            dedent(
                f"""
                role_arn     = "{test_role_arn}"
                region       = "{aws_region}"
                trusted_arns = [
                    "arn:aws:iam::990466748045:user/aleks",
                    "{test_role_arn}"
                ]
                """
            )
        )
    with terraform_apply(
        terraform_module_dir,
        destroy_after=not keep_after,
        json_output=True,
    ) as tf_output:
        yield tf_output
