.DEFAULT_GOAL := help

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
    match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
    if match:
        target, help = match.groups()
        print("%-40s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

TEST_REGION ?= us-west-1
TEST_ROLE ?= arn:aws:iam::303467602807:role/secret-tester
TEST_PATH ?= tests/test_module.py
TEST_FILTER ?=

help: install-hooks
	@python -c "$$PRINT_HELP_PYSCRIPT" < Makefile

.PHONY: install-hooks
install-hooks:  ## Install repo hooks
	@echo "Checking and installing hooks"
	@test -d .git/hooks || (echo "Looks like you are not in a Git repo" ; exit 1)
	@test -L .git/hooks/pre-commit || ln -fs ../../hooks/pre-commit .git/hooks/pre-commit
	@chmod +x .git/hooks/pre-commit
	@test -L .git/hooks/commit-msg || ln -fs ../../hooks/commit-msg .git/hooks/commit-msg
	@chmod +x .git/hooks/commit-msg


.PHONY: test
test:  ## Run tests on the module
	rm -f test_data/test_module/.terraform.lock.hcl
	pytest -xvvs --test-role-arn "arn:aws:iam::303467602807:role/secret-tester" tests/

.PHONY: test-keep
test-keep:  ## Run a test and keep resources (use TEST_PATH and TEST_FILTER to specify tests)
	pytest -xvvs \
		--aws-region=${TEST_REGION} \
		--test-role-arn=${TEST_ROLE} \
		--keep-after \
		$(if ${TEST_FILTER},-k "${TEST_FILTER}") \
		${TEST_PATH} \
		2>&1 | tee pytest-`date +%Y%m%d-%H%M%S`-output.log

.PHONY: test-clean
test-clean:  ## Run a test and destroy resources (use TEST_PATH and TEST_FILTER to specify tests)
	pytest -xvvs \
		--aws-region=${TEST_REGION} \
		--test-role-arn=${TEST_ROLE} \
		$(if ${TEST_FILTER},-k "${TEST_FILTER}") \
		${TEST_PATH} \
		2>&1 | tee pytest-`date +%Y%m%d-%H%M%S`-output.log

.PHONY: bootstrap
bootstrap: install-hooks ## bootstrap the development environment
	pip install -U "pip ~= 25.0"
	pip install -U "setuptools ~= 80.0"
	pip install -r requirements.txt

.PHONY: clean
clean: ## clean the repo from cruft
	rm -rf .pytest_cache
	find . -name '.terraform' -exec rm -fr {} +

.PHONY: fmt
fmt: format

.PHONY: format
format:  ## Use terraform fmt to format all files in the repo
	@echo "Formatting terraform files"
	terraform fmt -recursive
	black tests

define BROWSER_PYSCRIPT
import os, webbrowser, sys

from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

BROWSER := python -c "$$BROWSER_PYSCRIPT"

.PHONY: docs
docs: ## generate Sphinx HTML documentation, including API docs
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	$(BROWSER) docs/_build/html/index.html

.PHONY: lint
lint:  ## Lint the module
	@echo "Check code style"
	black --check tests
	terraform fmt -check

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
			git commit -m "Update CHANGELOG for $$NEW_VERSION"; \
			echo "Bumping version with bumpversion..."; \
			bumpversion --new-version $$NEW_VERSION patch; \
			echo ""; \
			echo "✓ Released version $$NEW_VERSION"; \
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
