# InfraHouse Terraform Module Requirements

This document defines the standards and requirements for all InfraHouse Terraform modules to ensure professional, 
well-documented, and maintainable infrastructure code.

## Goal

Provide comprehensive, professional documentation and tooling for all InfraHouse Terraform modules.

## Essential Components for Each Terraform Module Repository

### 1. README.md Structure

**Header Section:**
- Module name and tagline
- Comprehensive badge row

**Badges (in this order):**
- **Contact**: `[![Need Help?](https://img.shields.io/badge/Need%20Help%3F-Contact%20Us-0066CC)](https://infrahouse.com/contact)`
- **Documentation**: `[![Docs](https://img.shields.io/badge/docs-github.io-blue)](https://infrahouse.github.io/repo-name/)`
- **Terraform Registry**: `[![Registry](https://img.shields.io/badge/Terraform-Registry-purple?logo=terraform)](https://registry.terraform.io/modules/infrahouse/module-name/aws/latest)`
- **Latest Release**: `[![Release](https://img.shields.io/github/release/infrahouse/repo-name.svg)](https://github.com/infrahouse/repo-name/releases/latest)`
- **AWS Service Badge(s)**: `[![AWS EC2](https://img.shields.io/badge/AWS-EC2-orange?logo=amazonec2)](https://aws.amazon.com/ec2/)` (link to relevant AWS service(s))
- **Security**: `[![Security](https://img.shields.io/github/actions/workflow/status/infrahouse/repo-name/vuln-scanner-pr.yml?label=Security)](https://github.com/infrahouse/repo-name/actions/workflows/vuln-scanner-pr.yml)`
- **License**: `[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)`

**Content Sections:**
1. Brief description (what it does, why it exists)
2. **Why This Module?** (differentiation from alternatives)
3. **Features** (bullet list)
4. **Quick Start** (minimal working example)
5. **Documentation** (links to GitHub Pages sections)
6. **Requirements** (Terraform version, providers)
7. **Usage** (terraform-docs auto-generated section between `<!-- BEGIN_TF_DOCS -->` and `<!-- END_TF_DOCS -->`)
8. **Examples** (link to examples/)
9. **Contributing** (link to CONTRIBUTING.md)
10. **License** (link to LICENSE)

### 2. Documentation (GitHub Pages)

**Required Pages:**
- `index.md` - Overview, features, quick start
- `getting-started.md` - Prerequisites, first deployment
- `architecture.md` - How it works, diagrams
- `configuration.md` - All variables explained
- `examples.md` - Common use cases
- `troubleshooting.md` - Common issues
- `changelog.md` - Symlink to CHANGELOG.md (`ln -fs ../CHANGELOG.md docs/changelog.md`)

**Optional but Recommended:**
- `comparison.md` - vs alternatives
- `security.md` - Security considerations
- `monitoring.md` - Observability setup
- `upgrading.md` - Migration guides

**Documentation Dependencies (`requirements.txt`):**
```
diagrams ~= 0.25
mkdocs-material ~= 9.7
mkdocs-minify-plugin ~= 0.8
mkdocs-glightbox ~= 0.4
```

**`mkdocs.yml` Configuration:**
- `site_name` must follow the pattern `InfraHouse <module name>`, where the `terraform-aws-` prefix
  is omitted. For example, for `terraform-aws-actions-runner` the site name is
  `InfraHouse actions-runner`.
- The `glightbox` plugin must be enabled:
```yaml
plugins:
  - search
  - glightbox
  - minify:
      minify_html: true
```

### 3. Repository Files

**Must Have:**
- `README.md`
- `LICENSE` (Apache 2.0 recommended for patent protection and enterprise adoption)
- `CHANGELOG.md` (auto-generated with git-cliff)
- `CODING_STANDARD.md` (or link to central one)
- `.terraform-docs.yml`
- `mkdocs.yml`
- `.github/workflows/release.yml` (auto-create GitHub Releases from tags)
- `examples/` directory with working examples

**Should Have:**
- `CONTRIBUTING.md` (contribution guidelines)
- `SECURITY.md` (security policy, how to report vulnerabilities)
- `CODEOWNERS` (auto-assign reviewers)

### 4. Testing & Quality

- Working examples in `examples/` that can be tested
- `tests/` directory with pytest-based integration tests
  - Uses pytest-infrahouse fixtures
  - Uses infrahouse-core for validation
  - Target AWS provider version: `~> 6.0` (AWS 5.x is being deprecated)
  - Tests must use `aws_provider_version` parametrize to specify the provider version:
    ```python
    @pytest.mark.parametrize(
        "aws_provider_version", ["~> 6.0"], ids=["aws-6"]
    )
    def test_module(
        ...
        aws_provider_version,
    ):
    ```
  - Makefile targets: `test-keep`/`test-clean` (for development), `test` (for CI)
- Pre-commit hooks (terraform fmt, terraform-docs, tflint)
- `make bootstrap` must install pre-commit hooks (via `install-hooks` dependency)
- Automated CI/CD with terraform validate and plan
- Security scanning (OSV, checkov, tfsec)

**Security Dependencies (`requirements.txt`):**
```
checkov ~= 3.2
```

The repository must contain a `.checkov.yml` configuration file.

### 5. Release Automation

**GitHub Release Workflow** (`.github/workflows/release.yml`):
- Automatically creates GitHub Releases when tags are pushed
- Includes CHANGELOG.md content in release notes
- Enables the "Latest Release" badge in README

```yaml
name: Create Release
on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Create Release
        uses: softprops/action-gh-release@v1
        with:
          body_path: CHANGELOG.md
          generate_release_notes: true
```

**Release Process** (via Makefile targets):

The release process must:
- Check that `git-cliff` and `bumpversion` are installed (with helpful install instructions on failure)
- Verify the current branch is `main` (refuse to release from other branches)
- Show the current and new version, then prompt for confirmation before proceeding
- Update `CHANGELOG.md` using `git cliff --unreleased --tag <version> --prepend CHANGELOG.md`
  and commit it with a commit-msg compliant message (`chore: update CHANGELOG for <version>`)
- Bump the version using `bumpversion` with a compliant commit message
  (`chore: bump version to <version>`)
- Print next steps (`git push && git push --tags`) but NOT push automatically

Use a shared `do_release` function for `release-patch`, `release-minor`, and `release-major`:

```makefile
# Internal function to handle version release
# Args: $(1) = major|minor|patch
define do_release
	@echo "Checking if git-cliff is installed..."
	@command -v git-cliff >/dev/null 2>&1 || { \
		echo ""; \
		echo "Error: git-cliff is not installed."; \
		echo ""; \
		echo "Please install it using one of the following methods:"; \
		echo ""; \
		echo "  Cargo (Rust):"; \
		echo "    cargo install git-cliff"; \
		echo ""; \
		echo "  Arch Linux:"; \
		echo "    pacman -S git-cliff"; \
		echo ""; \
		echo "  Homebrew (macOS/Linux):"; \
		echo "    brew install git-cliff"; \
		echo ""; \
		echo "  From binary (Linux/macOS/Windows):"; \
		echo "    https://github.com/orhun/git-cliff/releases"; \
		echo ""; \
		echo "For more installation options, see: https://git-cliff.org/docs/installation"; \
		echo ""; \
		exit 1; \
	}
	@echo "Checking if bumpversion is installed..."
	@command -v bumpversion >/dev/null 2>&1 || { \
		echo ""; \
		echo "Error: bumpversion is not installed."; \
		echo ""; \
		echo "Please install it using:"; \
		echo "  make bootstrap"; \
		echo ""; \
		exit 1; \
	}
	@BRANCH=$$(git rev-parse --abbrev-ref HEAD); \
	if [ "$$BRANCH" != "main" ]; then \
		echo "Error: You must be on the 'main' branch to release."; \
		echo "Current branch: $$BRANCH"; \
		exit 1; \
	fi; \
	CURRENT=$$(grep ^current_version .bumpversion.cfg | head -1 | cut -d= -f2 | tr -d ' '); \
	echo "Current version: $$CURRENT"; \
	MAJOR=$$(echo $$CURRENT | cut -d. -f1); \
	MINOR=$$(echo $$CURRENT | cut -d. -f2); \
	PATCH=$$(echo $$CURRENT | cut -d. -f3); \
	if [ "$(1)" = "major" ]; then \
		NEW_VERSION=$$((MAJOR + 1)).0.0; \
	elif [ "$(1)" = "minor" ]; then \
		NEW_VERSION=$$MAJOR.$$((MINOR + 1)).0; \
	elif [ "$(1)" = "patch" ]; then \
		NEW_VERSION=$$MAJOR.$$MINOR.$$((PATCH + 1)); \
	fi; \
	echo "New version will be: $$NEW_VERSION"; \
	printf "Continue? (y/n) "; \
	read -r REPLY; \
	case "$$REPLY" in \
		[Yy]|[Yy][Ee][Ss]) \
			echo "Updating CHANGELOG.md with git-cliff..."; \
			git cliff --unreleased --tag $$NEW_VERSION --prepend CHANGELOG.md; \
			git add CHANGELOG.md; \
			git commit -m "chore: update CHANGELOG for $$NEW_VERSION"; \
			echo "Bumping version with bumpversion..."; \
			bumpversion --new-version $$NEW_VERSION \
				--message "chore: bump version to {new_version}" patch; \
			echo ""; \
			echo "Released version $$NEW_VERSION"; \
			echo ""; \
			echo "Next steps:"; \
			echo "  git push && git push --tags"; \
			;; \
		*) \
			echo "Release cancelled"; \
			;; \
	esac
endef

.PHONY: release-patch
release-patch: ## Release a patch version (x.x.PATCH)
	$(call do_release,patch)

.PHONY: release-minor
release-minor: ## Release a minor version (x.MINOR.0)
	$(call do_release,minor)

.PHONY: release-major
release-major: ## Release a major version (MAJOR.0.0)
	$(call do_release,major)
```

## Reference Implementation

See [terraform-aws-actions-runner](https://github.com/infrahouse/terraform-aws-actions-runner) as the reference implementation:
- [Published Documentation](https://infrahouse.github.io/terraform-aws-actions-runner/)
- [Repository Page](https://github.com/infrahouse/terraform-aws-actions-runner)
