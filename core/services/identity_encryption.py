"""
User Identity Encryption - Encrypted DOB storage and starsign calculation

Provides:
  - UDOS Crypt encoding (12x12x12 system): DOB → color-animal-adjective
  - Unique profile ID generation from DOB + location
  - Starsign/generation categorization
  - Local-only encryption (never transmitted)

The DOB is mapped through the UDOS Crypt system, ensuring only
someone with the Wizard key can decrypt the full identity.

Example: DOB 1975-11-15 + location "New York"
  → Scorpio (blue) + Gen X (wolf) + swift
  → "blue-wolf-swift"
  → Profile ID: a3f2c1e9d7b4f6a2

Author: uDOS Engineering
Version: v1.0.0
Date: 2026-01-30
"""

import json
from pathlib import Path
from typing import Optional, Dict, Tuple
from datetime import datetime
import base64

from core.services.logging_api import get_logger, get_repo_root

logger = get_logger("identity-encryption")


class IdentityEncryption:
    """Handle encryption of sensitive identity fields (DOB) and starsign calculation."""

    # Zodiac signs with date ranges (month-day tuples)
    ZODIAC_SIGNS = [
        ("Capricorn", (12, 22), (1, 19)),
        ("Aquarius", (1, 20), (2, 18)),
        ("Pisces", (2, 19), (3, 20)),
        ("Aries", (3, 21), (4, 19)),
        ("Taurus", (4, 20), (5, 20)),
        ("Gemini", (5, 21), (6, 20)),
        ("Cancer", (6, 21), (7, 22)),
        ("Leo", (7, 23), (8, 22)),
        ("Virgo", (8, 23), (9, 22)),
        ("Libra", (9, 23), (10, 22)),
        ("Scorpio", (10, 23), (11, 21)),
        ("Sagittarius", (11, 22), (12, 21)),
    ]

    # Generational cohorts by birth year
    GENERATIONS = {
        "Pre-Boomer": (1900, 1945),
        "Boomer": (1946, 1964),
        "Gen X": (1965, 1980),
        "Millennial": (1981, 1996),
        "Gen Z": (1997, 2012),
        "Gen Alpha": (2013, 2025),
    }

    def __init__(self):
        """Initialize encryption module."""
        self.repo_root = get_repo_root()

    # ========================================================================
    # DOB Encryption (currently STUB - implement with cryptography lib)
    # ========================================================================

    def encrypt_dob(self, dob: str, key: str) -> str:
        """Encrypt DOB using WIZARD_KEY with AES-256-GCM.

        Args:
            dob: Date of birth as "YYYY-MM-DD"
            key: Encryption key (WIZARD_KEY from .env)

        Returns:
            Encrypted DOB (base64-encoded with nonce)
        """
        try:
            # Import cryptography library
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
            import base64
            import os
            
            # Derive 256-bit key from WIZARD_KEY using PBKDF2
            salt = b'udos-identity-salt-v1'  # Static salt for determinism
            kdf = PBKDF2(
                algorithm=hashes.SHA256(),
                length=32,  # 256 bits
                salt=salt,
                iterations=100000,
            )
            derived_key = kdf.derive(key.encode('utf-8'))
            
            # Generate random nonce (96 bits for GCM)
            nonce = os.urandom(12)
            
            # Encrypt with AES-GCM
            aesgcm = AESGCM(derived_key)
            ciphertext = aesgcm.encrypt(nonce, dob.encode('utf-8'), None)
            
            # Combine nonce + ciphertext and encode as base64
            encrypted_bytes = nonce + ciphertext
            encrypted_b64 = base64.b64encode(encrypted_bytes).decode('utf-8')
            
            logger.debug(f"[LOCAL] DOB encrypted with AES-256-GCM")
            return encrypted_b64

        except ImportError:
            # Fallback if cryptography library not installed
            logger.warning(f"[LOCAL] cryptography library not installed - storing DOB as plaintext")
            logger.warning(f"[LOCAL] Install with: pip install cryptography")
            return dob
            
        except Exception as e:
            logger.warning(f"[LOCAL] DOB encryption failed: {e} (returning plaintext)")
            return dob

    def decrypt_dob(self, encrypted: str, key: str) -> Optional[str]:
        """Decrypt DOB using WIZARD_KEY with AES-256-GCM.

        Args:
            encrypted: Encrypted DOB (base64-encoded with nonce)
            key: Decryption key (WIZARD_KEY from .env)

        Returns:
            Decrypted DOB as "YYYY-MM-DD", or None if decryption fails
        """
        try:
            # Import cryptography library
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
            import base64
            
            # If encrypted looks like plaintext DOB format, return as-is
            if len(encrypted) == 10 and encrypted.count('-') == 2:
                logger.debug(f"[LOCAL] Plaintext DOB detected, returning as-is")
                return encrypted
            
            # Derive 256-bit key from WIZARD_KEY using PBKDF2
            salt = b'udos-identity-salt-v1'  # Same static salt
            kdf = PBKDF2(
                algorithm=hashes.SHA256(),
                length=32,  # 256 bits
                salt=salt,
                iterations=100000,
            )
            derived_key = kdf.derive(key.encode('utf-8'))
            
            # Decode base64 and extract nonce + ciphertext
            encrypted_bytes = base64.b64decode(encrypted)
            nonce = encrypted_bytes[:12]  # First 12 bytes
            ciphertext = encrypted_bytes[12:]  # Rest is ciphertext
            
            # Decrypt with AES-GCM
            aesgcm = AESGCM(derived_key)
            plaintext_bytes = aesgcm.decrypt(nonce, ciphertext, None)
            dob = plaintext_bytes.decode('utf-8')
            
            logger.debug(f"[LOCAL] DOB decrypted with AES-256-GCM")
            return dob

        except ImportError:
            # Fallback if cryptography library not installed
            logger.warning(f"[LOCAL] cryptography library not installed - returning plaintext")
            return encrypted
            
        except Exception as e:
            logger.warning(f"[LOCAL] DOB decryption failed: {e}")
            return None

    # ========================================================================
    # Starsign & Generation Calculation
    # ========================================================================

    def get_starsign(self, dob: str) -> Optional[str]:
        """Get zodiac sign for a given DOB.

        Args:
            dob: Date of birth as "YYYY-MM-DD"

        Returns:
            Zodiac sign name (e.g., "Leo"), or None if DOB is invalid
        """
        try:
            date_obj = datetime.strptime(dob, "%Y-%m-%d")
            month = date_obj.month
            day = date_obj.day

            for sign_name, start, end in self.ZODIAC_SIGNS:
                start_month, start_day = start
                end_month, end_day = end

                # Handle wrap-around (Capricorn spans Dec-Jan)
                if start_month > end_month:
                    if (month == start_month and day >= start_day) or \
                       (month == end_month and day <= end_day):
                        return sign_name
                else:
                    if start_month <= month <= end_month:
                        if month == start_month and day < start_day:
                            continue
                        if month == end_month and day > end_day:
                            continue
                        return sign_name

            return None
        except Exception as e:
            logger.debug(f"[LOCAL] Failed to calculate starsign: {e}")
            return None

    def get_generation(self, dob: str) -> Optional[str]:
        """Get generational cohort for a given DOB.

        Args:
            dob: Date of birth as "YYYY-MM-DD"

        Returns:
            Generation name (e.g., "Millennial"), or None if DOB is invalid
        """
        try:
            date_obj = datetime.strptime(dob, "%Y-%m-%d")
            year = date_obj.year

            for gen_name, (start_year, end_year) in self.GENERATIONS.items():
                if start_year <= year <= end_year:
                    return gen_name

            return None
        except Exception as e:
            logger.debug(f"[LOCAL] Failed to calculate generation: {e}")
            return None

    def get_starsign_group(self, dob: str) -> Optional[str]:
        """Get combined starsign-generation group identifier.

        This groups users by astrological sign + generation for privacy-preserving
        segmentation and age-appropriate features.

        Args:
            dob: Date of birth as "YYYY-MM-DD"

        Returns:
            Group ID like "Leo-Millennial", or None if DOB is invalid
        """
        starsign = self.get_starsign(dob)
        generation = self.get_generation(dob)

        if starsign and generation:
            return f"{starsign}-{generation}"
        return None

    # ========================================================================
    # Identity Profile Enhancement
    # ========================================================================

    def enrich_identity(self, identity: Dict, location: str = None) -> Dict:
        """Add UDOS Crypt fields to identity (deterministic, non-secret).

        Args:
            identity: Identity dictionary with user_dob
            location: Location for profile ID generation (optional)

        Returns:
            Enriched identity copy with _crypt_* fields when possible
        """
        enriched = identity.copy()

        dob = identity.get("user_dob")
        if not dob:
            return enriched

        try:
            from core.services.udos_crypt import get_udos_crypt

            crypt = get_udos_crypt()
            components = crypt.get_crypt_components(dob)
            if components.get("crypt_id"):
                enriched["_crypt_id"] = components.get("crypt_id")
                enriched["_starsign"] = components.get("starsign")
                enriched["_color"] = components.get("color")
                enriched["_generation"] = components.get("generation")
                enriched["_animal"] = components.get("animal")
                enriched["_adjective"] = components.get("adjective")

                if location:
                    enriched["_profile_id"] = crypt.generate_profile_id(dob, location)
        except Exception as exc:
            logger.debug(f"[LOCAL] UDOS Crypt enrichment skipped: {exc}")

        return enriched

    def get_age(self, dob: str) -> Optional[int]:
        """Calculate age from DOB.

        Args:
            dob: Date of birth as "YYYY-MM-DD"

        Returns:
            Age in years, or None if DOB is invalid
        """
        try:
            date_obj = datetime.strptime(dob, "%Y-%m-%d")
            today = datetime.now()
            age = today.year - date_obj.year

            # Adjust if birthday hasn't occurred this year
            if (today.month, today.day) < (date_obj.month, date_obj.day):
                age -= 1

            return age
        except Exception as e:
            logger.debug(f"[LOCAL] Failed to calculate age: {e}")
            return None

    # ========================================================================
    # Status & Diagnostics
    # ========================================================================

    def print_identity_summary(self, identity: Dict, location: str = None) -> None:
        """Print formatted identity summary with UDOS Crypt encoding.

        Args:
            identity: Identity dictionary
            location: Location for profile ID (optional)
        """
        dob = identity.get('user_dob')
        if not dob:
            return

        enriched = self.enrich_identity(identity, location)

        print("\n👤 YOUR IDENTITY:\n")
        print(f"  Name: {identity.get('user_username', 'Not set')}")
        print(f"  DOB: {dob}")

        # UDOS Crypt identity
        if enriched.get('_crypt_id'):
            print(f"\n  🔐 UDOS Crypt ID: {enriched['_crypt_id']}")
            print(f"     Starsign: ♈ {enriched.get('_starsign', '?')} (→ {enriched.get('_color', '?')})")
            print(f"     Generation: {enriched.get('_generation', '?')} (→ {enriched.get('_animal', '?')})")
            print(f"     Rising: {enriched.get('_adjective', '?')}")

            if enriched.get('_profile_id'):
                print(f"     Profile ID: {enriched['_profile_id']}")

        age = self.get_age(dob)
        if age is not None:
            print(f"\n  Age: {age}")

        print(f"  Role: {identity.get('user_role', 'ghost')}")
        print(f"  Location: {identity.get('user_location', 'Not set')}")
        print(f"  Timezone: {identity.get('user_timezone', 'UTC')}")
        print()
