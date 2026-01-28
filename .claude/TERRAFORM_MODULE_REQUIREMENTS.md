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

**Badges to include:**
- **Terraform Registry**: `[![Registry](https://img.shields.io/badge/terraform-registry-623CE4?logo=terraform)](registry url)`
- **Latest Release**: `[![GitHub release](https://img.shields.io/github/v/release/infrahouse/repo-name)](release url)`
- **License**: `[![License](https://img.shields.io/github/license/infrahouse/repo-name)](LICENSE)`
- **Documentation**: `[![Docs](https://img.shields.io/badge/docs-github.io-blue)](https://infrahouse.github.io/repo-name/)`
- **Security**: `[![Security](https://github.com/infrahouse/repo-name/actions/workflows/vuln-scanner-pr.yml/badge.svg)](workflow url)`
- **AWS Service Badge(s)**: Link to relevant AWS service(s) the module uses (e.g., Lambda, ECS, RDS). Use shields.io badges with AWS service logos.
- **Contact/Services**: `[![Need Help?](https://img.shields.io/badge/Need%20Help%3F-Contact%20Us-0066CC)](https://infrahouse.com/contact)` - Call to action for professional services

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
- `changelog.md` - Or link to CHANGELOG.md

**Optional but Recommended:**
- `comparison.md` - vs alternatives
- `security.md` - Security considerations
- `monitoring.md` - Observability setup
- `upgrading.md` - Migration guides

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
- `.github/ISSUE_TEMPLATE/` (bug report, feature request)
- `.github/PULL_REQUEST_TEMPLATE.md`

### 4. Testing & Quality

- Working examples in `examples/` that can be tested
- `tests/` directory with pytest-based integration tests
  - Uses pytest-infrahouse fixtures
  - Uses infrahouse-core for validation
  - Tests against multiple AWS provider versions
  - Makefile targets: `test-keep`/`test-clean` (for development), `test` (for CI)
- Pre-commit hooks (terraform fmt, terraform-docs, tflint)
- Automated CI/CD with terraform validate and plan
- Security scanning (OSV, checkov, tfsec)

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
```makefile
release-patch:
	git-cliff --tag $(shell bumpversion --dry-run --list patch | grep new_version | cut -d= -f2) -o CHANGELOG.md
	bumpversion patch
	git push && git push --tags
	# GitHub Actions workflow automatically creates the release
```

### 6. GitHub Repository Settings

- GitHub Pages enabled (already automated!)
- Topics/tags (terraform, aws, infrastructure, etc.)
- About section with description and website link
- Social media card image (optional but nice)
- Discussions enabled (for community Q&A)
- Issues with templates
- Branch protection with required reviews

### 7. Updates to CODING_STANDARD.md

Proposed additions:

```markdown
* **README.md (required):**
  - Header with module name and description
  - Badge row with:
    - Terraform Registry link
    - Latest release version
    - License
    - Documentation (GitHub Pages link)
    - Security scanning status
    - Relevant AWS service badge
  - "Why This Module?" section (differentiation)
  - Features list
  - Quick Start example
  - Documentation links (to GitHub Pages)
  - terraform-docs markers: `<!-- BEGIN_TF_DOCS -->` and `<!-- END_TF_DOCS -->`
  - Links to Contributing and License

* **GitHub Pages Documentation (required for terraform_module):**
  - Deployed via .github/workflows/docs.yml
  - Built with MkDocs (Material theme)
  - Minimum pages: index, getting-started, configuration
  - Architecture diagrams where applicable
  - Working examples with explanations

* **Repository Files (required):**
  - LICENSE file (Apache 2.0 recommended)
  - CHANGELOG.md (auto-generated via git-cliff)
  - SECURITY.md (security policy)
  - CONTRIBUTING.md (contribution guidelines)
  - .github/workflows/release.yml (auto-create releases from tags)
  - examples/ directory with working examples

* **Repository Configuration:**
  - GitHub Pages enabled and deployed
  - Topics/tags set (terraform, aws, relevant services)
  - About section filled with website link
  - Issue and PR templates configured
```

## Reference Implementation

See [terraform-aws-actions-runner](https://github.com/infrahouse/terraform-aws-actions-runner) as the reference implementation:
- [Published Documentation](https://infrahouse.github.io/terraform-aws-actions-runner/)
- [Repository Page](https://github.com/infrahouse/terraform-aws-actions-runner)
## Implementation Plan

1. Enable GitHub Pages for all terraform_module repos (✅ automated via repos.tf)
2. Deploy docs.yml workflow to all modules (✅ automated)
3. Create baseline docs/index.md and mkdocs.yml where missing (✅ automated)
4. Deploy release.yml workflow to all modules (automate GitHub Release creation)
5. Create GitHub Project to track documentation completion
6. For each module:
   - Update README.md with badges and structure
   - Create comprehensive GitHub Pages documentation
   - Add missing repository files (SECURITY.md, CONTRIBUTING.md, etc.)
   - Set up proper GitHub repository settings
   - Ensure working examples exist
   - Verify release automation works
