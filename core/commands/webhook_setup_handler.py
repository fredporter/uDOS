"""
Webhook Setup Handler - Interactive GitHub integration setup.

Provides vibe-cli style interactive prompts:
- Tells you what to do
- Opens URLs automatically
- Waits for you to press ENTER
- Saves secrets to Wizard keystore

Integrations supported:
  - GitHub webhooks (repo push, pull request events)
"""

import subprocess
import webbrowser
import sys
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime

from core.commands.base import BaseCommandHandler
from core.services.logging_api import get_repo_root, get_logger

logger = get_logger('webhook-setup')


class WebhookSetupHandler(BaseCommandHandler):
    """Interactive webhook setup handler with vibe-cli UX."""

    def __init__(self):
        """Initialize webhook setup handler."""
        super().__init__()
        self.repo_root = get_repo_root()
        self.wizard_installed = self._check_wizard_installed()

    def _check_wizard_installed(self) -> bool:
        """Check if Wizard server is installed."""
        wizard_dir = self.repo_root / "wizard"
        return wizard_dir.exists() and (wizard_dir / "server.py").exists()

    def _show_webhook_help(self) -> str:
        """Show webhook setup help."""
        return """
╔════════════════════════════════════════════════════════════╗
║          SETUP WEBHOOK - Interactive Integration Help     ║
╚════════════════════════════════════════════════════════════╝

WEBHOOK SETUP connects GitHub to uDOS with interactive prompts.

INTERACTIVE FEATURES (vibe-cli style):
  ✓ Step-by-step guidance
  ✓ Automatic URL opening
  ✓ Press ENTER to continue prompts
  ✓ Automatic secret storage in Wizard keystore
  ✓ No manual config files needed

AVAILABLE COMMANDS:

  SETUP webhook              Full setup (GitHub)
  SETUP webhook github       GitHub webhooks only

GITHUB WEBHOOKS:
  Enables uDOS to listen for:
    • Repository push events
    • Pull request events
    • Issue creation/updates

  Requires: GitHub account with repo access

WORKFLOW:

  1. Run: SETUP webhook
  2. Choose GitHub
  3. Follow interactive prompts
  4. URLs open automatically for configuration
  5. Secrets saved to Wizard keystore (encrypted)

VERIFICATION:

  After setup:
    WIZARD                    Start Wizard server
    http://localhost:8765     Open dashboard
    Settings → Webhooks       Verify connections

REQUIREMENTS:

  • Wizard Server installed (see: wizard/README.md)
  • GitHub account
  • Internet connection for OAuth/API setup

TROUBLESHOOTING:

  Browser won't open?
    • Manually visit the URL shown on screen
    • Links work even in headless/SSH environments

  Secret not saving?
    • Check: Is Wizard Server installed?
    • Run: python -m wizard.tools.secret_store_cli status

  Webhook not working?
    • See: docs/WEBHOOK-SETUP-SUMMARY.md

LEARN MORE:

  • docs/WEBHOOK-SETUP-SUMMARY.md       Quick reference
  • wizard/README.md                     Wizard architecture
  • GitHub docs: https://docs.github.com/webhooks

═══════════════════════════════════════════════════════════════
"""

    def handle(self, command: str, params: list, grid=None, parser=None) -> Dict:
        """
        Handle SETUP webhook command.

        Usage:
            SETUP webhook         Run full webhook setup (interactive)
            SETUP webhook github  Setup GitHub webhooks only
            SETUP webhook --help  Show help
        """
        if not params or params[0].lower() != "webhook":
            return {"status": "error", "message": "Invalid webhook setup command"}

        # Check if Wizard is needed
        if not self.wizard_installed:
            return {
                "status": "warning",
                "output": self._prompt_wizard_required()
            }

        if len(params) > 1:
            provider = params[1].lower()
            if provider == "--help":
                return {"status": "success", "output": self._show_webhook_help()}
            elif provider == "github":
                return self._setup_github_webhook()
            else:
                return {"status": "error", "message": f"Unknown webhook provider: {provider}"}

        # Full interactive setup (GitHub)
        return self._run_full_webhook_setup()

    def _run_full_webhook_setup(self) -> Dict:
        """Run interactive setup for GitHub webhooks."""
        lines = []
        lines.append("\n" + "=" * 70)
        lines.append("🔗  WEBHOOK SETUP - GitHub Integration")
        lines.append("=" * 70 + "\n")

        lines.append("This setup will guide you through connecting:")
        lines.append("  1. GitHub webhooks (push, pull request, issues)\n")

        lines.append("Each integration requires:")
        lines.append("  • You create an app/key on the external platform")
        lines.append("  • We save the secret to Wizard's encrypted keystore")
        lines.append("  • Everything stays local - no data leaves your machine\n")

        # Confirm
        response = input("Press ENTER to continue, or 'n' to skip: ").strip().lower()
        if response == "n":
            return {"status": "cancelled", "output": "Webhook setup cancelled."}

        results = {
            "github": self._setup_github_webhook(),
        }

        return {
            "status": "success",
            "output": self._summarize_setup(results)
        }

    def _setup_github_webhook(self) -> Dict:
        """Interactive GitHub webhook setup with vibe-cli UX."""
        print("\n" + "-" * 70)
        print("🐙  GITHUB WEBHOOK SETUP")
        print("-" * 70 + "\n")

        print("GitHub webhooks allow uDOS to listen for:")
        print("  • Repository push events")
        print("  • Pull request events")
        print("  • Issue creation/updates")
        print("  • Code reviews and discussions\n")

        # Step 1: Generate webhook secret
        print("Step 1: Generate a secure webhook secret")
        print("-" * 70)
        secret = self._generate_github_secret()
        if not secret:
            return {"status": "error", "message": "Failed to generate GitHub secret"}

        print(f"\n✅ Generated webhook secret: {secret[:16]}...\n")

        # Step 2: Configure GitHub repository
        print("Step 2: Add webhook to your GitHub repository")
        print("-" * 70)
        print("\nWe'll open your GitHub repository settings...")
        print("  1. Go to your repo")
        print("  2. Settings → Webhooks → Add webhook")
        print("  3. Use these settings:\n")

        print(f"  Payload URL:     http://localhost:8765/api/github/webhook")
        print(f"  Content type:    application/json")
        print(f"  Secret:          [Will paste below]")
        print(f"  Events:          Push, Pull requests, Issues\n")

        # Open GitHub settings (generic - they need to know their repo URL)
        print("Your GitHub webhooks page:")
        response = input("Press ENTER to open GitHub documentation: ").strip()

        try:
            webbrowser.open("https://docs.github.com/en/developers/webhooks-and-events/webhooks/creating-webhooks")
        except Exception as e:
            logger.warning(f"[WIZ] Could not open browser: {e}")
            print("👉 Please manually visit: https://docs.github.com/en/developers/webhooks-and-events/webhooks/creating-webhooks")

        # Step 3: Paste secret
        print("\n" + "-" * 70)
        print("\nNow paste the webhook secret into GitHub settings, then return here.\n")

        response = input("Press ENTER when you've added the webhook to GitHub: ").strip()

        # Step 4: Save to Wizard keystore
        print("\nStep 3: Save secret to Wizard keystore")
        print("-" * 70)
        print(f"\nSaving GitHub webhook secret to encrypted keystore...")

        success = self._save_github_secret(secret)
        if success:
            print("✅ GitHub webhook secret saved!\n")
            return {
                "status": "success",
                "provider": "github",
                "secret_id": "github-webhook-secret",
                "message": "GitHub webhook configured successfully"
            }
        else:
            print("⚠️  Could not save secret. Check Wizard keystore is accessible.\n")
            return {
                "status": "error",
                "provider": "github",
                "message": "Failed to save GitHub webhook secret"
            }

    def _generate_github_secret(self) -> Optional[str]:
        """Generate GitHub webhook secret using Wizard tools."""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "wizard.tools.generate_github_secrets"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                # Parse output - should contain the secret
                output_lines = result.stdout.strip().split("\n")
                for line in output_lines:
                    if line.startswith("Secret: "):
                        return line.replace("Secret: ", "").strip()
                    # Try alternative format
                    if len(line) > 30 and line.isalnum():
                        return line

            logger.error(f"[WIZ] Failed to generate GitHub secret: {result.stderr}")
            return None
        except Exception as e:
            logger.error(f"[WIZ] Error generating GitHub secret: {e}")
            return None

    def _save_github_secret(self, secret: str) -> bool:
        """Save GitHub webhook secret to Wizard keystore."""
        try:
            result = subprocess.run(
                [
                    sys.executable, "-m",
                    "wizard.tools.secret_store_cli",
                    "set", "github-webhook-secret", secret
                ],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                logger.info("[WIZ] GitHub webhook secret saved to keystore")
                return True
            else:
                logger.error(f"[WIZ] Failed to save secret: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"[WIZ] Error saving GitHub secret: {e}")
            return False

    def _summarize_setup(self, results: Dict) -> str:
        """Summarize webhook setup results."""
        lines = []
        lines.append("\n" + "=" * 70)
        lines.append("✅  WEBHOOK SETUP COMPLETE")
        lines.append("=" * 70 + "\n")

        github_result = results.get("github", {})
        if github_result.get("status") == "success":
            lines.append("✅ GitHub webhook configured")
            lines.append("   • Secrets saved to Wizard keystore")
            lines.append("   • Ready to receive repository events\n")
        elif github_result.get("status") != "skipped":
            lines.append("⚠️  GitHub webhook setup incomplete")
            lines.append(f"   • {github_result.get('message', 'Unknown error')}\n")

        lines.append("-" * 70)
        lines.append("\nNext steps:")
        lines.append("  1. Start Wizard server: WIZARD")
        lines.append("  2. Open dashboard: http://localhost:8765")
        lines.append("  3. Go to Settings → Webhooks")
        lines.append("  4. Verify GitHub is 'Connected'\n")

        lines.append("For troubleshooting:")
        lines.append("  • See: docs/WEBHOOK-SETUP-SUMMARY.md")
        lines.append("  • Detailed guide: docs/WEBHOOK-SETUP-SUMMARY.md\n")

        lines.append("=" * 70)

        return "\n".join(lines)

    def _prompt_wizard_required(self) -> str:
        """Prompt when Wizard is not installed."""
        return """
╔════════════════════════════════════════════════════════════╗
║  ⚠️  Wizard Server Required for Webhook Setup             ║
╚════════════════════════════════════════════════════════════╝

Webhook integration requires Wizard Server (port 8765) to be installed.

Wizard manages sensitive data:
  • GitHub webhook secrets
  • OAuth tokens
  • Cloud credentials

These are NOT stored locally in Core - they're in Wizard's encrypted keystore.

TO INSTALL WIZARD:
  1. Navigate to the wizard/ directory:
     cd wizard

  2. Install dependencies:
     pip install -r requirements.txt

  3. Run setup:
     python -m wizard.tools.check_provider_setup

  4. Then return here:
     SETUP webhook

LEARN MORE:
  • wizard/README.md
  • docs/INSTALLATION.md
  • docs/WIZARD-ARCHITECTURE.md

OFFLINE SETUP:
  If you want to configure only local identity settings:
     SETUP

  Webhook integration is always optional - configure when ready.
"""
