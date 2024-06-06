from textwrap import dedent

import boto3
import pytest
import logging
from os import path as osp

from infrahouse_toolkit.logging import setup_logging
from infrahouse_toolkit.terraform import terraform_apply

# "303467602807" is our test account
TEST_ACCOUNT = "303467602807"
TEST_ROLE_ARN = "arn:aws:iam::303467602807:role/secret-tester"
DEFAULT_PROGRESS_INTERVAL = 10
TRACE_TERRAFORM = False
DESTROY_AFTER = True
UBUNTU_CODENAME = "jammy"

LOG = logging.getLogger(__name__)
REGION = "us-east-2"
TEST_ZONE = "ci-cd.infrahouse.com"
TERRAFORM_ROOT_DIR = "test_data"


setup_logging(LOG, debug=True)


@pytest.fixture(scope="session")
def aws_iam_role():
    sts = boto3.client("sts")
    return sts.assume_role(
        RoleArn=TEST_ROLE_ARN, RoleSessionName=TEST_ROLE_ARN.split("/")[1]
    )


@pytest.fixture(scope="session")
def boto3_session(aws_iam_role):
    return boto3.Session(
        aws_access_key_id=aws_iam_role["Credentials"]["AccessKeyId"],
        aws_secret_access_key=aws_iam_role["Credentials"]["SecretAccessKey"],
        aws_session_token=aws_iam_role["Credentials"]["SessionToken"],
    )


@pytest.fixture(scope="session")
def ec2_client(boto3_session):
    assert boto3_session.client("sts").get_caller_identity()["Account"] == TEST_ACCOUNT
    return boto3_session.client("ec2", region_name=REGION)


@pytest.fixture(scope="session")
def ec2_client_map(ec2_client, boto3_session):
    regions = [reg["RegionName"] for reg in ec2_client.describe_regions()["Regions"]]
    ec2_map = {reg: boto3_session.client("ec2", region_name=reg) for reg in regions}

    return ec2_map


@pytest.fixture()
def route53_client(boto3_session):
    return boto3_session.client("route53", region_name=REGION)


@pytest.fixture()
def elbv2_client(boto3_session):
    return boto3_session.client("elbv2", region_name=REGION)


@pytest.fixture()
def autoscaling_client(boto3_session):
    assert boto3_session.client("sts").get_caller_identity()["Account"] == TEST_ACCOUNT
    return boto3_session.client("autoscaling", region_name=REGION)


@pytest.fixture()
def secretsmanager_client(boto3_session):
    assert boto3_session.client("sts").get_caller_identity()["Account"] == TEST_ACCOUNT
    return boto3_session.client("secretsmanager", region_name=REGION)


def get_secretsmanager_client_by_role(role_name):
    response = boto3.client("sts").assume_role(
        RoleArn=role_name, RoleSessionName=TEST_ROLE_ARN.split("/")[1]
    )
    # noinspection PyUnresolvedReferences
    return boto3.Session(
        aws_access_key_id=response["Credentials"]["AccessKeyId"],
        aws_secret_access_key=response["Credentials"]["SecretAccessKey"],
        aws_session_token=response["Credentials"]["SessionToken"],
    ).client("secretsmanager", region_name=REGION)


@pytest.fixture()
def service_network(boto3_session):
    terraform_module_dir = osp.join(TERRAFORM_ROOT_DIR, "service-network")
    # Create service network
    with open(osp.join(terraform_module_dir, "terraform.tfvars"), "w") as fp:
        fp.write(
            dedent(
                f"""
                role_arn = "{TEST_ROLE_ARN}"
                region = "{REGION}"
                """
            )
        )
    with terraform_apply(
        terraform_module_dir,
        destroy_after=DESTROY_AFTER,
        json_output=True,
        enable_trace=TRACE_TERRAFORM,
    ) as tf_service_network_output:
        yield tf_service_network_output


@pytest.fixture()
def ses(boto3_session):
    terraform_module_dir = osp.join(TERRAFORM_ROOT_DIR, "ses")
    # Create service network
    with open(osp.join(terraform_module_dir, "terraform.tfvars"), "w") as fp:
        fp.write(
            dedent(
                f"""
                role_arn = "{TEST_ROLE_ARN}"
                test_zone = "{TEST_ZONE}"
                region = "{REGION}"
                """
            )
        )
    with terraform_apply(
        terraform_module_dir,
        destroy_after=DESTROY_AFTER,
        json_output=True,
        enable_trace=TRACE_TERRAFORM,
    ) as tf_output:
        yield tf_output


@pytest.fixture()
def probe_role(boto3_session):
    terraform_module_dir = osp.join(TERRAFORM_ROOT_DIR, "probe_role")
    # Create service network
    with open(osp.join(terraform_module_dir, "terraform.tfvars"), "w") as fp:
        fp.write(
            dedent(
                f"""
                role_arn     = "{TEST_ROLE_ARN}"
                region       = "{REGION}"
                trusted_arns = ["arn:aws:iam::990466748045:user/aleks"]
                """
            )
        )
    with terraform_apply(
        terraform_module_dir,
        destroy_after=DESTROY_AFTER,
        json_output=True,
        enable_trace=TRACE_TERRAFORM,
    ) as tf_output:
        yield tf_output
