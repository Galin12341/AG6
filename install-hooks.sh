#!/bin/bash
# Git Hooks Installation Script
# Installs pre-merge-commit hook and other policy enforcement hooks

set -e

HOOKS_DIR=".git/hooks"
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "=== Git Hooks Installation ==="
echo ""

# Check if in git repository
if [ ! -d ".git" ]; then
    echo -e "${RED}Error: Not in a git repository${NC}"
    echo "Please run this script from the repository root"
    exit 1
fi

# Create hooks directory if it doesn't exist
mkdir -p "$HOOKS_DIR"

# Create .git-hooks directory for tracked hooks
mkdir -p .git-hooks

# Install pre-merge-commit hook
HOOK_FILE="$HOOKS_DIR/pre-merge-commit"

cat > "$HOOK_FILE" << 'EOF'
#!/bin/bash
# Git Hook: pre-merge-commit
# Prevents non-fast-forward merges to protected branches outside of PRs

PROTECTED_BRANCHES=("main" "master" "develop" "release/*")
REQUIRE_FF_ONLY=true
ALLOW_SQUASH=true
REQUIRE_PR_ENVIRONMENT=true

RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m'

CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

is_protected_branch() {
    local branch=$1
    for pattern in "${PROTECTED_BRANCHES[@]}"; do
        if [[ $branch == $pattern ]]; then
            return 0
        fi
    done
    return 1
}

is_pr_environment() {
    if [[ -n "$GITHUB_ACTIONS" && -n "$GITHUB_EVENT_NAME" ]]; then
        if [[ "$GITHUB_EVENT_NAME" == "pull_request" ]]; then
            return 0
        fi
    fi
    if [[ -n "$CI_MERGE_REQUEST_ID" ]]; then
        return 0
    fi
    if [[ -n "$CHANGE_ID" ]]; then
        return 0
    fi
    if [[ -n "$CI" || -n "$CONTINUOUS_INTEGRATION" ]]; then
        return 0
    fi
    return 1
}

is_fast_forward() {
    if [[ ! -f .git/MERGE_HEAD ]]; then
        return 1
    fi
    MERGE_HEAD=$(cat .git/MERGE_HEAD)
    MERGE_BASE=$(git merge-base HEAD "$MERGE_HEAD")
    if [[ "$MERGE_BASE" == "$(git rev-parse HEAD)" ]]; then
        return 0
    fi
    return 1
}

echo -e "${YELLOW}[Policy Check] Validating merge policy...${NC}"

if ! is_protected_branch "$CURRENT_BRANCH"; then
    echo -e "${GREEN}[Policy Check] ✓ Branch '$CURRENT_BRANCH' not protected. Merge allowed.${NC}"
    exit 0
fi

echo -e "${YELLOW}[Policy Check] Protected branch detected: $CURRENT_BRANCH${NC}"

if [[ "$REQUIRE_PR_ENVIRONMENT" == "true" ]]; then
    if ! is_pr_environment; then
        echo -e "${RED}[Policy Check] ✗ Direct merges to '$CURRENT_BRANCH' not allowed outside PR environment.${NC}"
        echo ""
        echo "Policy: Protected branches must be merged via Pull Request"
        echo ""
        echo "Allowed methods:"
        echo "  1. Create a PR on GitHub/GitLab"
        echo "  2. Use 'git request-pull' for code review"
        echo "  3. Bypass (if authorized): GIT_MERGE_ALLOW_DIRECT=1 git merge ..."
        echo ""
        if [[ "$GIT_MERGE_ALLOW_DIRECT" == "1" ]]; then
            echo -e "${YELLOW}[Policy Check] ⚠ Bypass flag detected. Allowing merge.${NC}"
            exit 0
        fi
        exit 1
    fi
fi

if [[ "$REQUIRE_FF_ONLY" == "true" ]]; then
    if ! is_fast_forward; then
        echo -e "${RED}[Policy Check] ✗ Non-fast-forward merge detected.${NC}"
        echo ""
        echo "Policy: '$CURRENT_BRANCH' requires fast-forward merges only"
        echo ""
        echo "This ensures:"
        echo "  - Linear history for easier bisecting"
        echo "  - Clear commit boundaries"
        echo "  - Simplified reverts"
        echo ""
        echo "Solutions:"
        echo "  1. Rebase your branch: git rebase $CURRENT_BRANCH feature-branch"
        echo "  2. Use --squash: git merge --squash feature-branch"
        echo ""
        exit 1
    fi
fi

echo -e "${GREEN}[Policy Check] ✓ Merge policy satisfied. Proceeding...${NC}"
exit 0
EOF

chmod +x "$HOOK_FILE"
echo -e "${GREEN}✓ Installed: pre-merge-commit${NC}"

# Copy to tracked directory
cp "$HOOK_FILE" .git-hooks/
echo -e "${GREEN}✓ Backed up to .git-hooks/${NC}"

# Create pre-push hook for additional checks
PREPUSH_FILE="$HOOKS_DIR/pre-push"

cat > "$PREPUSH_FILE" << 'EOF'
#!/bin/bash
# Git Hook: pre-push
# Additional checks before pushing

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}[Pre-Push Check] Validating push...${NC}"

# Check for debug statements
if git diff HEAD --cached | grep -E "console\.log|debugger|pdb\.set_trace|print\(\"DEBUG"; then
    echo -e "${YELLOW}⚠ Warning: Debug statements detected in commit${NC}"
    echo "Consider removing before pushing to shared branches"
fi

echo -e "${GREEN}✓ Pre-push checks passed${NC}"
exit 0
EOF

chmod +x "$PREPUSH_FILE"
echo -e "${GREEN}✓ Installed: pre-push${NC}"

# Summary
echo ""
echo "=== Installation Complete ==="
echo ""
echo "Installed hooks:"
echo "  • pre-merge-commit - Enforces merge policies"
echo "  • pre-push - Warns about debug code"
echo ""
echo "Configuration:"
echo "  • Protected branches: main, master, develop, release/*"
echo "  • Fast-forward only: enabled"
echo "  • PR requirement: enabled"
echo ""
echo "To customize, edit: $HOOKS_DIR/pre-merge-commit"
echo "Documentation: GIT_HOOKS_POLICY.md"
echo ""
echo -e "${GREEN}Git hooks are now active!${NC}"
