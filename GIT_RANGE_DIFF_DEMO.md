# Git Range-Diff Demonstration

## What is Git Range-Diff?

`git range-diff` compares two versions of a patch series, showing what changed between iterations. It's essential for code review when branches are rebased or amended.

## Why Use Range-Diff?

### Common Scenarios

1. **PR iterations**: Compare v1 vs v2 of a pull request after addressing review comments
2. **Rebase review**: See what changed during an interactive rebase
3. **Cherry-pick verification**: Ensure cherry-picked commits match originals
4. **Force-push review**: Understand what changed after a force-push

### Problems It Solves

**Without range-diff**:
- "What changed since the last review?" - unclear
- Force-pushes hide the delta between iterations
- Reviewers must re-review entire PR

**With range-diff**:
- See exactly what changed between PR v1 and v2
- Reviewers focus only on new changes
- Transparent history despite rebases

## Basic Syntax

```bash
# Compare two ranges
git range-diff <old-base>..<old-tip> <new-base>..<new-tip>

# Compare branch iterations
git range-diff main..feature-v1 main..feature-v2

# Using three-dot notation (common ancestor)
git range-diff main...feature-v1 main...feature-v2
```

## Real Example from This Repository

### Scenario: Comparing Two Feature Branch Versions

```bash
# We have two versions of the rerere feature
git log --oneline rerere-py-1
git log --oneline rerere-py-2

# Compare them
git range-diff main..rerere-py-1 main..rerere-py-2
```

### Output Interpretation

```
1:  de241c0 = 1:  de241c0 Add greet function - branch 1
2:  a0c759f ! 2:  xxxxxx Add greet function - branch 2
    @@ test_rerere.py
    -print("Hello from branch 2")
    +print("Greetings from branch 2")
3:  -:  ------- Remove: old debug code
-:  xxxxxx > 3:  New feature added
```

**Legend**:
- `=` : Commits are identical
- `!` : Commits differ (shows diff of diffs)
- `<` : Commit only in old version
- `>` : Commit only in new version

## Detailed Example: PR Iteration Workflow

### Initial PR (v1)

```bash
git checkout -b feature-auth-v1 main
# ... make 3 commits ...
git push origin feature-auth-v1
```

**Commits**:
1. Add user model
2. Add authentication logic
3. Add login endpoint

### After Code Review (v2)

Reviewer requests changes:
- Fix typo in user model
- Add password hashing
- Add tests for login

```bash
# Rebase and modify commits
git checkout -b feature-auth-v2 feature-auth-v1
git rebase -i main

# Make changes and force-push
git push origin feature-auth-v2 --force-with-lease
```

### Comparing Iterations

```bash
git range-diff main..feature-auth-v1 main..feature-auth-v2
```

**Output**:
```
1:  abc1234 ! 1:  def5678 Add user model
    @@ Commit message
     Add user model
    +
    +Fix typo in username field

    @@ models/user.py
    -usrename = Column(String)
    +username = Column(String)

2:  abc2345 ! 2:  def6789 Add authentication logic
    @@ Commit message
     Add authentication logic
    +
    +Add bcrypt password hashing

    @@ auth/login.py
    +import bcrypt
    +hash = bcrypt.hashpw(password, salt)

3:  abc3456 = 3:  def7890 Add login endpoint

-:  ------- > 4:  def8901 Add login endpoint tests
```

**Insights**:
- Commit 1: Typo fixed in user model
- Commit 2: Password hashing added
- Commit 3: Unchanged
- Commit 4: New test commit added

## Advanced Usage

### 1. Compare with Custom Base

```bash
# Compare against different base branches
git range-diff origin/main..feature-v1 origin/develop..feature-v2
```

### 2. Creation Factor (Fuzzy Matching)

```bash
# Adjust how similar commits must be to match (default: 60)
git range-diff --creation-factor=80 main..v1 main..v2

# 100 = exact match only
# 50 = loose matching (more false positives)
```

### 3. Diff Options

```bash
# Show full context
git range-diff -U10 main..v1 main..v2

# Ignore whitespace
git range-diff -w main..v1 main..v2

# Color output (default on terminal)
git range-diff --color main..v1 main..v2
```

### 4. Format Output

```bash
# Machine-readable format
git range-diff --no-color main..v1 main..v2 > pr-changes.txt

# Focus on specific files
git range-diff main..v1 main..v2 -- src/*.py
```

## Practical Workflows

### Workflow 1: Transparent Rebase

```bash
# Before rebase: tag current state
git tag pr-v1

# Rebase and address comments
git rebase -i main
# ... make changes ...
git push --force-with-lease

# Show reviewers what changed
git range-diff main..pr-v1 main..HEAD
```

### Workflow 2: Squash vs Individual Fixes

**Option A: Squash fixes into original commits**
```bash
git rebase -i main
# fixup! commits into originals
```

**Option B: Keep fixes as separate commits**
```bash
git commit -m "fixup: address review comments"
```

**Use range-diff to decide**:
```bash
# See which approach is cleaner
git range-diff main..original main..squashed
git range-diff main..original main..with-fixups
```

### Workflow 3: Cherry-Pick Verification

```bash
# Cherry-pick feature to release branch
git checkout release-1.0
git cherry-pick feature-commit-1 feature-commit-2

# Verify cherry-pick matches original
git range-diff main..feature release-1.0..HEAD
# Should show '=' for all commits if perfect
```

## Integration with PR Reviews

### GitHub PR Comment Template

```markdown
## Changes in v2

Review focus areas:

<summary>
<details>
<summary>Full range-diff</summary>

```
$ git range-diff main..pr-v1 main..pr-v2
[paste output here]
```
</details>
```

### GitLab MR Description

```markdown
## Iteration Changes

**v1 → v2**:
- Fixed password hashing (commit 2)
- Added tests (new commit 4)
- Typo fix (commit 1)

<details>
<summary>Range-diff output</summary>

```bash
git range-diff origin/main...v1 origin/main...v2
```
</details>
```

## Comparison with Other Tools

### range-diff vs diff

```bash
# diff: compares final states only
git diff feature-v1 feature-v2
# "What's different between branch tips?"

# range-diff: compares commit series
git range-diff main..feature-v1 main..feature-v2
# "What changed in each individual commit?"
```

### range-diff vs log

```bash
# log: shows commits in one branch
git log main..feature-v2

# range-diff: compares two series of commits
git range-diff main..v1 main..v2
```

## Real-World Examples

### Example 1: Addressing Review Comments

**Before** (3 commits):
1. Add feature X
2. Add tests for X
3. Update docs for X

**After** (3 commits):
1. Add feature X (fixed bug reviewer found)
2. Add tests for X (added edge case)
3. Update docs for X (clarified wording)

```bash
$ git range-diff origin/main..pr-v1 origin/main..pr-v2

1:  abc1234 ! 1:  def5678 Add feature X
    @@ src/feature.py: def feature_x():
    +# Fixed: null pointer when input empty
    +if not input:
    +    return None

2:  abc2345 ! 2:  def6789 Add tests for X
    @@ tests/test_feature.py: test suite
    +def test_feature_x_empty_input():
    +    assert feature_x("") is None

3:  abc3456 ! 3:  def7890 Update docs for X
    @@ docs/api.md: API Reference
    -Returns result
    +Returns result or None if input empty
```

### Example 2: Splitting a Large Commit

**Before** (1 commit):
1. Refactor authentication system (500 lines)

**After** (3 commits):
1. Extract authentication logic
2. Add password hashing
3. Update tests

```bash
$ git range-diff main..before-split main..after-split

1:  abc1234 < -:  ------- Refactor authentication system
-:  ------- > 1:  def5678 Extract authentication logic
-:  ------- > 2:  def6789 Add password hashing
-:  ------- > 3:  def7890 Update tests
```

## Common Pitfalls

### 1. Wrong Base Branch

```bash
# ❌ Wrong: comparing against different bases
git range-diff origin/main..v1 origin/develop..v2

# ✅ Correct: same base for both
git range-diff origin/main..v1 origin/main..v2
```

### 2. Comparing Unrelated Branches

```bash
# ❌ Wrong: completely different feature branches
git range-diff main..feature-a main..feature-b
# Results will be confusing

# ✅ Correct: different iterations of same feature
git range-diff main..feature-v1 main..feature-v2
```

### 3. Too Many Commits

```bash
# ❌ Hard to read: 50 commits vs 50 commits
git range-diff main..huge-v1 main..huge-v2

# ✅ Better: break into logical sections
git range-diff main..phase1-v1 main..phase1-v2
git range-diff phase1..phase2-v1 phase1..phase2-v2
```

## Tips for Effective Use

1. **Tag iterations**: `git tag pr-v1` before rebasing
2. **Document in PR**: Paste range-diff in PR description
3. **Focus reviews**: Reviewers can focus on changed commits only
4. **Adjust creation-factor**: Use `--creation-factor=70` if commits heavily modified
5. **Use with rebase**: Always run range-diff after interactive rebase

## CI/CD Integration

### Pre-Push Hook

```bash
#!/bin/bash
# .git/hooks/pre-push

# If force-pushing, require range-diff review
if [[ $FORCE_PUSH ]]; then
    echo "Force push detected. Generating range-diff..."
    git range-diff origin/main..origin/feature origin/main..feature
    read -p "Proceed with force push? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi
```

### GitHub Actions

```yaml
name: PR Iteration Diff

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  range-diff:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0

      - name: Generate range-diff
        if: github.event.before != '0000000000000000000000000000000000000000'
        run: |
          echo "## Range Diff" >> $GITHUB_STEP_SUMMARY
          echo '```' >> $GITHUB_STEP_SUMMARY
          git range-diff ${{ github.event.before }}..HEAD origin/main..HEAD || echo "First push"
          echo '```' >> $GITHUB_STEP_SUMMARY
```

## Conclusion

Git range-diff is essential for:
- **Transparent rebases**: Show exactly what changed
- **Efficient reviews**: Focus on new changes only
- **Quality control**: Verify cherry-picks and rebases
- **Team communication**: Clear iteration documentation

**When to use**:
- After addressing PR review comments
- After rebasing feature branch
- When splitting/combining commits
- Before force-pushing

**Best practice**: Always run range-diff before force-pushing to shared branches.

## Quick Reference

```bash
# Basic comparison
git range-diff A..B A..C

# With three-dot (common ancestor)
git range-diff A...B A...C

# Tagged iterations
git range-diff v1..v1-tip v2..v2-tip

# Adjust matching sensitivity
git range-diff --creation-factor=80 A..B A..C

# Ignore whitespace
git range-diff -w A..B A..C

# Focus on specific files
git range-diff A..B A..C -- src/
```
