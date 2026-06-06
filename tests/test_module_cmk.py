import json
import os
import time
from os import path as osp
from textwrap import dedent

import boto3
import pytest
from infrahouse_core.aws.secretsmanager import Secret
from infrahouse_core.timeout import timeout
from pytest_infrahouse import terraform_apply

from tests.conftest import LOG, TERRAFORM_ROOT_DIR
from tests.test_module import init_terraform_tf

CONSUMER_ROLE_ARN = os.environ.get(
    "CONSUMER_ROLE_ARN", "arn:aws:iam::493370826424:role/secret-consumer"
)


def _assume_role_session(boto3_session, role_arn, region):
    sts = boto3_session.client("sts", region_name=region)
    creds = sts.assume_role(
        RoleArn=role_arn,
        RoleSessionName=role_arn.split("/")[-1],
    )["Credentials"]
    return boto3.Session(
        aws_access_key_id=creds["AccessKeyId"],
        aws_secret_access_key=creds["SecretAccessKey"],
        aws_session_token=creds["SessionToken"],
    )


@pytest.mark.manual
def test_module_cmk(keep_after, test_role_arn, aws_region, boto3_session):
    terraform_module_dir = osp.join(TERRAFORM_ROOT_DIR, "secret_cmk")
    with open(osp.join(terraform_module_dir, "terraform.tfvars"), "w") as fp:
        fp.write(dedent(f"""
            region            = "{aws_region}"
            role_arn          = "{test_role_arn}"
            consumer_role_arn = "{CONSUMER_ROLE_ARN}"
        """))
    init_terraform_tf(terraform_module_dir)

    with terraform_apply(
        terraform_module_dir, destroy_after=not keep_after, json_output=True
    ) as tf_output:
        LOG.info("%s", json.dumps(tf_output, indent=4))
        assert tf_output["kms_key_id"]["value"]

        consumer_session = _assume_role_session(
            boto3_session, CONSUMER_ROLE_ARN, aws_region
        )
        secret = Secret(
            tf_output["secret_arn"]["value"],
            region=aws_region,
            session=consumer_session,
        )
        assert secret.value == "bar"
        secret.update("barbar")
        with timeout(5):
            while secret.value != "barbar":
                time.sleep(1)
        assert secret.value == "barbar"
