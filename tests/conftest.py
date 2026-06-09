from textwrap import dedent

import boto3
import pytest
import logging
from os import path as osp

from infrahouse_core.logging import setup_logging
from pytest_infrahouse import terraform_apply

MODULE_VERSION = "1.3.0"
DEFAULT_PROGRESS_INTERVAL = 10

LOG = logging.getLogger()
TERRAFORM_ROOT_DIR = "test_data"


setup_logging(LOG, debug_botocore=False)


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "manual: cross-account test, run by hand only (excluded from CI)",
    )


def get_secretsmanager_client_by_role(role_name, boto3_session, region):
    sts_client = boto3_session.client("sts", region_name=region)
    response = sts_client.assume_role(
        RoleArn=role_name, RoleSessionName=role_name.split("/")[1]
    )
    # noinspection PyUnresolvedReferences
    return boto3.Session(
        aws_access_key_id=response["Credentials"]["AccessKeyId"],
        aws_secret_access_key=response["Credentials"]["SecretAccessKey"],
        aws_session_token=response["Credentials"]["SessionToken"],
    ).client("secretsmanager", region_name=region)
