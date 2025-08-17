# uDOS Git Integration with SSH Key Support

**Version:** uDOS v1.3 with Git Dev Mode Integration  
**Location:** sandbox/user/.ssh  
**Mode:** Dev Mode Only (requires wizard folder)  

## 🎯 Overview

uDOS now includes comprehensive Git integration with SSH key management specifically designed for Dev Mode operations. All SSH keys are stored in the sandbox/user/.ssh directory for security and isolation.

## 🔑 SSH Key Management

### Generate New SSH Key
```bash
SSH-KEY GENERATE [key_name]
```
- Creates a new RSA 4096-bit SSH key pair
- Default name: `id_rsa`
- Keys stored in: `sandbox/user/.ssh/`
- Automatically sets proper permissions (600 for private, 644 for public)

### List SSH Keys
```bash
SSH-KEY LIST
```
- Shows all SSH keys in sandbox/user/.ssh
- Displays both private and public key pairs

### Add Key to SSH Agent
```bash
SSH-KEY ADD [key_name]
```
- Adds SSH key to the current SSH agent
- Default: `id_rsa`

### Test SSH Connection
```bash
SSH-KEY TEST [host]
```
- Tests SSH connection to specified host
- Default: `git@github.com`
- Useful for verifying GitHub/GitLab access

### Remove SSH Key
```bash
SSH-KEY REMOVE <key_name>
```
- Safely removes SSH key pair
- Prompts for confirmation

## 🔄 Git Operations

### Basic Git Commands
```bash
GIT STATUS              # Show repository status
GIT LOG                 # Show recent commits
GIT DIFF                # Show changes
GIT ADD <files>         # Stage files
```

### Repository Operations
```bash
CLONE <repo_url> [dir]          # Clone repository with SSH support
PUSH [remote] [branch]          # Push with SSH authentication
PULL [remote] [branch]          # Pull with SSH authentication
```

### Commit Operations
```bash
COMMIT "message"                # Create commit with message
COMMIT "message" -a             # Commit all tracked changes
COMMIT "message" --amend        # Amend previous commit
```

### Branch Management
```bash
BRANCH                          # List branches
BRANCH LIST                     # List all branches (local + remote)
BRANCH CREATE <name>            # Create and switch to new branch
BRANCH SWITCH <name>            # Switch to existing branch
BRANCH DELETE <name>            # Delete branch
```

### Advanced Operations
```bash
MERGE <branch>                  # Merge branch into current
REBASE <branch>                 # Rebase current branch onto target
STASH                           # Stash current changes
STASH POP                       # Apply most recent stash
STASH LIST                      # List all stashes
```

### Remote Management
```bash
REMOTE                          # List remotes
REMOTE ADD <name> <url>         # Add remote repository
REMOTE REMOVE <name>            # Remove remote
REMOTE SET-URL <name> <url>     # Update remote URL
```

## 🚀 Quick Setup Guide

### 1. Generate SSH Key
```bash
# Generate default SSH key
SSH-KEY GENERATE

# Or generate with custom name
SSH-KEY GENERATE my_github_key
```

### 2. Add Public Key to Git Service
```bash
# View your public key
SSH-KEY LIST

# Copy the .pub key content to GitHub/GitLab/etc
```

### 3. Test Connection
```bash
# Test GitHub connection
SSH-KEY TEST git@github.com

# Test GitLab connection  
SSH-KEY TEST git@gitlab.com
```

### 4. Clone and Work
```bash
# Clone repository
CLONE git@github.com:username/repo.git

# Make changes, then commit and push
GIT ADD .
COMMIT "feat: add new feature"
PUSH
```

## 📁 Directory Structure

```
sandbox/user/
├── .ssh/                       # SSH keys directory
│   ├── id_rsa                  # Private key (600 permissions)
│   ├── id_rsa.pub              # Public key (644 permissions)
│   ├── my_github_key           # Custom private key
│   └── my_github_key.pub       # Custom public key
└── README.md                   # This file
```

## 🔒 Security Features

### Automatic SSH Agent Setup
- SSH agent automatically started when needed
- Keys automatically loaded for Git operations
- Agent session isolated to current uDOS session

### Secure Key Storage
- Keys stored in user sandbox (not system-wide)
- Proper permissions automatically set
- Keys only accessible in Dev Mode

### Safe Operations
- Confirmation prompts for destructive operations
- Clear success/error messages
- Operation logging for audit trail

## 🎮 Example Workflows

### New Project Setup
```bash
# Generate SSH key for new project
SSH-KEY GENERATE project_key

# Add public key to Git service
SSH-KEY LIST

# Clone your repository
CLONE git@github.com:user/project.git

# Work on feature
BRANCH CREATE feature-x
# ... make changes ...
GIT ADD .
COMMIT "feat: implement feature x"
PUSH -u origin feature-x
```

### Daily Development
```bash
# Start work session
PULL origin main
BRANCH CREATE daily-work

# Work and commit
GIT ADD .
COMMIT "fix: resolve bug #123"

# Update and merge
BRANCH SWITCH main
PULL origin main
MERGE daily-work
PUSH origin main
```

### Emergency Hotfix
```bash
# Stash current work
STASH SAVE "work in progress"

# Create hotfix
BRANCH CREATE hotfix-urgent
# ... fix the issue ...
COMMIT "hotfix: critical security patch"
PUSH -u origin hotfix-urgent

# Return to previous work
BRANCH SWITCH main
STASH POP
```

## ⚙️ Configuration

### Multiple SSH Keys
You can manage multiple SSH keys for different services:

```bash
# GitHub key
SSH-KEY GENERATE github_key

# GitLab key  
SSH-KEY GENERATE gitlab_key

# Company Git server key
SSH-KEY GENERATE company_key
```

### SSH Config (Optional)
Create `sandbox/user/.ssh/config` for advanced SSH configuration:

```
Host github.com
    HostName github.com
    User git
    IdentityFile ~/sandbox/user/.ssh/github_key

Host gitlab.com
    HostName gitlab.com
    User git
    IdentityFile ~/sandbox/user/.ssh/gitlab_key
```

## 🚨 Troubleshooting

### SSH Key Issues
```bash
# Check if keys exist
SSH-KEY LIST

# Test connection
SSH-KEY TEST git@github.com

# Re-add key to agent
SSH-KEY ADD id_rsa
```

### Git Operation Failures
```bash
# Check repository status
GIT STATUS

# Verify remote configuration
REMOTE

# Test SSH connection
SSH-KEY TEST <git_host>
```

## 📝 Notes

- Git commands only available in Dev Mode (when wizard folder exists)
- SSH keys are isolated to uDOS sandbox for security
- All operations include automatic SSH agent setup
- Keys persist between uDOS sessions
- Compatible with GitHub, GitLab, Bitbucket, and custom Git servers

---
**Status:** Production Ready ✅  
**Security Level:** Sandbox Isolated  
**Compatibility:** All major Git services  
**Dev Mode:** Required for all operations
