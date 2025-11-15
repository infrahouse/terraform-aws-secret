# Plan: Fix SSO Role Assumption Issue (#34)

## Problem Statement
The module fails when users authenticate via AWS SSO because the `get_secret.py` script attempts to assume a
n AWS SSO reserved role that's already in use. AWS doesn't allow assuming SSO reserved roles via `sts:AssumeRole`, 
even when already using that role.

**Error:**
```
User: arn:aws:sts::<account>:assumed-role/AWSReservedSSO_<name>/<user>
is not authorized to perform: sts:AssumeRole on resource:
arn:aws:iam::<account>:role/aws-reserved/sso.amazonaws.com/...
```

## Root Cause
In `assets/get_secret.py:23-34`, the `get_client()` function always calls `sts.assume_role()` without checking 
if the current credentials already have the necessary permissions.

In `data_sources.tf:5-6`, the module extracts the caller's role name and passes it to the Python script, 
which then tries to assume that same role.

## Proposed Solution
Modify `get_client()` to detect when we're already using the target role and skip the assumption step. This handles:
1. AWS SSO users (assumed-role ARNs)
2. Regular IAM roles already in use
3. Cross-role assumptions (existing behavior)

## Implementation Steps

### 1. ✅ Update `get_client()` function in `assets/get_secret.py`
- ✅ Call `sts.get_caller_identity()` to get current ARN
- ✅ Extract role name from target role ARN using `split("/")[-1]`
- ✅ Compare using pattern: `assumed-role/{target_role_name}/` in current ARN
- ✅ If already using the target role → use current session
- ✅ If different role → assume it (existing behavior)

**Final Detection Logic:**
```python
target_role_name = role_arn.split("/")[-1]
if f"assumed-role/{target_role_name}/" in current_arn:
    # Use current session
```

### 2. ✅ Error handling
- ✅ Existing error handling maintained (ClientError in get_secret())
- ✅ Natural error propagation from AWS SDK if credentials are insufficient
- ✅ Backward compatibility preserved - errors from assume_role still surface properly

### 3. ✅ Testing

**CI/CD Testing:**
- ✅ All 14 existing tests passed (10 minutes runtime)
- ✅ Validates backward compatibility with IAM role workflows
- ✅ Confirms the fix is role-agnostic

**Manual SSO Testing:**
- ✅ Validated in actual use case where original error occurred
- ✅ Module now works with AWS SSO credentials

## Files to Modify
- `assets/get_secret.py` - Update `get_client()` function

## Alternative Solutions Considered

### Option A: Make secret reading optional
Add a `read_secret_value` parameter to skip reading entirely.
**Rejected:** Doesn't solve the core issue, just works around it.

### Option B: Detect SSO roles by prefix
Only skip assumption for `aws-reserved/sso.amazonaws.com` roles.
**Rejected:** Too narrow, doesn't handle other scenarios where re-assuming is unnecessary.

### Option C: Always use current credentials
Never assume roles.
**Rejected:** Breaks cross-role scenarios that currently work.

## Success Criteria
- ✅ SSO users can use the module without errors
- ✅ Existing IAM role-based workflows continue to work
- ✅ Cross-account role assumption still functions
- ✅ No breaking changes to module interface

## Release Automation

### 4. ✅ Setup git-cliff for Changelog Management

**Files created:**
- ✅ `cliff.toml` - git-cliff configuration (based on terraform-aws-update-dns)
- ✅ `CHANGELOG.md` - Initial changelog file with existing version history

**Configuration details:**
- ✅ Uses conventional commits (feat, fix, docs, chore, etc.)
- ✅ Links to GitHub issues automatically using pattern `(#123)`
- ✅ Groups commits by type (Features, Bug Fixes, Documentation, etc.)
- ✅ Skips release preparation commits
- ✅ Repository URL pattern: `https://github.com/infrahouse/terraform-aws-secret/issues/`

**Reference:** `C:\Users\aleks\code\infrahouse\terraform\terraform-aws-update-dns\cliff.toml`

### 5. ✅ Add Makefile Release Targets

**Targets added:**
- ✅ `make release-patch` - Release patch version (x.x.PATCH)
- ✅ `make release-minor` - Release minor version (x.MINOR.0)
- ✅ `make release-major` - Release major version (MAJOR.0.0)

**Release workflow:**
1. ✅ Check if on `main` branch
2. ✅ Check git-cliff and bumpversion are installed
3. ✅ Calculate new version based on current version
4. ✅ Prompt user for confirmation
5. ✅ Generate changelog entry with `git cliff --unreleased --tag <version> --prepend CHANGELOG.md`
6. ✅ Commit CHANGELOG.md
7. ✅ Bump version with bumpversion
8. ✅ Remind user to `git push && git push --tags`

**Reference:** `C:\Users\aleks\code\infrahouse\terraform\terraform-aws-update-dns\Makefile` lines 69-156

**Implementation complete:**
- ✅ `.bumpversion.cfg` already exists and configured
- ✅ `cliff.toml` created
- ✅ `CHANGELOG.md` created with version history
- ✅ Makefile release targets added (lines 74-161)
