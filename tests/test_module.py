import json
from os import path as osp
from textwrap import dedent

import pytest
from botocore.exceptions import ClientError
from infrahouse_toolkit.terraform import terraform_apply

from tests.conftest import (
    LOG,
    TRACE_TERRAFORM,
    DESTROY_AFTER,
    TEST_ZONE,
    TEST_ROLE_ARN,
    REGION,
    TERRAFORM_ROOT_DIR,
    get_secretsmanager_client_by_role,
)


def test_module(probe_role):
    terraform_module_dir = osp.join(TERRAFORM_ROOT_DIR, "secret")
    with open(osp.join(terraform_module_dir, "terraform.tfvars"), "w") as fp:
        fp.write(
            dedent(
                f"""
                region = "{REGION}"
                role_arn = "{TEST_ROLE_ARN}"

                admins = [
                    "arn:aws:iam::303467602807:role/aws-reserved/sso.amazonaws.com/us-west-1/AWSReservedSSO_AWSAdministratorAccess_422821c726d81c14",
                    "{probe_role["role_arn"]["value"]}"
                ]
                """
            )
        )

    with terraform_apply(
        terraform_module_dir,
        destroy_after=DESTROY_AFTER,
        json_output=True,
        enable_trace=TRACE_TERRAFORM,
    ) as tf_output:
        LOG.info("%s", json.dumps(tf_output, indent=4))


def test_module_no_access(probe_role, secretsmanager_client):
    terraform_module_dir = osp.join(TERRAFORM_ROOT_DIR, "secret")
    probe_role_arn = probe_role["role_arn"]["value"]
    with open(osp.join(terraform_module_dir, "terraform.tfvars"), "w") as fp:
        fp.write(
            dedent(
                f"""
                region = "{REGION}"
                role_arn = "{TEST_ROLE_ARN}"

                admins = [
                    "arn:aws:iam::303467602807:role/aws-reserved/sso.amazonaws.com/us-west-1/AWSReservedSSO_AWSAdministratorAccess_422821c726d81c14",
                    "{TEST_ROLE_ARN}"
                ]
                """
            )
        )

    with terraform_apply(
        terraform_module_dir,
        destroy_after=DESTROY_AFTER,
        json_output=True,
        enable_trace=TRACE_TERRAFORM,
    ) as tf_output:
        LOG.info("%s", json.dumps(tf_output, indent=4))
        sm_client = get_secretsmanager_client_by_role(probe_role["role_arn"]["value"])
        with pytest.raises(ClientError) as err:
            sm_client.get_secret_value(
                SecretId="foo",
            )
        assert err.type is ClientError
        # Example
        # e = {
        #     "Message": (
        #         "User: "
        #         "arn:aws:sts::303467602807:assumed-role/terraform-20240606193517506500000001/secret-tester "
        #         "is not authorized to perform: secretsmanager:GetSecretValue on resource: foo with "
        #         "an explicit deny in a resource-based policy"
        #     ),
        #     "Code": "AccessDeniedException",
        # }
        assert err.value.response["Error"]["Code"] == "AccessDeniedException"


def test_module_reads(probe_role, secretsmanager_client):
    terraform_module_dir = osp.join(TERRAFORM_ROOT_DIR, "secret")
    probe_role_arn = probe_role["role_arn"]["value"]
    with open(osp.join(terraform_module_dir, "terraform.tfvars"), "w") as fp:
        fp.write(
            dedent(
                f"""
                region = "{REGION}"
                role_arn = "{TEST_ROLE_ARN}"

                admins = [
                    "arn:aws:iam::303467602807:role/aws-reserved/sso.amazonaws.com/us-west-1/AWSReservedSSO_AWSAdministratorAccess_422821c726d81c14",
                    "{TEST_ROLE_ARN}"
                ]
                readers = [
                    "{probe_role_arn}"
                ]
                """
            )
        )

    with terraform_apply(
        terraform_module_dir,
        destroy_after=DESTROY_AFTER,
        json_output=True,
        enable_trace=TRACE_TERRAFORM,
    ) as tf_output:
        LOG.info("%s", json.dumps(tf_output, indent=4))
        sm_client = get_secretsmanager_client_by_role(probe_role["role_arn"]["value"])
        # Can read
        assert (
            sm_client.get_secret_value(
                SecretId="foo",
            )["SecretString"]
            == "bar"
        )

        # Can't write
        with pytest.raises(ClientError) as err:
            sm_client.put_secret_value(
                SecretId="foo",
                SecretString="barbar",
            )
        assert err.type is ClientError
        assert err.value.response["Error"]["Code"] == "AccessDeniedException"


def test_module_writes(probe_role, secretsmanager_client):
    terraform_module_dir = osp.join(TERRAFORM_ROOT_DIR, "secret")
    probe_role_arn = probe_role["role_arn"]["value"]
    with open(osp.join(terraform_module_dir, "terraform.tfvars"), "w") as fp:
        fp.write(
            dedent(
                f"""
                region = "{REGION}"
                role_arn = "{TEST_ROLE_ARN}"

                admins = [
                    "arn:aws:iam::303467602807:role/aws-reserved/sso.amazonaws.com/us-west-1/AWSReservedSSO_AWSAdministratorAccess_422821c726d81c14",
                    "{TEST_ROLE_ARN}"
                ]
                writers = [
                    "{probe_role_arn}"
                ]
                """
            )
        )

    with terraform_apply(
        terraform_module_dir,
        destroy_after=DESTROY_AFTER,
        json_output=True,
        enable_trace=TRACE_TERRAFORM,
    ) as tf_output:
        LOG.info("%s", json.dumps(tf_output, indent=4))
        sm_client = get_secretsmanager_client_by_role(probe_role["role_arn"]["value"])

        # Can read
        assert (
            sm_client.get_secret_value(
                SecretId="foo",
            )["SecretString"]
            == "bar"
        )

        # Can write
        sm_client.put_secret_value(
            SecretId="foo",
            SecretString="barbar",
        )
        assert (
            sm_client.get_secret_value(
                SecretId="foo",
            )["SecretString"]
            == "barbar"
        )

        # Can't delete
        with pytest.raises(ClientError) as err:
            sm_client.delete_secret(SecretId="foo", ForceDeleteWithoutRecovery=True)
        assert err.type is ClientError
        assert err.value.response["Error"]["Code"] == "AccessDeniedException"
