# Contributing to this Project

Thank you for your interest in contributing! This document provides guidelines for contributing to this Terraform module.

## How to Contribute

### Reporting Issues

- Check existing issues before creating a new one
- Use a clear, descriptive title
- Include Terraform and provider versions
- Provide minimal reproduction steps
- Include relevant logs or error messages

### Submitting Changes

1. Fork the repository
2. Create a feature branch from `main`
3. Make your changes following our coding standards
4. Write or update tests as needed
5. Run `make test-clean` to verify all tests pass
6. Submit a pull request

### Pull Request Guidelines

- Reference any related issues
- Provide a clear description of changes
- Ensure CI checks pass
- Keep changes focused and atomic
- Update documentation if needed

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/REPO_NAME.git
cd REPO_NAME

# Install dependencies
make bootstrap

# Run tests (keeps infrastructure for debugging)
make test-keep

# Run tests with cleanup (before PR)
make test-clean
```

## Coding Standards

Please follow the coding standards defined in `.claude/CODING_STANDARD.md`:

- Use `terraform fmt` for formatting
- Follow naming conventions (snake_case)
- Add descriptions to all variables and outputs
- Include validation blocks where appropriate
- Use conventional commits for commit messages

## Commit Message Format

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: Add support for custom IAM policies
fix: Correct security group ingress rules
docs: Update README with new examples
refactor: Simplify variable validation logic
```

## Testing

- Tests use pytest with pytest-infrahouse fixtures
- Tests create real AWS infrastructure
- Always run `make test-clean` before submitting PR
- Ensure tests pass for all supported AWS provider versions

## Questions?

- Open a GitHub issue for questions about contributing
- See [SECURITY.md](SECURITY.md) for reporting security vulnerabilities

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.
