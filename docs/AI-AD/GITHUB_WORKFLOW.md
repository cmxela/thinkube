# GitHub Workflow for Thinkube

This document outlines how we use GitHub in the Thinkube project's AI-assisted development process.

## Branch Structure

- `main` - Stable, deployable code - protected branch
- `develop` - Integration branch for feature development
- `feature/[component-name]` - Feature branches for each component (e.g., `feature/lxd-setup`)
- `fix/[issue-number]` - Branches for bug fixes (e.g., `fix/42-ssh-permissions`)
- `docs/[topic]` - Documentation-only changes (e.g., `docs/networking`)

### Branch Naming Conventions

- Use lowercase and hyphens for branch names
- Keep branch names short but descriptive
- Include issue numbers for fix branches
- Component names should match directory names when possible

## Development Workflow

### 1. Repository Setup (One-time)

If you're setting up a new working environment:

```bash
# Clone the repository
git clone git@github.com:cmxela/thinkube.git
cd thinkube

# Set up remote tracking for develop branch
git checkout -b develop origin/develop

# Configure commit template (optional)
git config commit.template .github/commit-template.txt
```

### 2. Starting a New Feature

For each major component (e.g., lxd-setup, networking):

1. Ensure you have the latest develop branch:
   ```bash
   git checkout develop
   git pull origin develop
   ```

2. Create a feature branch:
   ```bash
   git checkout -b feature/lxd-setup
   ```

3. Setup branch tracking immediately:
   ```bash
   git push -u origin feature/lxd-setup
   ```

### 3. Incremental Development Cycle

Following the test-first approach, work in small increments:

1. Create or update test playbook first:
   ```bash
   # Edit test playbook
   nano ansible/20_lxd_setup/28_test_lxd_profiles.yaml
   
   # Run test (it should fail initially)
   ansible-playbook -i inventory/inventory.yaml ansible/20_lxd_setup/28_test_lxd_profiles.yaml
   ```

2. Implement the feature to make test pass:
   ```bash
   # Edit implementation playbook
   nano ansible/20_lxd_setup/20_setup_lxd_profiles.yaml
   
   # Run implementation
   ansible-playbook -i inventory/inventory.yaml ansible/20_lxd_setup/20_setup_lxd_profiles.yaml
   
   # Verify test now passes
   ansible-playbook -i inventory/inventory.yaml ansible/20_lxd_setup/28_test_lxd_profiles.yaml
   ```

3. Commit the changes when tests pass:
   ```bash
   git add ansible/20_lxd_setup/28_test_lxd_profiles.yaml
   git add ansible/20_lxd_setup/20_setup_lxd_profiles.yaml
   git commit -m "[LXD-Setup] Add vm-networks profile creation and testing"
   ```

4. Push changes regularly (at least daily):
   ```bash
   git push
   ```

### 4. Handling Simultaneous Features

If you need to work on multiple features concurrently:

```bash
# Save current work
git commit -m "[LXD-Setup] Checkpoint: profile configuration"
git push

# Switch to a different feature branch
git checkout develop
git pull
git checkout -b feature/networking
```

### 5. Pull Requests

When a feature is complete and all tests pass:

1. Prepare your branch for PR:
   ```bash
   # Rebase on latest develop to resolve any conflicts
   git checkout develop
   git pull
   git checkout feature/lxd-setup
   git rebase develop
   
   # Force push if you rebased (be careful!)
   git push --force-with-lease
   ```

2. Create a pull request to `develop`:

   **Option 1: Through GitHub interface:**
   - Use a clear title: "[Component] What was implemented"
   - Fill in the PR template

   **Option 2: Using GitHub CLI with temporary file:**
   ```bash
   # Create a temporary file with the PR description
   cat > /tmp/pr_body.md << 'EOL'
   ## Component Description
   Brief overview of the component and its purpose.

   ## Implemented Features
   - Feature 1: Description
   - Feature 2: Description

   ## Testing Performed
   - [ ] Test playbooks created and passing
   - [ ] Tested on fresh environment
   - [ ] Verified idempotence (can run multiple times)

   ## Documentation
   - [ ] Component README updated
   - [ ] Added to architecture docs if needed

   ## Screenshots
   Attach any relevant screenshots
   EOL

   # Create the PR using GitHub CLI
   source ~/.env
   GITHUB_TOKEN="$GITHUB_TOKEN" gh pr create \
     --title "[Component] What was implemented" \
     --body "$(cat /tmp/pr_body.md)" \
     --base develop \
     --draft  # Remove this flag for a ready PR
   ```

3. Comment on or update an existing PR:
   ```bash
   # Add a comment to a PR
   GITHUB_TOKEN="$GITHUB_TOKEN" gh pr comment 3 --body "Created issue #4 to track this item"

   # Update PR description using a temporary file
   cat > /tmp/updated_pr.md << 'EOL'
   ## Updated Component Description
   New content for PR body
   EOL

   GITHUB_TOKEN="$GITHUB_TOKEN" gh pr edit 3 --body "$(cat /tmp/updated_pr.md)"
   ```

### 6. Code Review

When reviewing PRs (human or AI-assisted review):

1. **Implementation Quality**:
   - Does each task follow the "fail fast" principle?
   - Are variable names consistent with our naming conventions?
   - Is error handling following our standards?

2. **Test Coverage**:
   - Do tests exist for all functionality?
   - Do tests verify both success and failure cases?
   - Are tests following our test-first approach?

3. **Documentation**:
   - Is the documentation clear and complete?
   - Are any architecture documents updated?
   - Are all required variables documented?

4. **Security and Best Practices**:
   - No hardcoded secrets
   - No overly permissive settings
   - No security anti-patterns

### 7. Merging

After approval:

1. Squash and merge the PR to `develop`:
   - Go to the PR on GitHub
   - Use "Squash and merge" option
   - Ensure the commit message properly summarizes the changes

2. Delete the feature branch after merging:
   ```bash
   # Locally
   git checkout develop
   git pull
   git branch -d feature/lxd-setup
   
   # On remote
   git push origin --delete feature/lxd-setup
   ```

### 8. Releases

When ready for a release:

1. Create a release branch:
   ```bash
   git checkout develop
   git pull
   git checkout -b release/v0.1.0
   ```

2. Final testing on release branch:
   ```bash
   # Run all test playbooks
   for test in $(find ansible -name "*test*.yaml"); do
     ansible-playbook -i inventory/inventory.yaml $test
   done
   ```

3. Create a PR from `release/v0.1.0` to `main`

4. After merging to main, tag the release:
   ```bash
   git checkout main
   git pull
   git tag -a v0.1.0 -m "Release v0.1.0: Initial LXD setup implementation"
   git push origin v0.1.0
   ```

## Commit Message Format

Structure commit messages using this format:

```
[Component] Brief description of the change

- Detailed bullet points about what changed
- Reference to tests that were added
```

Examples:
```
[LXD-Setup] Add vm-networks profile creation

- Add test for profile existence
- Implement profile creation task
- Include network device configuration
```

```
[Networking] Fix ZeroTier route configuration

- Update test to verify route creation
- Fix IP forwarding configuration
- Add validation for route existence
```

To make this easier, create a commit template:

```bash
mkdir -p .github
cat > .github/commit-template.txt << 'EOF'
[Component] Concise summary of changes

- Detail 1 of what changed
- Detail 2 of what changed
- Reference to tests (#issue if relevant)
EOF

git config commit.template .github/commit-template.txt
```

## Issue Management

### Creating Issues

1. Use GitHub Issues for tracking tasks, bugs, and features
2. Create an issue for each distinct component or bug
3. Include clear acceptance criteria in each issue

#### Creating Detailed Issues via CLI

For detailed issues with formatting, use the temporary file approach with GitHub CLI:

```bash
# 1. Create a temporary file with the issue description
cat > /tmp/issue_body.md << 'EOL'
## Problem Description

Detailed description of the issue using Markdown formatting.

### Steps to Reproduce
1. First step
2. Second step
3. Third step

### Expected Behavior
What should happen.

### Actual Behavior
What actually happens.

## Technical Details
```bash
# Example code or command output
```

## Proposed Solution
Detailed explanation of the solution.
EOL

# 2. Create the issue using the temporary file
source ~/.env  # Make sure GITHUB_TOKEN is available
GITHUB_TOKEN="$GITHUB_TOKEN" gh issue create \
  --title "Comprehensive issue title" \
  --body "$(cat /tmp/issue_body.md)" \
  --label "enhancement,bug"  # Comma-separated labels
```

This approach avoids issues with escaping special characters and command line limitations.

### Issue Structure

```markdown
## Description
Brief description of the issue or feature

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Tests created and passing

## Additional Context
Any relevant background information
```

### Issue Labels

Standardize issues with labels:

- `component:lxd` - Component-specific issues
- `component:networking` - Networking-related issues
- `bug` - Something isn't working
- `enhancement` - New feature or improvement
- `documentation` - Documentation-only changes
- `test` - Test-related changes
- `priority:high/medium/low` - Priority level
- `needs-physical-access` - Issues requiring physical server access

#### Creating Custom Labels

To create new labels for better categorization of issues:

```bash
# Create a new label via GitHub CLI
source ~/.env
GITHUB_TOKEN="$GITHUB_TOKEN" gh api \
  -X POST /repos/cmxela/thinkube/labels \
  -f name='needs-physical-access' \
  -f color='d73a4a' \
  -f description='Issues requiring physical access to hardware'

# Add a label to an existing issue
GITHUB_TOKEN="$GITHUB_TOKEN" gh issue edit 123 --add-label "needs-physical-access"
```

Common colors for labels:
- Red (#d73a4a): Urgent issues, bugs
- Orange (#e99695): Important tasks
- Yellow (#fbca04): Warnings, attention needed
- Green (#0e8a16): Ready, completed
- Blue (#1d76db): Information, documentation
- Purple (#5319e7): Enhancement, feature

## AI-Assisted Workflow Best Practices

### 1. Context Management

- Provide Claude with necessary context at the beginning of sessions
- Reference documentation links when starting a new session
- Keep file paths consistent with repository structure

### 2. Code Generation

- Request small, focused code segments instead of complete playbooks
- Specify adherence to our standards (variable naming, error handling)
- Review all generated code carefully before committing

### 3. Working with Tests

- Always ask Claude to generate the test first
- Verify tests fail initially and pass after implementation
- Break down complex playbooks into small testable sections

### 4. Commit Discipline

- Review all code before committing, even small changes
- Commit as soon as a test passes
- Keep commits focused on single functionality

### 5. Documentation

- Update documentation in the same PR as code changes
- Document complex decisions and design choices
- Keep READMEs and architecture docs in sync with implementation

## Maintaining Clean History

Occasionally cleanup your feature branch before submitting a PR:

```bash
# Squash multiple work-in-progress commits
git rebase -i HEAD~3  # Replace 3 with number of commits to consider

# Alternatively, reset and recommit for a clean history
git reset --soft HEAD~3  # Moves HEAD but keeps changes staged
git commit -m "[Component] Comprehensive commit message"
```