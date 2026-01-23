import json
from os import path as osp, remove
from textwrap import dedent

import pytest
from botocore.exceptions import ClientError
from pytest_infrahouse import terraform_apply

from tests.conftest import (
    LOG,
    TERRAFORM_ROOT_DIR,
    get_secretsmanager_client_by_role,
    MODULE_VERSION,
)


def init_terraform_tf(terraform_dir, aws_provider_version="~> 5.11"):
    import shutil

    state_files = [
        osp.join(terraform_dir, ".terraform"),
        osp.join(terraform_dir, ".terraform.lock.hcl"),
    ]

    for state_file in state_files:
        try:
            if osp.isdir(state_file):
                shutil.rmtree(state_file)
            elif osp.isfile(state_file):
                remove(state_file)
        except FileNotFoundError:
            # File was already removed by another process
            pass

    # Update terraform.tf with the specified AWS provider version
    terraform_tf_content = dedent(
        f"""
        terraform {{
          required_providers {{
            aws = {{
              source  = "hashicorp/aws"
              version = "{aws_provider_version}"
            }}
          }}
        }}
        """
    )

    with open(osp.join(terraform_dir, "terraform.tf"), "w") as fp:
        fp.write(terraform_tf_content)


@pytest.mark.parametrize(
    "aws_provider_version", ["~> 5.11", "~> 6.0"], ids=["aws-5", "aws-6"]
)
@pytest.mark.parametrize("probe_role_suffix", ["", "*"])
def test_module(
    probe_role,
    keep_after,
    test_role_arn,
    probe_role_suffix,
    aws_region,
    aws_provider_version,
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
                    "{probe_role_arn}{probe_role_suffix}"
                ]
                """
            )
        )
    init_terraform_tf(terraform_module_dir, aws_provider_version)

    with terraform_apply(
        terraform_module_dir,
        destroy_after=not keep_after,
        json_output=True,
    ) as tf_output:
        LOG.info("%s", json.dumps(tf_output, indent=4))


def test_module_no_access(
    probe_role, keep_after, test_role_arn, aws_region, boto3_session
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
    init_terraform_tf(terraform_module_dir)

    with terraform_apply(
        terraform_module_dir,
        destroy_after=not keep_after,
        json_output=True,
    ) as tf_output:
        LOG.info("%s", json.dumps(tf_output, indent=4))
        sm_client = get_secretsmanager_client_by_role(
            probe_role_arn, boto3_session, aws_region
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
    keep_after,
    test_role_arn,
    probe_role_suffix,
    aws_region,
    boto3_session,
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
    init_terraform_tf(terraform_module_dir)

    with terraform_apply(
        terraform_module_dir,
        destroy_after=not keep_after,
        json_output=True,
    ) as tf_output:
        LOG.info("%s", json.dumps(tf_output, indent=4))
        sm_client = get_secretsmanager_client_by_role(
            probe_role["role_arn"]["value"], boto3_session, aws_region
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
    keep_after,
    test_role_arn,
    probe_role_suffix,
    aws_region,
    boto3_session,
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
    init_terraform_tf(terraform_module_dir)

    with terraform_apply(
        terraform_module_dir,
        destroy_after=not keep_after,
        json_output=True,
    ) as tf_output:
        LOG.info("%s", json.dumps(tf_output, indent=4))
        sm_client = get_secretsmanager_client_by_role(
            probe_role["role_arn"]["value"], boto3_session, aws_region
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


def test_module_secret_value(
    probe_role, keep_after, test_role_arn, aws_region, boto3_session
):
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
    init_terraform_tf(terraform_module_dir)

    with terraform_apply(
        terraform_module_dir,
        destroy_after=not keep_after,
        json_output=True,
    ) as tf_output:
        LOG.info("%s", json.dumps(tf_output, indent=4))

        secret_value_0 = tf_output["secret_value"]["value"]
        sm_client = get_secretsmanager_client_by_role(
            probe_role_arn, boto3_session, aws_region
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
                probe_role_arn, boto3_session, aws_region
            )
            assert (
                sm_client.get_secret_value(
                    SecretId="foo",
                )["SecretString"]
                == secret_value_0
            )


def test_module_external_value(
    probe_role, keep_after, test_role_arn, aws_region, boto3_session
):
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
    init_terraform_tf(terraform_module_dir)
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
            probe_role_arn, boto3_session, aws_region
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
                probe_role_arn, boto3_session, aws_region
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
    init_terraform_tf(terraform_module_dir)

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
    init_terraform_tf(terraform_module_dir)

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
        expected_tags = [
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
            {
                "Key": "module_version",
                "Value": MODULE_VERSION,
            },
        ]
        for tag in expected_tags:
            assert tag in response["Tags"]


def test_module_null_secret_value_output(
    probe_role, keep_after, test_role_arn, aws_region, boto3_session
):
    """
    Test that when secret_value input is null:
    1. The secret_value output is None (not "NoValue")
    2. After setting value via AWS SDK, output reflects the new value
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
    init_terraform_tf(terraform_module_dir)

    # First apply: secret_value output should be None when no AWSCURRENT exists
    with terraform_apply(
        terraform_module_dir,
        destroy_after=not keep_after,
        json_output=True,
    ) as tf_output:
        LOG.info("First apply output: %s", json.dumps(tf_output, indent=4))

        # Verify secret_value output is absent (Terraform omits null sensitive outputs)
        assert "secret_value" not in tf_output, (
            f"Expected secret_value to be absent when secret_value input is null, "
            f"but got: {tf_output.get('secret_value')!r}"
        )

        # Set a real value via AWS SDK
        sm_client = get_secretsmanager_client_by_role(
            probe_role_arn, boto3_session, aws_region
        )
        sm_client.put_secret_value(
            SecretId="foo",
            SecretString="externally-set-value",
        )

        # Second apply: secret_value output should now reflect the externally set value
        with terraform_apply(
            terraform_module_dir,
            destroy_after=not keep_after,
            json_output=True,
        ) as tf_output_2:
            LOG.info("Second apply output: %s", json.dumps(tf_output_2, indent=4))

            secret_value_output_2 = tf_output_2["secret_value"]["value"]
            LOG.info(
                "secret_value output after second apply: %r", secret_value_output_2
            )
            assert secret_value_output_2 == "externally-set-value", (
                f"Expected secret_value output to be 'externally-set-value' after external update, "
                f"got: {secret_value_output_2!r}"
            )


def test_module_duplicate_role(
    probe_role, keep_after, test_role_arn, aws_region, boto3_session
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
    init_terraform_tf(terraform_module_dir)

    with terraform_apply(
        terraform_module_dir,
        destroy_after=not keep_after,
        json_output=True,
    ) as tf_output:
        LOG.info("%s", json.dumps(tf_output, indent=4))
        sm_client = get_secretsmanager_client_by_role(
            probe_role["role_arn"]["value"], boto3_session, aws_region
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
