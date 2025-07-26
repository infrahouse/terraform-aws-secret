import json
from os import path as osp
from pprint import pprint
from textwrap import dedent

import pytest
from botocore.exceptions import ClientError
from infrahouse_toolkit.terraform import terraform_apply

from tests.conftest import (
    LOG,
    TERRAFORM_ROOT_DIR,
    get_secretsmanager_client_by_role,
)


@pytest.mark.parametrize("probe_role_suffix", ["", "*"])
def test_module(probe_role, keep_after, test_role_arn, probe_role_suffix, aws_region):
    terraform_module_dir = osp.join(TERRAFORM_ROOT_DIR, "secret")
    probe_role_arn = probe_role["role_arn"]["value"]
    with open(osp.join(terraform_module_dir, "terraform.tfvars"), "w") as fp:
        fp.write(
            dedent(
                f"""
                region = "{aws_region}"
                role_arn = "{test_role_arn}"

                admins = [
                    "{probe_role_arn}{probe_role_suffix}"
                ]
                """
            )
        )

    with terraform_apply(
        terraform_module_dir,
        destroy_after=not keep_after,
        json_output=True,
    ) as tf_output:
        LOG.info("%s", json.dumps(tf_output, indent=4))


def test_module_no_access(
    probe_role, secretsmanager_client, keep_after, test_role_arn, aws_region
):
    terraform_module_dir = osp.join(TERRAFORM_ROOT_DIR, "secret")
    probe_role_arn = probe_role["role_arn"]["value"]
    with open(osp.join(terraform_module_dir, "terraform.tfvars"), "w") as fp:
        fp.write(
            dedent(
                f"""
                region = "{aws_region}"
                role_arn = "{test_role_arn}"

                admins = [
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
        LOG.info("%s", json.dumps(tf_output, indent=4))
        sm_client = get_secretsmanager_client_by_role(
            probe_role_arn, test_role_arn, aws_region
        )
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


@pytest.mark.parametrize("probe_role_suffix", ["", "*"])
def test_module_reads(
    probe_role,
    secretsmanager_client,
    keep_after,
    test_role_arn,
    probe_role_suffix,
    aws_region,
):
    terraform_module_dir = osp.join(TERRAFORM_ROOT_DIR, "secret")
    probe_role_arn = probe_role["role_arn"]["value"]
    with open(osp.join(terraform_module_dir, "terraform.tfvars"), "w") as fp:
        fp.write(
            dedent(
                f"""
                region = "{aws_region}"
                role_arn = "{test_role_arn}"

                admins = [
                    "{test_role_arn}"
                ]
                readers = [
                    "{probe_role_arn}{probe_role_suffix}"
                ]
                """
            )
        )

    with terraform_apply(
        terraform_module_dir,
        destroy_after=not keep_after,
        json_output=True,
    ) as tf_output:
        LOG.info("%s", json.dumps(tf_output, indent=4))
        sm_client = get_secretsmanager_client_by_role(
            probe_role["role_arn"]["value"], test_role_arn, aws_region
        )
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


@pytest.mark.parametrize("probe_role_suffix", ["", "*"])
def test_module_writes(
    probe_role,
    secretsmanager_client,
    keep_after,
    test_role_arn,
    probe_role_suffix,
    aws_region,
):
    terraform_module_dir = osp.join(TERRAFORM_ROOT_DIR, "secret")
    probe_role_arn = probe_role["role_arn"]["value"]
    with open(osp.join(terraform_module_dir, "terraform.tfvars"), "w") as fp:
        fp.write(
            dedent(
                f"""
                region = "{aws_region}"
                role_arn = "{test_role_arn}"

                admins = [
                    "{test_role_arn}"
                ]
                writers = [
                    "{probe_role_arn}{probe_role_suffix}"
                ]
                """
            )
        )

    with terraform_apply(
        terraform_module_dir,
        destroy_after=not keep_after,
        json_output=True,
    ) as tf_output:
        LOG.info("%s", json.dumps(tf_output, indent=4))
        sm_client = get_secretsmanager_client_by_role(
            probe_role["role_arn"]["value"], test_role_arn, aws_region
        )

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


def test_module_secret_value(probe_role, keep_after, test_role_arn, aws_region):
    probe_role_arn = probe_role["role_arn"]["value"]
    terraform_module_dir = osp.join(TERRAFORM_ROOT_DIR, "secret")
    with open(osp.join(terraform_module_dir, "terraform.tfvars"), "w") as fp:
        fp.write(
            dedent(
                f"""
                region = "{aws_region}"
                role_arn = "{test_role_arn}"
                admins = []

                writers = [
                    "{probe_role_arn}"
                ]
                secret_value = "generate"
                """
            )
        )

    with terraform_apply(
        terraform_module_dir,
        destroy_after=not keep_after,
        json_output=True,
    ) as tf_output:
        LOG.info("%s", json.dumps(tf_output, indent=4))

        secret_value_0 = tf_output["secret_value"]["value"]
        sm_client = get_secretsmanager_client_by_role(
            probe_role_arn, test_role_arn, aws_region
        )
        # Can read
        assert (
            sm_client.get_secret_value(
                SecretId="foo",
            )["SecretString"]
            == secret_value_0
        )

        # Overwrite the secret and make sure Terraform reverts the secret
        sm_client.put_secret_value(
            SecretId="foo",
            SecretString="barbar",
        )

        with terraform_apply(
            terraform_module_dir,
            destroy_after=not keep_after,
            json_output=True,
        ):
            sm_client = get_secretsmanager_client_by_role(
                probe_role_arn, test_role_arn, aws_region
            )
            assert (
                sm_client.get_secret_value(
                    SecretId="foo",
                )["SecretString"]
                == secret_value_0
            )


def test_module_external_value(probe_role, keep_after, test_role_arn, aws_region):
    """
    Create a secret, set the value outside of Terraform
    """
    probe_role_arn = probe_role["role_arn"]["value"]
    terraform_module_dir = osp.join(TERRAFORM_ROOT_DIR, "secret")
    with open(osp.join(terraform_module_dir, "terraform.tfvars"), "w") as fp:
        fp.write(
            dedent(
                f"""
                region = "{aws_region}"
                role_arn = "{test_role_arn}"
                admins = []

                writers = [
                    "{probe_role_arn}"
                ]
                secret_value = null
                """
            )
        )
    # Ensure destroy
    with terraform_apply(
        terraform_module_dir,
        destroy_after=True,
        json_output=True,
    ) as tf_output:
        LOG.info("%s", json.dumps(tf_output, indent=4))

    # The test itself
    with terraform_apply(
        terraform_module_dir,
        destroy_after=not keep_after,
        json_output=True,
    ) as tf_output:
        LOG.info("%s", json.dumps(tf_output, indent=4))

        # secret_value_0 = tf_output["secret_value"]["value"]
        sm_client = get_secretsmanager_client_by_role(
            probe_role_arn, test_role_arn, aws_region
        )
        assert (
            sm_client.get_secret_value(
                SecretId="foo",
            )["SecretString"]
            == "NoValue"
        )

        # Overwrite the secret and make sure Terraform reverts the secret
        sm_client.put_secret_value(
            SecretId="foo",
            SecretString="barbar",
        )

        with terraform_apply(
            terraform_module_dir,
            destroy_after=not keep_after,
            json_output=True,
        ):
            sm_client = get_secretsmanager_client_by_role(
                probe_role_arn, test_role_arn, aws_region
            )
            assert (
                sm_client.get_secret_value(
                    SecretId="foo",
                )["SecretString"]
                == "barbar"
            )


def test_module_name_prefix(keep_after, test_role_arn, aws_region):
    terraform_module_dir = osp.join(TERRAFORM_ROOT_DIR, "secret")
    with open(osp.join(terraform_module_dir, "terraform.tfvars"), "w") as fp:
        fp.write(
            dedent(
                f"""
                region = "{aws_region}"
                role_arn = "{test_role_arn}"
                secret_name = null
                secret_name_prefix = "some_secret"

                admins = []
                """
            )
        )

    with terraform_apply(
        terraform_module_dir,
        destroy_after=not keep_after,
        json_output=True,
    ) as tf_output:
        LOG.info("%s", json.dumps(tf_output, indent=4))
        assert tf_output["secret_name"]["value"].startswith("some_secret")


def test_module_tags(
    boto3_session, secretsmanager_client, keep_after, test_role_arn, aws_region
):
    terraform_module_dir = osp.join(TERRAFORM_ROOT_DIR, "secret")
    with open(osp.join(terraform_module_dir, "terraform.tfvars"), "w") as fp:
        fp.write(
            dedent(
                f"""
                region = "{aws_region}"
                role_arn = "{test_role_arn}"
                tags = {{
                    tag1: "value1"
                }}
                """
            )
        )

    with terraform_apply(
        terraform_module_dir,
        destroy_after=not keep_after,
        json_output=True,
    ) as tf_output:
        LOG.info("%s", json.dumps(tf_output, indent=4))
        response = secretsmanager_client.describe_secret(
            SecretId=tf_output["secret_arn"]["value"]
        )
        sts_client = boto3_session.client("sts", region_name=aws_region)
        assert response["Tags"] == [
            {
                "Key": "owner",
                "Value": test_role_arn,
            },
            {
                "Key": "tag1",
                "Value": "value1",
            },
            {
                "Key": "environment",
                "Value": "development",
            },
            {
                "Key": "created_by_module",
                "Value": "infrahouse/secret/aws",
            },
            {
                "Key": "service",
                "Value": "unknown",
            },
            {
                "Key": "created_by",
                "Value": "infrahouse/terraform-aws-secret",
            },
            {
                "Key": "account",
                "Value": sts_client.get_caller_identity()["Account"],
            },
        ]


def test_module_duplicate_role(
    probe_role, secretsmanager_client, keep_after, test_role_arn, aws_region
):
    terraform_module_dir = osp.join(TERRAFORM_ROOT_DIR, "secret")
    probe_role_arn = probe_role["role_arn"]["value"]
    with open(osp.join(terraform_module_dir, "terraform.tfvars"), "w") as fp:
        fp.write(
            dedent(
                f"""
                region = "{aws_region}"
                role_arn = "{test_role_arn}"

                admins = [
                    "{test_role_arn}"
                ]
                writers = [
                    "{probe_role_arn}"
                ]
                readers = [
                    "{probe_role_arn}"
                ]
                """
            )
        )

    with terraform_apply(
        terraform_module_dir,
        destroy_after=not keep_after,
        json_output=True,
    ) as tf_output:
        LOG.info("%s", json.dumps(tf_output, indent=4))
        sm_client = get_secretsmanager_client_by_role(
            probe_role["role_arn"]["value"], test_role_arn, aws_region
        )

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
