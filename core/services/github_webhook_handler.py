"""
GitHub Webhook Handler for uDOS v1.2.5
Processes GitHub webhook events and triggers knowledge update workflows.

Supported Events:
- push: Repository push events (knowledge updates)
- pull_request: PR opened/merged (review triggers)
- release: New releases (changelog updates)
"""

import json
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path


class GitHubWebhookHandler:
    """Process GitHub webhook events."""

    def __init__(self):
        self.event_handlers = {
            'push': self.handle_push,
            'pull_request': self.handle_pull_request,
            'release': self.handle_release,
            'issues': self.handle_issue,
            'issue_comment': self.handle_issue_comment,
            'workflow_run': self.handle_workflow_run
        }

    def process_event(self, event_type: str, payload: Dict) -> Dict:
        """
        Process GitHub webhook event.

        Args:
            event_type: GitHub event type (push, pull_request, etc.)
            payload: Webhook payload

        Returns:
            Processing result with actions to take
        """
        handler = self.event_handlers.get(event_type)
        if not handler:
            return {
                'status': 'ignored',
                'reason': f'No handler for event type: {event_type}'
            }

        try:
            return handler(payload)
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'event_type': event_type
            }

    def handle_push(self, payload: Dict) -> Dict:
        """
        Handle push events.

        Triggers knowledge update workflow if:
        - Push to main/master branch
        - Changes in knowledge/ directory
        - Commit message contains [knowledge-update]
        """
        ref = payload.get('ref', '')
        branch = ref.split('/')[-1] if '/' in ref else ref
        commits = payload.get('commits', [])
        repository = payload.get('repository', {}).get('full_name', 'unknown')

        # Check if push to main/master
        if branch not in ['main', 'master']:
            return {
                'status': 'ignored',
                'reason': f'Not main branch: {branch}'
            }

        # Check for knowledge directory changes
        knowledge_files = []
        for commit in commits:
            added = commit.get('added', [])
            modified = commit.get('modified', [])
            removed = commit.get('removed', [])

            all_files = added + modified + removed
            knowledge_files.extend([
                f for f in all_files
                if f.startswith('knowledge/')
            ])

        if not knowledge_files:
            return {
                'status': 'ignored',
                'reason': 'No knowledge files changed'
            }

        # Build workflow actions
        actions = []

        # Run quality scan on changed guides
        changed_guides = [
            f for f in knowledge_files
            if f.endswith('.md') and not f.endswith('README.md')
        ]

        if changed_guides:
            actions.append({
                'type': 'workflow',
                'name': 'knowledge-quality-scan',
                'args': {
                    'files': changed_guides,
                    'reason': f'GitHub push to {branch}'
                }
            })

        # Run cross-reference validation
        actions.append({
            'type': 'workflow',
            'name': 'xref-validation',
            'args': {
                'reason': f'GitHub push to {branch}'
            }
        })

        return {
            'status': 'processed',
            'event': 'push',
            'repository': repository,
            'branch': branch,
            'commits': len(commits),
            'knowledge_files': len(knowledge_files),
            'actions': actions
        }

    def handle_pull_request(self, payload: Dict) -> Dict:
        """
        Handle pull request events.

        Triggers review workflow for:
        - PR opened with knowledge changes
        - PR ready for review
        """
        action = payload.get('action', '')
        pr = payload.get('pull_request', {})
        pr_number = pr.get('number', 0)
        title = pr.get('title', '')
        base_branch = pr.get('base', {}).get('ref', '')

        # Only process opened/ready_for_review
        if action not in ['opened', 'ready_for_review', 'synchronize']:
            return {
                'status': 'ignored',
                'reason': f'PR action not relevant: {action}'
            }

        # Check if PR affects knowledge
        if 'knowledge' not in title.lower():
            return {
                'status': 'ignored',
                'reason': 'PR does not mention knowledge'
            }

        actions = [{
            'type': 'workflow',
            'name': 'knowledge-gap-analysis',
            'args': {
                'pr_number': pr_number,
                'reason': f'PR #{pr_number} review'
            }
        }]

        return {
            'status': 'processed',
            'event': 'pull_request',
            'action': action,
            'pr_number': pr_number,
            'title': title,
            'actions': actions
        }

    def handle_release(self, payload: Dict) -> Dict:
        """
        Handle release events.

        Triggers changelog/documentation updates.
        """
        action = payload.get('action', '')
        release = payload.get('release', {})
        tag = release.get('tag_name', '')
        name = release.get('name', '')

        if action != 'published':
            return {
                'status': 'ignored',
                'reason': f'Release not published: {action}'
            }

        actions = [{
            'type': 'command',
            'command': 'CHANGELOG UPDATE',
            'args': {
                'version': tag,
                'release_name': name
            }
        }]

        return {
            'status': 'processed',
            'event': 'release',
            'tag': tag,
            'name': name,
            'actions': actions
        }

    def handle_issue(self, payload: Dict) -> Dict:
        """Handle issue events (knowledge gap submissions)."""
        action = payload.get('action', '')
        issue = payload.get('issue', {})
        title = issue.get('title', '')
        labels = [label.get('name') for label in issue.get('labels', [])]

        # Check if knowledge gap issue
        if 'knowledge-gap' not in labels:
            return {
                'status': 'ignored',
                'reason': 'Not a knowledge gap issue'
            }

        if action == 'opened':
            return {
                'status': 'processed',
                'event': 'issue',
                'action': action,
                'title': title,
                'actions': [{
                    'type': 'notification',
                    'message': f'New knowledge gap reported: {title}'
                }]
            }

        return {'status': 'ignored', 'reason': f'Issue action: {action}'}

    def handle_issue_comment(self, payload: Dict) -> Dict:
        """Handle issue comment events."""
        return {'status': 'ignored', 'reason': 'Issue comments not processed'}

    def handle_workflow_run(self, payload: Dict) -> Dict:
        """Handle GitHub Actions workflow run events."""
        action = payload.get('action', '')
        workflow = payload.get('workflow', {})
        workflow_name = workflow.get('name', '')

        if action == 'completed' and 'knowledge' in workflow_name.lower():
            return {
                'status': 'processed',
                'event': 'workflow_run',
                'workflow': workflow_name,
                'actions': [{
                    'type': 'notification',
                    'message': f'Knowledge workflow completed: {workflow_name}'
                }]
            }

        return {'status': 'ignored', 'reason': f'Workflow: {workflow_name}'}


# Global handler instance
_github_handler = None


def get_github_handler() -> GitHubWebhookHandler:
    """Get global GitHub webhook handler."""
    global _github_handler
    if _github_handler is None:
        _github_handler = GitHubWebhookHandler()
    return _github_handler
