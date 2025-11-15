# Architecture Notes

## Lambda Packaging - How terraform-aws-lambda-monitored Works

### The Problem

**Original naive approach:**
```
1. null_resource creates: .build/function_name/ directory
2. archive_file reads:     .build/function_name/ directory
3. External process deletes .build/ (e.g., terraform get -update)
4. Next terraform plan:
   - Triggers unchanged → null_resource doesn't rebuild
   - archive_file tries to read missing directory → FAILS ❌
```

### The Solution (Implemented in terraform-aws-lambda-monitored v0.3.4)

#### Key Insight #1: Build In-Place
```hcl
locals {
  # Build directly in the source directory (not in a separate .build)
  build_directory = var.lambda_source_dir
}
```

**Why this helps:**
- The source directory is in **your repository** (tracked by git)
- It **survives** `terraform get -update=true` (not inside `.terraform/modules/`)
- Dependencies get installed alongside source code

#### Key Insight #2: Deterministic Hash-Based Filename
```hcl
locals {
  # Create a hash from all factors that affect the package
  package_hash = md5(join("-", [
    local.source_files_hash,      # Source code changes
    filemd5(requirements.txt),     # Dependency changes
    var.architecture,              # Platform changes
    var.python_version,            # Runtime changes
    var.function_name              # Function name
  ]))

  # Filename includes the hash
  package_filename = "${var.function_name}-${local.package_hash}.zip"
}
```

**Why this helps:**
- **Same inputs → same filename** → Terraform knows it's unchanged
- **Different inputs → different filename** → Terraform knows rebuild is needed
- The hash becomes the **source of truth** for "has anything changed?"

#### Key Insight #3: Store ZIP in path.root/.build
```hcl
data "archive_file" "lambda_source_hash" {
  source_dir  = local.build_directory
  output_path = "${path.root}/.build/${local.package_filename}"
  #                ^^^^^^^^^ Not path.module!
  depends_on = [null_resource.install_python_dependencies]
}
```

**Why this helps:**
- `path.root` = your project root (not inside `.terraform/modules/`)
- **Survives** `terraform get -update=true`
- **Survives** module re-downloads

### How It Solves the CI/CD Problem

#### Scenario: Fresh git clone in CI/CD

```
1. git clone → Fresh directory, no .build yet
2. terraform init → Pulls state from S3
3. terraform plan:
   - Calculates package_hash = "abc123"
   - Checks: Does .build/function_name-abc123.zip exist?
   - NO → archive_file will need to create it
   - depends_on → null_resource runs FIRST during apply
4. terraform apply:
   - null_resource runs → installs dependencies in source dir
   - archive_file creates → ${path.root}/.build/function_name-abc123.zip
   - ✅ SUCCESS
```

#### Scenario: Code hasn't changed (CI/CD rerun)

```
1. git clone → Fresh directory
2. terraform plan:
   - Calculates package_hash = "abc123" (SAME as before)
   - Filename = function_name-abc123.zip (SAME)
   - Checks state: "I already uploaded this exact zip to S3"
   - archive_file will package the git controlled files in a zip archive, but Terraform knows no changes needed,
     so the archive won't be updated in the S3 bucket - until a next change in the lambda core, requirements, etc.
   - ✅ No rebuild required
```

### The Clever Part

The **hash-based filename** makes the filesystem state irrelevant! Terraform compares:

```
State says:    "Uploaded function_name-abc123.zip to S3"
Current hash:  "abc123"
Filename:      "function_name-abc123.zip"
→ They match → No changes needed!
```

Even if the local `.build` directory is missing, Terraform knows the **correct artifact is already in S3**.

### What NOT to Do

#### Anti-pattern: Store build in path.module

```hcl
# BAD - Gets wiped by terraform get -update
output_path = "${path.module}/.build/${var.function_name}.zip"
```

#### Anti-pattern: Use random_uuid without hash

```hcl
# BAD - Creates new UUID even when code hasn't changed
resource "random_uuid" "lamda_src_hash" {
  keepers = { ... }
}
output_path = "${path.module}/${random_uuid.lamda_src_hash.result}.zip"
```

This stores the zip in `path.module` which gets deleted during module updates.

### References

- Module: `registry.infrahouse.com/infrahouse/lambda-monitored/aws`
- Version: 0.3.4
- File: `lambda_code.tf`
- Issue discovered: 2025-11-09 (`.build` directory deletion after terraform get -update)
