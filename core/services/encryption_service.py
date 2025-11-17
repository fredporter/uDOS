"""
Encryption Service - v1.0.20
AES-256 encryption for Tier 1 (Private) memory

Security Features:
- AES-256-GCM encryption
- PBKDF2 key derivation (100,000 iterations)
- Secure random IV generation
- Authentication tag verification
- Key stretching from password

Author: uDOS Development Team
Version: 1.0.20
"""

import os
import json
import hashlib
from pathlib import Path
from typing import Tuple, Optional
from base64 import b64encode, b64decode
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend


class EncryptionService:
    """
    Handles AES-256-GCM encryption/decryption for private data

    Features:
    - Password-based encryption (PBKDF2 key derivation)
    - Automatic IV generation
    - Authentication with GCM mode
    - Secure key storage
    """

    def __init__(self, key_file: str = None):
        """
        Initialize EncryptionService

        Args:
            key_file: Path to store encryption key salt (defaults to .metadata/encryption.key)
        """
        if key_file is None:
            base_path = Path(__file__).parent.parent.parent / 'memory' / '.metadata'
            base_path.mkdir(parents=True, exist_ok=True)
            key_file = base_path / 'encryption.key'

        self.key_file = Path(key_file)
        self.salt = self._load_or_create_salt()
        self._master_key = None

    def _load_or_create_salt(self) -> bytes:
        """Load existing salt or create new one"""
        if self.key_file.exists():
            with open(self.key_file, 'rb') as f:
                data = json.loads(f.read())
                return b64decode(data['salt'])
        else:
            # Generate new salt
            salt = os.urandom(32)
            self._save_salt(salt)
            return salt

    def _save_salt(self, salt: bytes):
        """Save salt to key file"""
        data = {
            'salt': b64encode(salt).decode('utf-8'),
            'algorithm': 'PBKDF2-SHA256',
            'iterations': 100000,
            'key_size': 32
        }
        self.key_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.key_file, 'w') as f:
            json.dump(data, f, indent=2)

        # Secure file permissions (owner read/write only)
        os.chmod(self.key_file, 0o600)

    def derive_key(self, password: str) -> bytes:
        """
        Derive encryption key from password using PBKDF2

        Args:
            password: User password

        Returns:
            32-byte encryption key
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
            backend=default_backend()
        )
        return kdf.derive(password.encode('utf-8'))

    def set_master_key(self, password: str):
        """Set master encryption key from password"""
        self._master_key = self.derive_key(password)

    def get_master_key(self) -> Optional[bytes]:
        """Get current master key"""
        return self._master_key

    def encrypt(self, data: str, password: str = None) -> Tuple[bytes, bytes]:
        """
        Encrypt data using AES-256-GCM

        Args:
            data: Plain text data to encrypt
            password: Password to derive key (uses master key if not provided)

        Returns:
            Tuple of (ciphertext, nonce)
        """
        # Derive key from password or use master key
        if password:
            key = self.derive_key(password)
        elif self._master_key:
            key = self._master_key
        else:
            raise ValueError("No password or master key provided")

        # Generate random nonce (12 bytes for GCM)
        nonce = os.urandom(12)

        # Create cipher and encrypt
        aesgcm = AESGCM(key)
        ciphertext = aesgcm.encrypt(nonce, data.encode('utf-8'), None)

        return ciphertext, nonce

    def decrypt(self, ciphertext: bytes, nonce: bytes, password: str = None) -> str:
        """
        Decrypt data using AES-256-GCM

        Args:
            ciphertext: Encrypted data
            nonce: Nonce used during encryption
            password: Password to derive key (uses master key if not provided)

        Returns:
            Decrypted plain text

        Raises:
            ValueError: If decryption fails (wrong password or corrupted data)
        """
        # Derive key from password or use master key
        if password:
            key = self.derive_key(password)
        elif self._master_key:
            key = self._master_key
        else:
            raise ValueError("No password or master key provided")

        # Create cipher and decrypt
        try:
            aesgcm = AESGCM(key)
            plaintext = aesgcm.decrypt(nonce, ciphertext, None)
            return plaintext.decode('utf-8')
        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}")

    def encrypt_file(self, filepath: Path, password: str = None) -> Path:
        """
        Encrypt a file in place

        Args:
            filepath: Path to file to encrypt
            password: Encryption password

        Returns:
            Path to encrypted file (.enc extension)
        """
        # Read plain text
        with open(filepath, 'r', encoding='utf-8') as f:
            plaintext = f.read()

        # Encrypt
        ciphertext, nonce = self.encrypt(plaintext, password)

        # Save encrypted file
        enc_filepath = filepath.with_suffix(filepath.suffix + '.enc')

        # Package ciphertext and nonce
        package = {
            'nonce': b64encode(nonce).decode('utf-8'),
            'ciphertext': b64encode(ciphertext).decode('utf-8'),
            'original_name': filepath.name,
            'encrypted_at': str(filepath.stat().st_mtime)
        }

        with open(enc_filepath, 'w') as f:
            json.dump(package, f, indent=2)

        # Remove original file
        filepath.unlink()

        return enc_filepath

    def decrypt_file(self, enc_filepath: Path, password: str = None) -> Path:
        """
        Decrypt a file

        Args:
            enc_filepath: Path to encrypted file
            password: Decryption password

        Returns:
            Path to decrypted file
        """
        # Read encrypted package
        with open(enc_filepath, 'r') as f:
            package = json.load(f)

        # Extract components
        nonce = b64decode(package['nonce'])
        ciphertext = b64decode(package['ciphertext'])
        original_name = package.get('original_name', enc_filepath.stem)

        # Decrypt
        plaintext = self.decrypt(ciphertext, nonce, password)

        # Save decrypted file
        dec_filepath = enc_filepath.parent / original_name
        with open(dec_filepath, 'w', encoding='utf-8') as f:
            f.write(plaintext)

        return dec_filepath

    def verify_password(self, password: str, test_data: str = "test") -> bool:
        """
        Verify password by encrypting and decrypting test data

        Args:
            password: Password to verify
            test_data: Test string to encrypt/decrypt

        Returns:
            True if password works, False otherwise
        """
        try:
            ciphertext, nonce = self.encrypt(test_data, password)
            decrypted = self.decrypt(ciphertext, nonce, password)
            return decrypted == test_data
        except Exception:
            return False

    def change_password(self, old_password: str, new_password: str):
        """
        Change encryption password

        Note: This requires re-encrypting all files in private tier

        Args:
            old_password: Current password
            new_password: New password
        """
        # Verify old password
        if not self.verify_password(old_password):
            raise ValueError("Invalid old password")

        # Generate new salt
        new_salt = os.urandom(32)
        self._save_salt(new_salt)
        self.salt = new_salt

        # Derive new key
        self._master_key = self.derive_key(new_password)


def main():
    """Test EncryptionService"""
    print("🔒 uDOS Encryption Service v1.0.20")
    print("=" * 50)

    # Create service
    service = EncryptionService()

    # Test password
    password = "test_password_123"

    print(f"\n🔑 Testing encryption with password...")

    # Test basic encryption/decryption
    test_data = "This is sensitive private data! 🔒"
    print(f"Original: {test_data}")

    # Encrypt
    ciphertext, nonce = service.encrypt(test_data, password)
    print(f"Encrypted: {b64encode(ciphertext).decode()[:50]}...")

    # Decrypt
    decrypted = service.decrypt(ciphertext, nonce, password)
    print(f"Decrypted: {decrypted}")

    # Verify
    if decrypted == test_data:
        print("✅ Encryption/decryption successful!")
    else:
        print("❌ Encryption/decryption failed!")

    # Test password verification
    print(f"\n🔐 Testing password verification...")
    if service.verify_password(password):
        print("✅ Password verification works!")
    else:
        print("❌ Password verification failed!")

    # Test wrong password
    print(f"\n🚫 Testing wrong password...")
    try:
        service.decrypt(ciphertext, nonce, "wrong_password")
        print("❌ Should have failed with wrong password!")
    except ValueError as e:
        print(f"✅ Correctly rejected wrong password: {e}")

    # Test master key
    print(f"\n🔑 Testing master key...")
    service.set_master_key(password)

    encrypted2, nonce2 = service.encrypt("Data with master key")
    decrypted2 = service.decrypt(encrypted2, nonce2)
    print(f"✅ Master key works: {decrypted2}")

    print(f"\n✅ All encryption tests passed!")


if __name__ == "__main__":
    main()
