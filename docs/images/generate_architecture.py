#!/usr/bin/env python3
"""Generate architecture diagram for terraform-aws-secret module."""

from diagrams import Cluster, Diagram, Edge
from diagrams.aws.security import SecretsManager, IAM
from diagrams.aws.management import Config
from diagrams.programming.language import Python
from diagrams.onprem.iac import Terraform

with Diagram(
    "terraform-aws-secret Architecture",
    filename="architecture",
    outformat="png",
    show=False,
    direction="TB",
    graph_attr={"splines": "ortho", "nodesep": "1.0", "ranksep": "1.0"},
):
    with Cluster("Terraform Module", graph_attr={"margin": "20"}):
        tf = Terraform("terraform-aws-secret")
        py_script = Python("get_secret.py")

    with Cluster("AWS Secrets Manager"):
        secret = SecretsManager("Secret")
        secret_version = Config("Secret Version")
        policy = IAM("Resource Policy")

    with Cluster("Access Control"):
        admins = IAM("Admins")
        writers = IAM("Writers")
        readers = IAM("Readers")

    # Terraform creates resources
    tf >> Edge(label="creates") >> secret
    tf >> Edge(label="creates") >> secret_version
    tf >> Edge(label="creates") >> policy

    # Policy grants access
    policy >> Edge(label="full access") >> admins
    policy >> Edge(label="read/write") >> writers
    policy >> Edge(label="read only") >> readers

    # Python script reads secret
    tf >> Edge(label="uses") >> py_script
    py_script << Edge(label="reads") << secret
