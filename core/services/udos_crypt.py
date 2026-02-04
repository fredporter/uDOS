"""
UDOS Crypt System - 12x12x12 Identity Encoding
==============================================

Deterministic, privacy-respecting identity mapping:
  DOB -> starsign -> color
  DOB -> generation -> animal
  DOB -> day-of-year -> adjective

Reference: docs/specs/UDOS-CRYPT-SYSTEM.md
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional, Tuple, List
import hashlib


class UDOSCrypt:
    """Encode DOB into a deterministic, human-readable crypt ID."""

    ZODIAC_SIGNS: List[Tuple[str, Tuple[int, int], Tuple[int, int]]] = [
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

    STARSIGN_COLORS = {
        "Capricorn": "black",
        "Aquarius": "silver",
        "Pisces": "indigo",
        "Aries": "red",
        "Taurus": "green",
        "Gemini": "yellow",
        "Cancer": "pearl",
        "Leo": "gold",
        "Virgo": "cream",
        "Libra": "rose",
        "Scorpio": "blue",
        "Sagittarius": "purple",
    }

    GENERATIONS = [
        ("Pre-Boomer", (1900, 1945), "phoenix"),
        ("Boomer", (1946, 1964), "eagle"),
        ("Gen X", (1965, 1980), "wolf"),
        ("Millennial", (1981, 1996), "fox"),
        ("Gen Z", (1997, 2012), "owl"),
        ("Gen Alpha", (2013, 2025), "dolphin"),
        ("Gen Beta", (2026, 2041), "mongoose"),
        ("Gen Gamma", (2042, 2057), "raven"),
        ("Future1", (2058, 2073), "leopard"),
        ("Future2", (2074, 2089), "lynx"),
        ("Future3", (2090, 2105), "badger"),
        ("Future4", (2106, 2121), "hawk"),
    ]

    ADJECTIVES = [
        "swift",
        "steady",
        "adaptive",
        "bold",
        "grounded",
        "flowing",
        "nurturing",
        "creative",
        "analytical",
        "harmonious",
        "mysterious",
        "visionary",
    ]

    def validate_dob(self, dob: str) -> Tuple[bool, str]:
        """Validate DOB format and supported range."""
        try:
            date_obj = datetime.strptime(dob, "%Y-%m-%d")
        except Exception:
            return False, "Invalid DOB format (expected YYYY-MM-DD)"

        year = date_obj.year
        if year < 1900 or year > 2121:
            return False, "Invalid generation (year out of range)"

        starsign = self.get_starsign(dob)
        generation = self.get_generation(dob)
        if not starsign or not generation:
            return False, "Invalid DOB (starsign/generation not resolved)"

        return True, f"✅ Valid: {starsign} {generation}"

    def get_starsign(self, dob: str) -> Optional[str]:
        """Return zodiac sign for DOB."""
        try:
            date_obj = datetime.strptime(dob, "%Y-%m-%d")
        except Exception:
            return None

        month = date_obj.month
        day = date_obj.day

        for sign_name, start, end in self.ZODIAC_SIGNS:
            start_month, start_day = start
            end_month, end_day = end

            if start_month > end_month:
                if (month == start_month and day >= start_day) or (
                    month == end_month and day <= end_day
                ):
                    return sign_name
            else:
                if start_month <= month <= end_month:
                    if month == start_month and day < start_day:
                        continue
                    if month == end_month and day > end_day:
                        continue
                    return sign_name

        return None

    def get_generation(self, dob: str) -> Optional[str]:
        """Return generation name for DOB."""
        try:
            year = datetime.strptime(dob, "%Y-%m-%d").year
        except Exception:
            return None

        for name, (start, end), _animal in self.GENERATIONS:
            if start <= year <= end:
                return name
        return None

    def get_adjective(self, dob: str) -> Optional[str]:
        """Return adjective based on day-of-year modulo 12."""
        try:
            date_obj = datetime.strptime(dob, "%Y-%m-%d")
            day_of_year = int(date_obj.strftime("%j"))
            index = (day_of_year - 1) % 12
            return self.ADJECTIVES[index]
        except Exception:
            return None

    def encode_identity(self, dob: str) -> Optional[str]:
        """Return crypt ID (color-animal-adjective)."""
        components = self.get_crypt_components(dob)
        return components.get("crypt_id") if components else None

    def generate_profile_id(self, dob: str, location: str) -> Optional[str]:
        """Generate deterministic profile hash using DOB + location + crypt ID."""
        crypt_id = self.encode_identity(dob)
        if not crypt_id:
            return None
        seed = f"{dob}|{location}|{crypt_id}".encode("utf-8")
        digest = hashlib.sha256(seed).hexdigest()
        return digest[:16]

    def get_crypt_components(self, dob: str) -> Dict[str, Optional[str]]:
        """Return full crypt component breakdown."""
        starsign = self.get_starsign(dob)
        generation = self.get_generation(dob)
        adjective = self.get_adjective(dob)

        color = self.STARSIGN_COLORS.get(starsign) if starsign else None
        animal = None
        if generation:
            for name, _range, animal_name in self.GENERATIONS:
                if name == generation:
                    animal = animal_name
                    break

        crypt_id = None
        if color and animal and adjective:
            crypt_id = f"{color}-{animal}-{adjective}"

        return {
            "starsign": starsign,
            "color": color,
            "generation": generation,
            "animal": animal,
            "adjective": adjective,
            "crypt_id": crypt_id,
        }

    def print_crypt_tables(self) -> None:
        """Print reference tables to stdout."""
        print("STARSIGN → COLOR")
        for sign, color in self.STARSIGN_COLORS.items():
            print(f"  {sign:11} → {color}")

        print("\nGENERATION → ANIMAL")
        for name, (start, end), animal in self.GENERATIONS:
            print(f"  {name:11} ({start}-{end}) → {animal}")

        print("\nDAY-OF-YEAR → ADJECTIVE (mod 12)")
        for idx, adj in enumerate(self.ADJECTIVES):
            print(f"  {idx:2} → {adj}")


_udos_crypt_singleton: Optional[UDOSCrypt] = None


def get_udos_crypt() -> UDOSCrypt:
    """Return singleton UDOSCrypt instance."""
    global _udos_crypt_singleton
    if _udos_crypt_singleton is None:
        _udos_crypt_singleton = UDOSCrypt()
    return _udos_crypt_singleton
