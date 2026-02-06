#!/usr/bin/env python3
"""
Generate GitHub Secrets for Wizard Configuration
=================================================

Generates cryptographically secure secrets for:
- GitHub webhook secret (for validating webhook signatures)
- Displays instructions for adding to GitHub and Wizard
"""

import secrets
import json
from pathlib import Path
from datetime import datetime

# Colors
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
BLUE = "\033[0;34m"
CYAN = "\033[0;36m"
BOLD = "\033[1m"
NC = "\033[0m"  # No Color


def generate_webhook_secret(length: int = 32) -> str:
    """Generate a cryptographically secure webhook secret."""
    return secrets.token_hex(length)


def display_secret_with_instructions(secret: str, wizard_url: str = "http://localhost:8765"):
    """Display the secret and setup instructions."""

    print(f"\n{BLUE}{'=' * 70}{NC}")
    print(f"{BOLD}  🔐 GitHub Webhook Secret Generated{NC}")
    print(f"{BLUE}{'=' * 70}{NC}\n")

    # Display the secret
    print(f"{GREEN}Your GitHub Webhook Secret:{NC}")
    print(f"{CYAN}{BOLD}{secret}{NC}\n")

    print(f"{YELLOW}⚠ SAVE THIS SECRET - You'll need it in two places:{NC}\n")

    # Instructions for GitHub
    print(f"{BOLD}STEP 1: Configure in GitHub{NC}")
    print(f"{BLUE}{'─' * 70}{NC}")
    print("1. Go to your GitHub repository")
    print("2. Navigate to: Settings → Webhooks → Add webhook")
    print(f"3. Set Payload URL: {wizard_url}/api/github/webhook")
    print("4. Set Content type: application/json")
    print(f"5. Set Secret: {CYAN}{secret}{NC}")
    print("6. Select events you want:")
    print("   • Push events")
    print("   • Pull request events")
    print("   • Workflow run events")
    print("7. Make sure 'Active' is checked")
    print(f"8. Click 'Add webhook'\n")

    # Instructions for Wizard
    print(f"{BOLD}STEP 2: Configure in Wizard Dashboard{NC}")
    print(f"{BLUE}{'─' * 70}{NC}")
    print(f"1. Open Wizard Dashboard: {wizard_url}/#config")
    print("2. Scroll to 'Quick Secret Setup' section")
    print("3. Find 'GitHub Webhook Secret' field")
    print(f"4. Paste the secret: {CYAN}{secret}{NC}")
    print("5. Click 'Save to Secret Store'\n")

    # Alternative: CLI method
    print(f"{BOLD}ALTERNATIVE: Use Secret Store CLI{NC}")
    print(f"{BLUE}{'─' * 70}{NC}")
    print("If you prefer command-line setup:")
    print(f"{CYAN}python -m wizard.tools.secret_store_cli set github-webhook-secret \"{secret}\"{NC}\n")

    # Verification
    print(f"{BOLD}STEP 3: Verify Setup{NC}")
    print(f"{BLUE}{'─' * 70}{NC}")
    print(f"1. Visit: {wizard_url}/#webhooks")
    print("2. Check that GitHub webhook shows 'Secret configured'")
    print("3. Test webhook from GitHub: Settings → Webhooks → Recent Deliveries")
    print("4. Send a test payload and verify it's received\n")

    # Security notes
    print(f"{BOLD}📋 Security Notes:{NC}")
    print(f"{BLUE}{'─' * 70}{NC}")
    print("• Secret is stored encrypted in wizard/secrets.tomb")
    print("• Never commit this secret to git")
    print("• Rotate secrets periodically (every 90 days recommended)")
    print("• Use different secrets for different environments (dev/prod)")
    print(f"• Wizard requires WIZARD_KEY env var to decrypt secrets\n")

    print(f"{GREEN}✓ Secret generated successfully!{NC}\n")


def save_to_temp_file(secret: str) -> Path:
    """Save secret to a temporary file for easy copying."""
    temp_dir = Path(__file__).parent.parent.parent / "memory" / "private"
    temp_dir.mkdir(parents=True, exist_ok=True)

    temp_file = temp_dir / f"github-webhook-secret-{datetime.now().strftime('%Y%m%d-%H%M%S')}.txt"

    content = f"""GitHub Webhook Secret
Generated: {datetime.now().isoformat()}

Secret: {secret}

⚠ DELETE THIS FILE AFTER SETUP IS COMPLETE ⚠

This secret should be:
1. Added to GitHub webhook configuration
2. Saved to Wizard secret store
3. Then this file should be deleted

To save to secret store:
python -m wizard.tools.secret_store_cli set github-webhook-secret "{secret}"
"""

    temp_file.write_text(content)
    return temp_file


def main():
    """Generate and display GitHub webhook secret."""
    import sys

    # Check for custom length
    length = 32
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        length = int(sys.argv[1])

    # Check for custom wizard URL
    wizard_url = "http://localhost:8765"
    if len(sys.argv) > 2:
        wizard_url = sys.argv[2]

    # Generate secret
    secret = generate_webhook_secret(length)

    # Display instructions
    display_secret_with_instructions(secret, wizard_url)

    # Save to temp file
    temp_file = save_to_temp_file(secret)
    print(f"{BLUE}💾 Secret also saved to:{NC} {temp_file}")
    print(f"{YELLOW}   (Remember to delete after setup!){NC}\n")


if __name__ == "__main__":
    main()
