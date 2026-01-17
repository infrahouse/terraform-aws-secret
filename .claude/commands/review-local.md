---
description: Run Terraform module review locally (similar to GitHub PR review)
---

You are running a local Terraform module review, similar to the automated GitHub PR review workflow.

## Your Task

1. **Create review directory:**
   ```bash
   mkdir -p .claude/reviews
   ```

2. **Check for previous review:**
   - Look for `.claude/reviews/terraform-module-review.md`
   - If it exists, this is a follow-up review (read the existing file as the "previous" review)
   - If it doesn't exist, this is the first review

3. **Get changes to review:**
   - First, check what changes exist:
     ```bash
     # Check for uncommitted changes
     git status --short

     # Check for commits ahead of main/master
     git log --oneline origin/main..HEAD 2>/dev/null || git log --oneline origin/master..HEAD 2>/dev/null || echo "No remote branch found"
     ```

   - Based on what's found, create a diff file in .claude/reviews/:
     - **If there are uncommitted changes:** `git diff HEAD > .claude/reviews/pr-changes.diff`
     - **If there are committed changes ahead of main:** `git diff origin/main...HEAD > .claude/reviews/pr-changes.diff` (or origin/master)
     - **If no changes:** Tell the user there's nothing to review

4. **Show the user what will be reviewed:**
   ```bash
   echo "Changes to review:"
   cat .claude/reviews/pr-changes.diff | head -50
   echo ""
   echo "Total lines in diff: $(wc -l < .claude/reviews/pr-changes.diff)"
   ```

5. **Launch the terraform-module-reviewer agent:**

   **For FIRST review (no previous review found):**
   ```
   Launch the terraform-module-reviewer agent.

   Review all changes in .claude/reviews/pr-changes.diff file.

   Focus your review on the changes made while considering the overall module context.
   Analyze what was added, modified, or removed, and assess the impact on:
   - Security
   - Functionality
   - Best practices compliance
   - Code standards

   IMPORTANT: Save your complete review to .claude/reviews/terraform-module-review.md
   as specified in your agent instructions.
   ```

   **For FOLLOW-UP review (previous review exists):**
   ```
   Launch the terraform-module-reviewer agent.

   This is a follow-up review.

   Read the previous review from .claude/reviews/terraform-module-review.md
   and the current changes in .claude/reviews/pr-changes.diff.

   Compare the previous findings with the current state:
   - Mark issues as '✅ FIXED:' if they have been resolved
   - Mark issues as '⚠️ STILL PRESENT:' if unaddressed
   - Mark new issues as '🆕 NEW:' if they appear for the first time
   - Provide a summary at the top showing progress
     (e.g., '3 issues fixed, 1 still present, 2 new issues found')

   Focus on showing what has improved and what still needs attention.

   IMPORTANT: Overwrite .claude/reviews/terraform-module-review.md with your
   new review (replacing the previous one) as specified in your agent instructions.
   ```

6. **After the agent completes:**
   - Verify the review was created/updated: `ls -lh .claude/reviews/terraform-module-review.md`
   - Show the user where to find it
   - Let them know they can:
     - Read the review now
     - Make changes and run /review again to see what improved

## Important Notes

- This review runs **locally** - it won't post to GitHub
- The review helps you catch issues **before** creating a PR
- You can iterate: make changes → run /review again → see what improved
- Each /review run overwrites the previous review (showing your progress)
- When you're satisfied, create your PR and the GitHub workflow will do the official review