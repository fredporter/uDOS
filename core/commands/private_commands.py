"""
Private Command Handler - v1.0.20
Tier 1: Personal encrypted data (never shared)

Commands:
  PRIVATE SAVE <file>     - Encrypt and save file to private tier
  PRIVATE READ <file>     - Decrypt and display file
  PRIVATE LIST [path]     - List private files
  PRIVATE DELETE <file>   - Securely delete private file
  PRIVATE UNLOCK          - Unlock private tier with password
  PRIVATE LOCK            - Lock private tier
  PRIVATE STATUS          - Show private tier status

Author: uDOS Development Team
Version: 1.0.20
"""

import os
import getpass
from pathlib import Path
from typing import List, Optional
from core.services.encryption_service import EncryptionService
from core.services.memory_manager import MemoryManager, MemoryTier


class PrivateCommandHandler:
    """Handler for PRIVATE (Tier 1) commands"""

    def __init__(self):
        """Initialize PrivateCommandHandler"""
        self.memory_manager = MemoryManager()
        self.encryption_service = EncryptionService()
        self.private_path = self.memory_manager.get_tier_path(MemoryTier.PRIVATE)
        self.unlocked = False
        self.password = None

    def handle(self, command: str, args: List[str]) -> str:
        """
        Route PRIVATE commands to appropriate handlers

        Args:
            command: Subcommand (SAVE, READ, etc.)
            args: Command arguments

        Returns:
            Formatted response string
        """
        if not command or command.upper() == "HELP":
            return self._help()

        command = command.upper()

        handlers = {
            'SAVE': self._save,
            'WRITE': self._save,     # Alias
            'READ': self._read,
            'OPEN': self._read,      # Alias
            'LIST': self._list,
            'LS': self._list,        # Alias
            'DELETE': self._delete,
            'RM': self._delete,      # Alias
            'UNLOCK': self._unlock,
            'LOCK': self._lock,
            'STATUS': self._status,
            'INFO': self._status,    # Alias
        }

        handler = handlers.get(command)
        if handler:
            return handler(args)
        else:
            return f"❌ Unknown PRIVATE command: {command}\n\nType 'PRIVATE HELP' for usage."

    def _help(self) -> str:
        """Display PRIVATE command help"""
        return """
🔒 PRIVATE - Tier 1: Personal Encrypted Storage

SECURITY MODEL:
  • Maximum privacy - Never shared or synced
  • AES-256-GCM encryption automatic on save
  • Password-based encryption (PBKDF2, 100k iterations)
  • Device owner only - No remote access
  • Secure deletion with data overwrite

COMMANDS:
  PRIVATE UNLOCK                 Unlock private tier with password
  PRIVATE LOCK                   Lock private tier
  PRIVATE SAVE <file>            Encrypt and save file
  PRIVATE READ <file>            Decrypt and display file
  PRIVATE LIST [path]            List private files
  PRIVATE DELETE <file>          Securely delete file
  PRIVATE STATUS                 Show tier status

WORKFLOW:
  1. PRIVATE UNLOCK              # Authenticate once per session
  2. PRIVATE SAVE journal.md     # Auto-encrypt on save
  3. PRIVATE READ journal.md     # Auto-decrypt on read
  4. PRIVATE LOCK                # Lock when done

WHAT TO STORE:
  ✅ Personal journals and reflections
  ✅ Private medical records
  ✅ Passwords and credentials
  ✅ Financial data
  ✅ Personal goals and plans
  ✅ Private notes and ideas

SECURITY NOTES:
  • Master password required to access tier
  • Files encrypted with AES-256-GCM
  • No password recovery - if lost, data is gone
  • Files never synced to other devices
  • Deleted files are securely overwritten

EXAMPLES:
  PRIVATE UNLOCK                 # Enter password to unlock
  PRIVATE SAVE journal.md        # Encrypt journal
  PRIVATE LIST                   # See encrypted files
  PRIVATE READ journal.md        # Decrypt and read
  PRIVATE DELETE old-notes.md    # Secure delete
  PRIVATE LOCK                   # Lock tier
"""

    def _check_unlocked(self) -> Optional[str]:
        """Check if tier is unlocked, return error message if not"""
        if not self.unlocked:
            return "🔐 Private tier is locked. Use 'PRIVATE UNLOCK' to authenticate."
        return None

    def _unlock(self, args: List[str]) -> str:
        """Unlock private tier with password"""
        if self.unlocked:
            return "✅ Private tier is already unlocked"

        print("\n🔒 Private Tier Authentication")
        print("Enter your master password to unlock private storage.")
        print("(This password encrypts all your private data)\n")

        # Get password from user
        password = getpass.getpass("Password: ")

        if not password:
            return "❌ Password cannot be empty"

        # Verify password
        if not self.encryption_service.verify_password(password):
            # First time setup
            print("\n🆕 First time setup detected!")
            print("This will be your master password for all private data.")
            confirm = getpass.getpass("Confirm password: ")

            if password != confirm:
                return "❌ Passwords do not match"

        # Set master key
        self.encryption_service.set_master_key(password)
        self.password = password
        self.unlocked = True

        return """
✅ Private tier unlocked successfully!

🔒 Security Active:
  • AES-256-GCM encryption enabled
  • All saves automatically encrypted
  • All reads automatically decrypted
  • Files never leave device unencrypted

Type 'PRIVATE LOCK' when finished to secure tier.
"""

    def _lock(self, args: List[str]) -> str:
        """Lock private tier"""
        if not self.unlocked:
            return "ℹ️  Private tier is already locked"

        self.unlocked = False
        self.password = None
        self.encryption_service._master_key = None

        return "🔒 Private tier locked. All encrypted data secured."

    def _status(self, args: List[str]) -> str:
        """Show private tier status"""
        stats = self.memory_manager.get_tier_stats(MemoryTier.PRIVATE)

        output = ["🔒 Private Tier Status"]
        output.append("=" * 60)

        # Lock status
        lock_status = "🔓 UNLOCKED" if self.unlocked else "🔐 LOCKED"
        output.append(f"\nSecurity: {lock_status}")

        if self.unlocked:
            output.append("⚠️  Remember to LOCK when finished!")

        # Statistics
        output.append(f"\n📊 Statistics:")
        output.append(f"  Files: {stats['file_count']}")
        output.append(f"  Size: {stats['total_size_mb']} MB")
        if stats['last_modified']:
            output.append(f"  Last Modified: {stats['last_modified']}")

        # Security info
        output.append(f"\n🔐 Encryption:")
        output.append(f"  Algorithm: AES-256-GCM")
        output.append(f"  Key Derivation: PBKDF2-SHA256 (100k iterations)")
        output.append(f"  Master Key: {'Set' if self.unlocked else 'Not set'}")

        output.append("\n" + "=" * 60)

        return "\n".join(output)

    def _save(self, args: List[str]) -> str:
        """Save and encrypt a file to private tier"""
        error = self._check_unlocked()
        if error:
            return error

        if not args:
            return "❌ Usage: PRIVATE SAVE <filename>"

        filename = args[0]
        source = Path(filename)

        # Check if source exists
        if not source.exists():
            return f"❌ File not found: {filename}"

        # Read file content
        try:
            with open(source, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return f"❌ Error reading file: {e}"

        # Encrypt content
        try:
            ciphertext, nonce = self.encryption_service.encrypt(content)
        except Exception as e:
            return f"❌ Encryption error: {e}"

        # Save to private tier
        dest = self.private_path / (source.name + '.enc')

        try:
            import json
            from base64 import b64encode

            package = {
                'nonce': b64encode(nonce).decode('utf-8'),
                'ciphertext': b64encode(ciphertext).decode('utf-8'),
                'original_name': source.name,
                'size': len(content),
                'encrypted_at': str(source.stat().st_mtime)
            }

            with open(dest, 'w') as f:
                json.dump(package, f, indent=2)

            # Secure file permissions
            os.chmod(dest, 0o600)

        except Exception as e:
            return f"❌ Error saving encrypted file: {e}"

        return f"""
✅ File encrypted and saved to private tier

📄 File: {source.name}
🔒 Encrypted: {dest.name}
💾 Size: {len(content)} bytes → {dest.stat().st_size} bytes
🔐 Security: AES-256-GCM with authentication

The file is now encrypted and stored in your private tier.
Use 'PRIVATE READ {source.name}' to decrypt and view.
"""

    def _read(self, args: List[str]) -> str:
        """Read and decrypt a file from private tier"""
        error = self._check_unlocked()
        if error:
            return error

        if not args:
            return "❌ Usage: PRIVATE READ <filename>"

        filename = args[0]

        # Look for encrypted file
        enc_file = self.private_path / (filename + '.enc')

        if not enc_file.exists():
            # Try without .enc extension
            enc_file = self.private_path / filename
            if not enc_file.exists():
                return f"❌ File not found in private tier: {filename}"

        # Read encrypted package
        try:
            import json
            from base64 import b64decode

            with open(enc_file, 'r') as f:
                package = json.load(f)

            nonce = b64decode(package['nonce'])
            ciphertext = b64decode(package['ciphertext'])
            original_name = package.get('original_name', filename)

        except Exception as e:
            return f"❌ Error reading encrypted file: {e}"

        # Decrypt
        try:
            content = self.encryption_service.decrypt(ciphertext, nonce)
        except Exception as e:
            return f"❌ Decryption error: {e}"

        # Display content
        output = [f"🔓 Decrypted: {original_name}"]
        output.append("=" * 60)
        output.append(content)
        output.append("=" * 60)
        output.append(f"📄 Size: {len(content)} bytes")

        return "\n".join(output)

    def _list(self, args: List[str]) -> str:
        """List files in private tier"""
        error = self._check_unlocked()
        if error:
            return error

        path = args[0] if args else ""
        files = self.memory_manager.list_files(MemoryTier.PRIVATE, path)

        output = ["🔒 Private Tier Files"]
        if path:
            output.append(f"📁 Path: {path}")
        output.append("=" * 60)

        if not files:
            output.append("\n📭 No encrypted files found")
        else:
            output.append(f"\n🔐 {len(files)} encrypted items\n")

            for file in files:
                if file['is_dir']:
                    output.append(f"📁 {file['name']}/")
                else:
                    # Remove .enc extension for display
                    display_name = file['name'].replace('.enc', '')
                    size_kb = file['size'] / 1024
                    output.append(f"🔒 {display_name} ({size_kb:.1f} KB encrypted)")

        output.append("\n" + "=" * 60)
        output.append("\nℹ️  Use 'PRIVATE READ <filename>' to decrypt and view")

        return "\n".join(output)

    def _delete(self, args: List[str]) -> str:
        """Securely delete a file from private tier"""
        error = self._check_unlocked()
        if error:
            return error

        if not args:
            return "❌ Usage: PRIVATE DELETE <filename>"

        filename = args[0]

        # Look for encrypted file
        enc_file = self.private_path / (filename + '.enc')

        if not enc_file.exists():
            enc_file = self.private_path / filename
            if not enc_file.exists():
                return f"❌ File not found in private tier: {filename}"

        # Confirm deletion
        print(f"\n⚠️  Secure deletion of: {filename}")
        print("This will permanently delete the encrypted file.")
        confirm = input("Type 'DELETE' to confirm: ")

        if confirm.upper() != 'DELETE':
            return "❌ Deletion cancelled"

        # Secure delete (overwrite before removing)
        try:
            file_size = enc_file.stat().st_size

            # Overwrite with random data
            with open(enc_file, 'wb') as f:
                f.write(os.urandom(file_size))

            # Delete file
            enc_file.unlink()

        except Exception as e:
            return f"❌ Error deleting file: {e}"

        return f"""
✅ File securely deleted from private tier

📄 File: {filename}
🔒 Encrypted data overwritten with random bytes
🗑️  File removed from filesystem

The encrypted file has been permanently deleted.
"""


def main():
    """Test PrivateCommandHandler"""
    handler = PrivateCommandHandler()

    print("\n" + "=" * 60)
    print("Testing PRIVATE Commands")
    print("=" * 60 + "\n")

    # Test commands
    print(handler.handle("HELP", []))
    print("\n" + "=" * 60 + "\n")
    print(handler.handle("STATUS", []))


if __name__ == "__main__":
    main()
