# Security Policy

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability in this project, please report it responsibly.

**Please DO NOT create a public GitHub issue for security vulnerabilities.**

### How to Report

Send an email to **security@infrahouse.com** with:

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Any suggested fixes (optional)

### What to Expect

- **Acknowledgment:** Within 48 hours of your report
- **Initial Assessment:** Within 5 business days
- **Resolution Timeline:** Depends on severity, typically 30-90 days

### Scope

This policy applies to:

- The Terraform module code in this repository
- Associated documentation and examples

### Out of Scope

- Issues in upstream dependencies (report to respective maintainers)
- Issues in AWS services (report to AWS)

## Security Best Practices

When using this module:

- Follow the principle of least privilege for IAM roles
- Enable encryption at rest and in transit where applicable
- Review the module's security group and IAM policy configurations
- Keep the module updated to the latest version

## Supported Versions

We provide security updates for the latest major version only.

| Version | Supported          |
| ------- | ------------------ |
| Latest  | :white_check_mark: |
| Older   | :x:                |