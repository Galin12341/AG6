# Git Rerere (Reuse Recorded Resolution) Demonstration

## What is Git Rerere?

**rerere** stands for "reuse recorded resolution". It's a Git feature that remembers how you resolved merge conflicts and automatically reapplies those resolutions when the same conflict appears again.

## Why Use Rerere?

### Common Scenarios

1. **Rebasing long-lived feature branches**: Resolve same conflicts repeatedly
2. **Cherry-picking commits**: Same changes cause same conflicts
3. **Complex merges with multiple attempts**: Try different merge strategies
4. **Testing integration**: Merge, test, abort, fix, merge again

### Benefits

- Saves time on repetitive conflict resolution
- Ensures consistent conflict resolution across attempts
- Enables confident merge/rebase experimentation

## Current Conflict Scenario

We have a merge conflict in `test_rerere.py`:
- Branch `rerere-py-1`: Contains `greet()` printing "Hello from branch 1"
- Branch being merged: Contains `greet()` printing "Hello from branch 2"

Both branches added the same function with different implementations (both added conflict).

## Rerere Status Check

```bash
# Check if rerere is enabled
$ git config rerere.enabled
true

# Check current rerere state
$ git rerere status
test_rerere.py

# View what rerere knows about conflicts
$ git rerere diff
```

## Step-by-Step Demonstration

### Step 1: Current Conflict State

```bash
$ git status
On branch rerere-py-1
You have unmerged paths.
  (fix conflicts and run "git commit")

Unmerged paths:
	both added:      test_rerere.py
```

### Step 2: Resolve the Conflict

We'll resolve by keeping both functions with different names:

```python
def greet_branch1():
    print("Hello from branch 1")

def greet_branch2():
    print("Hello from branch 2")

def greet():
    greet_branch1()
    greet_branch2()
```

When we resolve and commit, rerere records this resolution automatically.

### Step 3: Rerere Records the Resolution

After resolving:
```bash
$ git add test_rerere.py
$ git commit -m "Resolve: merge both greet functions"

# Rerere has now recorded this resolution in:
# .git/rr-cache/<conflict-sha>/
```

### Step 4: Simulate Same Conflict Again

```bash
# Abort current merge to test rerere
$ git reset --hard HEAD~1

# Re-do the merge
$ git merge branch-2

# Rerere automatically applies previous resolution!
Merge conflict in test_rerere.py
Resolved 'test_rerere.py' using previous resolution.
```

## Rerere Storage

Rerere stores resolutions in `.git/rr-cache/`:

```
.git/rr-cache/
└── <sha-of-conflict>/
    ├── preimage     # The conflict markers
    └── postimage    # The resolved version
```

## Advanced Rerere Commands

### View Rerere Status
```bash
# Show files with recorded resolutions
git rerere status

# Show diff of recorded resolutions
git rerere diff

# Show what rerere would apply
git rerere diff --cached
```

### Manage Rerere Cache

```bash
# Forget resolution for specific file
git rerere forget test_rerere.py

# Clear old unused resolutions (default: 60 days old)
git rerere gc

# Clear all rerere cache
git rerere clear
```

### Rerere Configuration

```bash
# Enable rerere globally
git config --global rerere.enabled true

# Auto-stage files resolved by rerere
git config --global rerere.autoupdate true

# Set cache expiration (default: 60 days)
git config --global gc.rerereResolved 90

# Keep unresolved conflicts longer (default: 15 days)
git config --global gc.rerereUnresolved 30
```

## Practical Workflow Example

### Scenario: Long-Lived Feature Branch

```bash
# Initial rebase causes conflicts
git rebase main
# ... resolve conflicts manually ...
git add .
git rebase --continue

# Later, need to rebase again
git rebase main
# Rerere auto-applies previous resolutions!
# Only new conflicts need manual resolution
```

### Scenario: Testing Different Merge Strategies

```bash
# Try merge strategy 1
git merge --no-ff feature-branch
# ... resolve conflicts ...
git add .
git commit

# Not satisfied, try different approach
git reset --hard HEAD~1

# Try merge strategy 2 (squash)
git merge --squash feature-branch
# Rerere auto-applies same conflict resolutions
# Only new conflicts need resolution
```

## Rerere with Autoupdate

Enable autoupdate to automatically stage resolved files:

```bash
git config rerere.autoupdate true

# Now when rerere resolves conflicts:
git merge feature-branch
Resolved 'file.py' using previous resolution.
# file.py is automatically staged!
```

## When Rerere Doesn't Help

Rerere won't help in these situations:

1. **Context changed**: Surrounding code changed significantly
2. **First occurrence**: No previous resolution recorded
3. **Different conflict**: Similar but not identical conflict
4. **Manual conflict markers**: Hand-edited conflict markers

## Real Team Application

### Use Case: Release Branch Maintenance

```bash
# Feature merged to main
git checkout main
git merge feature-x  # conflicts resolved

# Need same feature on release branch
git checkout release-1.0
git cherry-pick feature-x
# Rerere automatically applies same resolution!
```

### Use Case: Rebasing Multiple Feature Branches

Team has 3 feature branches, all conflicting with main:

```bash
# Branch A rebases first
git checkout feature-a
git rebase main
# ... resolve conflicts for shared.py ...

# Branch B rebases
git checkout feature-b
git rebase main
# Rerere auto-resolves shared.py if same conflict!

# Branch C rebases
git checkout feature-c
git rebase main
# Rerere auto-resolves shared.py again!
```

## Troubleshooting

### Rerere Applied Wrong Resolution

```bash
# Abort the operation
git merge --abort  # or git rebase --abort

# Forget the bad resolution
git rerere forget file.py

# Redo with correct resolution
git merge branch
# ... resolve correctly ...
```

### Check What Rerere Knows

```bash
# List all recorded resolutions
ls .git/rr-cache/

# View specific resolution
cat .git/rr-cache/<sha>/postimage
```

### Rerere Not Working

```bash
# Verify rerere is enabled
git config rerere.enabled
# Should output: true

# Check rerere status during conflict
git rerere status
# Should list conflicted files

# Manually trigger rerere
git rerere
```

## Best Practices

1. **Enable globally**: `git config --global rerere.enabled true`
2. **Use with autoupdate**: Auto-stage resolved files
3. **Verify resolutions**: Don't blindly trust rerere, review changes
4. **Clear periodically**: Use `git rerere gc` to clean old resolutions
5. **Document resolutions**: Complex resolutions deserve commit message notes

## Integration with CI/CD

Rerere doesn't affect CI/CD directly, but enables:
- **Faster rebases**: Auto-resolution speeds up branch updates
- **Confident refactoring**: Try merges without fear
- **Hotfix workflows**: Cherry-pick with auto-resolution

## Limitations

- **File-level only**: Doesn't resolve semantic conflicts
- **Exact match required**: Different context = no match
- **Local only**: Not shared across team (each dev builds own cache)
- **No version control**: Resolutions not tracked in repo

## Sharing Rerere Resolutions (Advanced)

While rerere is local, you can share resolutions:

```bash
# Export rerere database
tar czf rerere-cache.tar.gz .git/rr-cache/

# Team member imports
tar xzf rerere-cache.tar.gz -C .git/
```

**Warning**: Only share within trusted team, resolutions may be context-specific.

## Conclusion

Git rerere is a powerful tool for:
- Reducing repetitive conflict resolution
- Enabling confident merge experimentation
- Speeding up rebase workflows

**Enable it today**: `git config --global rerere.enabled true`

Most developers enable and forget about rerere - it silently works in the background, saving time when you need it most.
