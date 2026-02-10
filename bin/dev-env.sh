#!/bin/bash
# =============================================================================
# uDOS Development Environment Setup
# =============================================================================
# Disable pagers and configure VSCode terminal for clean output
# Source this in your shell: source bin/dev-env.sh

# Disable all pagers (prevents alternate buffer mode)
export PAGER=cat
export GIT_PAGER=cat
export LESS=-R

# Ensure unbuffered output
export PYTHONUNBUFFERED=1

# VSCode terminal settings
export TERM=xterm-256color

# Prevent less from opening
export LESSSECURE=1

# Git: No paging for any commands
git config --local pager.log cat 2>/dev/null
git config --local pager.diff cat 2>/dev/null
git config --local pager.show cat 2>/dev/null
git config --local pager.status cat 2>/dev/null

echo "✅ Dev environment configured:"
echo "   • Git pagers disabled"
echo "   • Python unbuffered output"
echo "   • PAGER set to cat"
echo "   • Terminal ready for development"
