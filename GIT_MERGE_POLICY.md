# Git Merge Strategy Policy & Recommendations

## Executive Summary

This document outlines merge strategy recommendations for team collaboration, analyzing trade-offs across three critical dimensions: **auditability**, **bisectability**, and **revert risk**.

## Merge Strategy Comparison

### 1. Merge Commits (Default `git merge`)

**Strategy**: Creates a merge commit with two parents, preserving both branch histories.

```bash
git merge feature-branch
```

**Pros**:
- **Auditability**: ★★★★★ Excellent - Complete history of when/how features were integrated
- **Bisectability**: ★★★☆☆ Good - Can bisect, but may hit merge commits
- **Revert Risk**: ★★★★☆ Low - Easy to revert entire feature with `git revert -m`

**Cons**:
- History can become cluttered with many merge commits
- Graph visualization becomes complex in active repositories

**Best for**:
- Long-lived feature branches
- Teams needing full audit trails for compliance
- Projects where knowing "when" a feature merged matters

### 2. Squash Merge

**Strategy**: Combines all commits from feature branch into a single commit on main.

```bash
git merge --squash feature-branch
git commit -m "feat: complete feature description"
```

**Pros**:
- **Auditability**: ★★★☆☆ Moderate - Clear feature boundaries, but lose individual commit context
- **Bisectability**: ★★★★★ Excellent - Each commit on main is a complete, tested feature
- **Revert Risk**: ★★★★★ Lowest - Single commit revert, clean rollback

**Cons**:
- Loses granular development history
- Author attribution for individual commits lost
- Cannot cherry-pick specific sub-changes

**Best for**:
- Public-facing main branch with clean history
- Features developed with many WIP commits
- Teams using PRs as the unit of change

### 3. Rebase and Fast-Forward

**Strategy**: Replays feature commits on top of main, then fast-forwards.

```bash
git checkout feature-branch
git rebase main
git checkout main
git merge --ff-only feature-branch
```

**Pros**:
- **Auditability**: ★★★★☆ Good - Linear history, all commits visible
- **Bisectability**: ★★★★★ Excellent - Clean linear history, easy to bisect
- **Revert Risk**: ★★☆☆☆ Higher - Must revert multiple commits in reverse order

**Cons**:
- Rewrites commit history (changes SHAs)
- Dangerous for shared/published branches
- Harder to see when features were integrated

**Best for**:
- Small teams with disciplined workflows
- Repositories prioritizing linear history
- Feature branches with clean, atomic commits

### 4. Fast-Forward Only (No Merge Commits)

**Strategy**: Only allow merges that can fast-forward, enforcing rebase workflow.

```bash
git merge --ff-only feature-branch
```

**Pros**:
- **Auditability**: ★★★☆☆ Moderate - Linear but loses integration context
- **Bisectability**: ★★★★★ Excellent - Simplest to bisect
- **Revert Risk**: ★★☆☆☆ Higher - No merge commit to revert

**Cons**:
- Requires rebasing before every merge
- Loses information about branch integration points
- Can be disruptive for long-running features

**Best for**:
- Trunk-based development
- Continuous integration workflows
- Small, frequent changes

## Real Team Scenarios & Recommendations

### Scenario 1: Financial Services / Regulated Industry

**Requirements**:
- Full audit trail for compliance
- Need to prove when code entered production branch
- Occasional need to remove specific features quickly

**Recommended Strategy**: **Merge Commits**

**Configuration**:
```bash
git config merge.ff false  # Require merge commits
```

**Rationale**:
- Compliance requires knowing exactly when code merged
- Merge commits provide revert points for emergency rollbacks
- Trade-off: More complex history is acceptable for auditability

### Scenario 2: Open Source Project with External Contributors

**Requirements**:
- Clean, understandable history for newcomers
- Features should be atomic units
- Need to revert incomplete features easily

**Recommended Strategy**: **Squash Merge** (GitHub PR default)

**GitHub Settings**:
- Enable: "Allow squash merging"
- Disable: "Allow merge commits" (optional)
- Require: PR review before merge

**Rationale**:
- External contributors may have messy commit history
- Maintainers control final commit message
- Easy feature revert reduces risk of accepting contributions

### Scenario 3: Startup with Fast Iteration

**Requirements**:
- Deploy multiple times per day
- Quick bisect capability when bugs appear
- Small, incremental changes

**Recommended Strategy**: **Rebase + Fast-Forward**

**Configuration**:
```bash
git config merge.ff only  # Enforce FF-only
```

**Workflow**:
```bash
# Developer workflow
git fetch origin
git rebase origin/main
git push --force-with-lease

# Integration (automatic via CI)
git merge --ff-only feature-branch
```

**Rationale**:
- Linear history simplifies debugging
- Fast iteration needs quick bisect
- Trade-off: Team must be disciplined with rebasing

### Scenario 4: Enterprise Monorepo with Multiple Teams

**Requirements**:
- Multiple teams working independently
- Need to track which team contributed what
- Must support parallel development

**Recommended Strategy**: **Hybrid - Merge Commits + Squash**

**Policy**:
- Feature branches: Squash merge to team branch
- Team branches: Merge commit to main
- Hotfixes: Direct merge commit to main

**Rationale**:
- Team boundaries remain visible in history
- Feature complexity hidden within team branches
- Balance between clean history and auditability

## Revert Risk Analysis

### Low Risk (Easy to Revert)

1. **Squash merge**: `git revert <commit-sha>`
2. **Merge commit**: `git revert -m 1 <merge-sha>`

### Medium Risk (Multiple Steps)

3. **Rebased branch**: Must identify and revert all commits
```bash
git revert <commit-n>..<commit-1>
```

### High Risk (Complex Recovery)

4. **Interactive rebase history**: May need to recreate work
5. **Force-pushed branches**: Requires reflog recovery

## Bisectability Considerations

### Best for Bisecting

1. **Squash merge**: Each main commit is a complete, tested feature
2. **Rebase + FF**: Linear history, no merge commits to skip

```bash
git bisect start
git bisect bad HEAD
git bisect good v1.0.0
# Bisect will test each commit efficiently
```

### Requires Extra Flags

3. **Merge commits**: Use `--first-parent` to stay on main branch
```bash
git bisect start --first-parent
```

## Auditability Requirements

### High Auditability Needs

**Use Merge Commits When**:
- Regulatory compliance required (SOX, HIPAA, PCI-DSS)
- Need to prove code review happened at integration time
- Legal requirement to preserve author timestamps

### Moderate Auditability

**Use Squash Merge When**:
- Feature-level tracking sufficient
- PR review process documented externally (GitHub)
- Original branch history preserved in PR

## Recommended Policies by Team Size

### Small Team (2-5 developers)
- **Strategy**: Rebase + Fast-Forward
- **Rationale**: Simplicity, easy coordination
- **Tools**: Pre-push hooks to prevent direct main commits

### Medium Team (6-20 developers)
- **Strategy**: Squash Merge via PRs
- **Rationale**: Balance of clean history and safety
- **Tools**: CI checks, PR templates, branch protection

### Large Team (20+ developers)
- **Strategy**: Merge Commits with structured workflow
- **Rationale**: Full auditability, clear team boundaries
- **Tools**: CODEOWNERS, required reviews, automated merge queues

## Implementation Checklist

- [ ] Document chosen strategy in CONTRIBUTING.md
- [ ] Configure git config defaults for team
- [ ] Set up branch protection rules
- [ ] Create pre-merge CI checks (tests, lint, format)
- [ ] Train team on revert procedures
- [ ] Establish emergency hotfix process
- [ ] Set up monitoring for merge conflicts
- [ ] Document bisect procedures for incidents

## Tools to Enforce Policy

### Pre-Receive Hook (Server-Side)
```bash
# Prevent non-FF merges on protected branches
# See: GIT_HOOKS_POLICY.sh
```

### GitHub Branch Protection
- Require PR reviews
- Require status checks
- Require linear history (FF-only)
- Restrict who can push

### GitLab Merge Request Settings
- Merge method: Squash/Merge/Rebase
- Fast-forward merge only
- Remove source branch after merge

## Conclusion

No single merge strategy is optimal for all scenarios. Consider:

1. **Regulatory environment** → Merge commits for audit trails
2. **Team size** → Squash for medium/large, rebase for small
3. **Release frequency** → Squash for daily deploys, merge for infrequent
4. **Risk tolerance** → Squash for easiest reverts
5. **History importance** → Merge for full history, squash for clean history

**Action Item**: Evaluate your team's priorities on the auditability-bisectability-revert risk triangle and choose accordingly.
