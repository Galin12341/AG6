# Git Hooks Policy Enforcement

## Overview

This repository uses Git hooks to enforce merge policies, ensuring code quality, auditability, and consistency across the team.

## Installed Hooks

### 1. pre-merge-commit Hook

**Purpose**: Prevents non-fast-forward merges to protected branches outside of PR workflows.

**Location**: `.git/hooks/pre-merge-commit`

**Triggers**: Before creating a merge commit

**Enforced Policies**:
- Protected branches (main, master, develop, release/*) require PR environment
- Fast-forward only merges for linear history
- Prevents accidental direct merges to production branches

## Protected Branches

The following branches have enhanced protection:

- `main` - Production branch
- `master` - Alternative production branch name
- `develop` - Integration branch
- `release/*` - Release preparation branches

## Merge Policy Rules

### Rule 1: PR-Only Merges (Auditability)

**Rationale**: All merges to protected branches must go through PR review for:
- Code review audit trail
- CI/CD validation
- Team awareness
- Documentation in PR description

**Enforcement**:
```bash
# ✗ This will be blocked
git checkout main
git merge feature-branch
# Error: Direct merges to 'main' not allowed outside PR environment

# ✓ Correct workflow
# 1. Push feature branch
git push origin feature-branch

# 2. Create PR via GitHub/GitLab
# 3. Get approval
# 4. Merge via PR interface
```

**Bypass** (Emergency Only):
```bash
# For hotfixes or authorized direct merges
GIT_MERGE_ALLOW_DIRECT=1 git merge hotfix-branch
```

### Rule 2: Fast-Forward Only (Bisectability)

**Rationale**: Linear history improves:
- `git bisect` effectiveness
- Commit history readability
- Simplified debugging

**Enforcement**:
```bash
# ✗ This will be blocked
git checkout main
git merge --no-ff feature-branch
# Error: Non-fast-forward merge detected

# ✓ Correct workflow
git checkout feature-branch
git rebase main
git checkout main
git merge --ff-only feature-branch
```

### Rule 3: Squash Allowed (Clean History)

**Rationale**: Squash merges acceptable for:
- Multiple WIP commits
- Maintaining clean main branch
- Feature-level granularity

**Enforcement**:
```bash
# ✓ Squash merges are allowed
git merge --squash feature-branch
git commit -m "feat: complete feature description"
```

## Hook Configuration

### Customizing Protected Branches

Edit `.git/hooks/pre-merge-commit`:

```bash
# Add custom protected branches
PROTECTED_BRANCHES=("main" "master" "develop" "release/*" "prod/*")
```

### Disabling Fast-Forward Requirement

```bash
# In .git/hooks/pre-merge-commit
REQUIRE_FF_ONLY=false  # Allow merge commits
```

### Disabling PR Requirement

```bash
# In .git/hooks/pre-merge-commit
REQUIRE_PR_ENVIRONMENT=false  # Allow direct merges
```

## Installation for Team

### Automatic Installation (Recommended)

Create `.git-hooks/` directory (tracked in repo):

```bash
# Create tracked hooks directory
mkdir .git-hooks
cp .git/hooks/pre-merge-commit .git-hooks/

# Team members install with:
./install-hooks.sh
```

**install-hooks.sh**:
```bash
#!/bin/bash
# Install git hooks from .git-hooks/ directory

HOOKS_DIR=".git/hooks"
SOURCE_DIR=".git-hooks"

for hook in "$SOURCE_DIR"/*; do
    hook_name=$(basename "$hook")
    ln -sf "../../$SOURCE_DIR/$hook_name" "$HOOKS_DIR/$hook_name"
    chmod +x "$HOOKS_DIR/$hook_name"
    echo "Installed: $hook_name"
done

echo "Git hooks installed successfully!"
```

### Manual Installation

Each team member runs:

```bash
# Copy hook to .git/hooks/
cp docs/git-hooks/pre-merge-commit .git/hooks/
chmod +x .git/hooks/pre-merge-commit
```

## Testing Hooks

### Test 1: Protected Branch Direct Merge (Should Fail)

```bash
git checkout main
git merge feature-branch
# Expected: Error message about PR requirement
```

### Test 2: Non-FF Merge (Should Fail)

```bash
# Create divergent history
git checkout -b test-branch main
echo "test" > test.txt
git add test.txt && git commit -m "test"

git checkout main
echo "main" > main.txt
git add main.txt && git commit -m "main change"

# Try non-FF merge
git merge test-branch
# Expected: Error about fast-forward requirement
```

### Test 3: FF Merge (Should Succeed)

```bash
git checkout -b test-branch-2 main
echo "test" > test2.txt
git add test2.txt && git commit -m "test"

# FF merge should work
git checkout main
git merge --ff-only test-branch-2
# Expected: Success
```

### Test 4: Bypass Flag (Should Succeed)

```bash
git checkout main
GIT_MERGE_ALLOW_DIRECT=1 git merge feature-branch
# Expected: Warning but allowed
```

## CI/CD Integration

### GitHub Actions Detection

Hook automatically detects GitHub Actions environment:

```yaml
# .github/workflows/merge-check.yml
name: Merge Policy Check

on: [pull_request]

jobs:
  policy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Verify merge policy
        run: |
          # Hook recognizes GITHUB_ACTIONS environment
          git merge origin/main
          # Proceeds normally in PR context
```

### GitLab CI Detection

Hook detects `CI_MERGE_REQUEST_ID` variable:

```yaml
# .gitlab-ci.yml
merge-check:
  script:
    - git merge origin/main
  only:
    - merge_requests
```

## Server-Side Enforcement (Ultimate Protection)

While client-side hooks help developers, server-side hooks provide true enforcement.

### GitHub Branch Protection

```
Settings → Branches → Branch protection rules

Required settings:
☑ Require pull request reviews before merging
☑ Require status checks to pass before merging
☑ Require linear history (enforces FF or squash)
☑ Include administrators
```

### GitLab Protected Branches

```
Settings → Repository → Protected Branches

main:
  - Allowed to merge: Developers + Maintainers
  - Allowed to push: No one
  - Require merge request: Yes
```

### Pre-Receive Hook (Server-Side)

For self-hosted Git servers:

```bash
#!/bin/bash
# hooks/pre-receive (on git server)

while read oldrev newrev refname; do
    branch=$(echo $refname | sed 's/refs\/heads\///')

    # Check if protected branch
    if [[ "$branch" == "main" || "$branch" == "master" ]]; then
        # Verify it's a fast-forward
        if ! git merge-base --is-ancestor $oldrev $newrev; then
            echo "Error: Non-fast-forward push to $branch rejected"
            echo "Please rebase and try again"
            exit 1
        fi
    fi
done
```

## Policy Trade-offs

### Configuration 1: Strict (Recommended for Large Teams)

```bash
REQUIRE_FF_ONLY=true
REQUIRE_PR_ENVIRONMENT=true
ALLOW_SQUASH=true
```

**Pros**:
- Maximum auditability via PR requirement
- Linear history via FF-only
- Flexibility with squash option

**Cons**:
- More ceremony for hotfixes
- Requires rebase familiarity

### Configuration 2: Balanced (Medium Teams)

```bash
REQUIRE_FF_ONLY=false
REQUIRE_PR_ENVIRONMENT=true
ALLOW_SQUASH=true
```

**Pros**:
- PR audit trail maintained
- More flexible merge strategies
- Easier for less experienced devs

**Cons**:
- Non-linear history
- Harder to bisect

### Configuration 3: Permissive (Small Teams)

```bash
REQUIRE_FF_ONLY=false
REQUIRE_PR_ENVIRONMENT=false
ALLOW_SQUASH=true
```

**Pros**:
- Maximum flexibility
- Fast iteration
- Less overhead

**Cons**:
- Easier to break main
- Less auditability
- Trust-based system

## Emergency Procedures

### Hotfix Process

When production is down and you need to bypass policies:

```bash
# 1. Create hotfix branch
git checkout -b hotfix/critical-bug main

# 2. Fix the issue
# ... make changes ...
git commit -m "hotfix: resolve critical production issue"

# 3. Merge with bypass flag
git checkout main
GIT_MERGE_ALLOW_DIRECT=1 git merge hotfix/critical-bug

# 4. Create retrospective PR
git push origin main
# Manually create PR for documentation/review
```

### Revert Process

If a bad merge gets through:

```bash
# For merge commits
git revert -m 1 <merge-sha>

# For fast-forward merges
git revert <commit-sha-1>^..<commit-sha-n>

# Or reset (if not pushed)
git reset --hard HEAD~1
```

## Monitoring and Metrics

### Hook Execution Log

Add logging to hooks:

```bash
# In hook script
LOG_FILE=".git/hooks.log"
echo "$(date): pre-merge-commit executed on $CURRENT_BRANCH" >> $LOG_FILE
```

### Analytics Queries

```bash
# Count direct merges (bypasses)
git log --grep="GIT_MERGE_ALLOW_DIRECT" --oneline | wc -l

# Count merge commits vs FF
git log --oneline --merges | wc -l
git log --oneline --no-merges | wc -l

# Average PR lifetime
gh pr list --state closed --json number,createdAt,mergedAt --jq '.[] | (.mergedAt - .createdAt)'
```

## Troubleshooting

### Hook Not Running

```bash
# Check hook is executable
ls -l .git/hooks/pre-merge-commit

# Make executable
chmod +x .git/hooks/pre-merge-commit

# Verify hooks are enabled
git config core.hooksPath
# Should be empty or point to .git/hooks
```

### Hook Blocking Valid Merge

```bash
# Temporary disable
mv .git/hooks/pre-merge-commit .git/hooks/pre-merge-commit.disabled

# Re-enable after merge
mv .git/hooks/pre-merge-commit.disabled .git/hooks/pre-merge-commit
```

### Hook Not Detecting PR Environment

```bash
# Check environment variables
env | grep -E 'CI|GITHUB|GITLAB'

# Manually set (for testing)
export GITHUB_ACTIONS=true
export GITHUB_EVENT_NAME=pull_request
```

## Best Practices

1. **Document exceptions**: Log all bypass usages
2. **Regular audits**: Review merge patterns monthly
3. **Team training**: Ensure all devs understand policies
4. **Gradual rollout**: Start permissive, tighten over time
5. **Clear communication**: Update team when policies change

## Additional Resources

- [Git Hooks Documentation](https://git-scm.com/docs/githooks)
- [GitHub Branch Protection](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/defining-the-mergeability-of-pull-requests/about-protected-branches)
- [GitLab Protected Branches](https://docs.gitlab.com/ee/user/project/protected_branches.html)

## Maintenance

### Update Hook Across Team

```bash
# Update tracked version
cp .git/hooks/pre-merge-commit .git-hooks/

# Commit and push
git add .git-hooks/pre-merge-commit
git commit -m "chore: update merge policy hook"
git push

# Team members update with
git pull
./install-hooks.sh
```

### Version History

- v1.0: Initial FF-only policy
- v1.1: Added PR environment detection
- v1.2: Added bypass flag support
- v2.0: Added multi-branch pattern support
