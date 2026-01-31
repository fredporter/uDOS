"""
Form Field Validator - Enhanced Validation for Setup Forms

Provides robust validation for all setup form fields:
- Username: no spaces/special chars, min 3 chars, not reserved
- Date of Birth: YYYY-MM-DD format, not future, age-appropriate
- Timezone: IANA format or common aliases (AEST, EST, etc.)
- Location: city names, grid locations
- Role: admin, user, ghost only
- OS Type: alpine, ubuntu, mac, windows only
- Password: strength requirements (optional)

Author: uDOS Engineering
Version: v1.0.0
Date: 2026-01-31
"""

import re
from datetime import datetime, date
from typing import Tuple, Optional, List
from pathlib import Path

from core.services.logging_service import get_logger

logger = get_logger('form-validator')

# Reserved usernames that cannot be used
RESERVED_USERNAMES = {
    'root', 'admin', 'system', 'nobody', 'daemon', 'bin', 'sys', 'sync',
    'uucp', 'www-data', 'backup', 'list', 'irc', 'gnats', 'news', 'usx',
    'udp', 'proxy', 'www', 'test', 'guest', 'invalid', 'anonymous',
    'localhost', 'admin', 'wizard', 'udos', 'core'
}

# Timezone aliases mapping to IANA names
TIMEZONE_ALIASES = {
    'AEST': 'Australia/Sydney',
    'AEDT': 'Australia/Sydney',
    'ACST': 'Australia/Adelaide',
    'ACDT': 'Australia/Adelaide',
    'AWST': 'Australia/Perth',
    'AWDT': 'Australia/Perth',
    'EST': 'US/Eastern',
    'EDT': 'US/Eastern',
    'CST': 'US/Central',
    'CDT': 'US/Central',
    'MST': 'US/Mountain',
    'MDT': 'US/Mountain',
    'PST': 'US/Pacific',
    'PDT': 'US/Pacific',
    'GMT': 'Europe/London',
    'BST': 'Europe/London',
    'UTC': 'UTC',
    'CET': 'Europe/Paris',
    'CEST': 'Europe/Paris',
    'JST': 'Asia/Tokyo',
    'IST': 'Asia/Kolkata',
    'HKT': 'Asia/Hong_Kong',
    'SGT': 'Asia/Singapore',
    'NZST': 'Pacific/Auckland',
    'NZDT': 'Pacific/Auckland',
}

# Valid OS types
VALID_OS_TYPES = {'alpine', 'ubuntu', 'mac', 'windows'}

# Valid roles
VALID_ROLES = {'admin', 'user', 'ghost'}


class FormFieldValidator:
    """Enhanced validation for setup form fields."""

    @staticmethod
    def validate_username(value: str) -> Tuple[bool, Optional[str]]:
        """Validate username field.
        
        Rules:
        - 3-32 characters
        - Alphanumeric + underscore, hyphen only
        - Cannot be reserved name
        - Cannot start/end with hyphen or underscore
        - Case-insensitive check against reserved list
        
        Args:
            value: Username to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        value = str(value).strip() if value else ''
        
        if not value:
            return False, "Username cannot be blank"
        
        if len(value) < 3:
            return False, "Username must be at least 3 characters"
        
        if len(value) > 32:
            return False, "Username must be 32 characters or less"
        
        # Check format: alphanumeric, underscore, hyphen only
        if not re.match(r'^[a-zA-Z0-9_-]+$', value):
            return False, "Username can only contain letters, numbers, underscore, and hyphen"
        
        # Cannot start/end with hyphen or underscore
        if value[0] in '-_' or value[-1] in '-_':
            return False, "Username cannot start or end with hyphen or underscore"
        
        # Check reserved names (case-insensitive)
        if value.lower() in RESERVED_USERNAMES:
            return False, f"Username '{value}' is reserved and cannot be used"
        
        # Cannot have consecutive hyphens or underscores
        if re.search(r'[-_]{2,}', value):
            return False, "Username cannot have consecutive hyphens or underscores"
        
        logger.debug(f"[LOCAL] Username validation passed: {value}")
        return True, None

    @staticmethod
    def validate_dob(value: str) -> Tuple[bool, Optional[str]]:
        """Validate date of birth field.
        
        Rules:
        - YYYY-MM-DD format
        - Cannot be in future
        - Cannot be less than 5 years old (child protection)
        - Cannot be more than 150 years old (sanity check)
        
        Args:
            value: Date string to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        value = str(value).strip() if value else ''
        
        if not value:
            return False, "Date of birth cannot be blank"
        
        # Check format
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', value):
            return False, "Date must be in YYYY-MM-DD format (e.g., 1990-01-15)"
        
        try:
            dob = datetime.strptime(value, '%Y-%m-%d').date()
        except ValueError:
            return False, "Invalid date - please check day and month values"
        
        today = date.today()
        
        # Cannot be future date
        if dob > today:
            return False, "Date of birth cannot be in the future"
        
        # Age check: at least 5 years old
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        if age < 5:
            return False, "Must be at least 5 years old"
        
        # Sanity check: not more than 150 years old
        if age > 150:
            return False, "Date seems too far in the past - please verify"
        
        logger.debug(f"[LOCAL] DOB validation passed: {value} (age: {age})")
        return True, None

    @staticmethod
    def validate_timezone(value: str) -> Tuple[bool, Optional[str]]:
        """Validate timezone field.
        
        Rules:
        - Can be IANA format (e.g., America/Los_Angeles, Asia/Tokyo)
        - Can be common alias (AEST, EST, PST, etc.)
        - Case-insensitive for aliases
        - Must be recognized
        
        Args:
            value: Timezone string to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        value = str(value).strip() if value else ''
        
        if not value:
            return False, "Timezone cannot be blank"
        
        # Check if it's a known alias (case-insensitive)
        if value.upper() in TIMEZONE_ALIASES:
            iana_name = TIMEZONE_ALIASES[value.upper()]
            logger.debug(f"[LOCAL] Timezone validation passed: {value} → {iana_name}")
            return True, None
        
        # Check IANA format: Continent/City or UTC
        if value == 'UTC':
            return True, None
        
        # IANA format patterns: Must have at least one slash (Region/Zone)
        if '/' in value:
            if re.match(r'^[A-Z][a-zA-Z0-9_]*(/[A-Z][a-zA-Z0-9_]+)+$', value):
                # Valid IANA pattern match
                logger.debug(f"[LOCAL] Timezone validation passed (IANA pattern): {value}")
                return True, None
        
        # Show helpful error with suggestions
        similar = FormFieldValidator._find_similar_timezones(value)
        if similar:
            return False, f"Unknown timezone. Did you mean: {', '.join(similar)}?"
        
        return False, f"Unknown timezone. Try AEST, EST, PST, or IANA format like America/Los_Angeles"

    @staticmethod
    def validate_location(value: str) -> Tuple[bool, Optional[str]]:
        """Validate location field.
        
        Rules:
        - Cannot be blank
        - 2-100 characters
        - Can contain letters, numbers, spaces, hyphens, apostrophes
        - Cannot start/end with space
        
        Args:
            value: Location string to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        value = str(value).strip() if value else ''
        
        if not value:
            return False, "Location cannot be blank"
        
        if len(value) < 2:
            return False, "Location must be at least 2 characters"
        
        if len(value) > 100:
            return False, "Location must be 100 characters or less"
        
        # Allow letters, numbers, spaces, hyphens, apostrophes, commas
        if not re.match(r"^[a-zA-Z0-9\s\-',]+$", value):
            return False, "Location can only contain letters, numbers, spaces, hyphens, and apostrophes"
        
        # Check for excessive spaces
        if '  ' in value:
            return False, "Location should not have multiple consecutive spaces"
        
        logger.debug(f"[LOCAL] Location validation passed: {value}")
        return True, None

    @staticmethod
    def validate_role(value: str) -> Tuple[bool, Optional[str]]:
        """Validate role field.
        
        Rules:
        - Must be one of: admin, user, ghost
        - Case-insensitive
        
        Args:
            value: Role string to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        value = str(value).strip().lower() if value else ''
        
        if not value:
            return False, "Role cannot be blank"
        
        if value not in VALID_ROLES:
            return False, f"Invalid role. Choose from: {', '.join(VALID_ROLES)}"
        
        logger.debug(f"[LOCAL] Role validation passed: {value}")
        return True, None

    @staticmethod
    def validate_os_type(value: str) -> Tuple[bool, Optional[str]]:
        """Validate OS type field.
        
        Rules:
        - Must be one of: alpine, ubuntu, mac, windows
        - Case-insensitive
        
        Args:
            value: OS type string to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        value = str(value).strip().lower() if value else ''
        
        if not value:
            return False, "OS type cannot be blank"
        
        if value not in VALID_OS_TYPES:
            return False, f"Invalid OS type. Choose from: {', '.join(VALID_OS_TYPES)}"
        
        logger.debug(f"[LOCAL] OS type validation passed: {value}")
        return True, None

    @staticmethod
    def validate_password(value: str, required: bool = False) -> Tuple[bool, Optional[str]]:
        """Validate password field (optional).
        
        Rules:
        - If required: min 8 chars, at least 1 number, 1 lowercase, 1 uppercase
        - If optional: can be blank
        - Max 128 characters
        
        Args:
            value: Password string to validate
            required: Whether password is required
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        value = str(value).strip() if value else ''
        
        # Empty password is OK if not required
        if not value and not required:
            return True, None
        
        if not value and required:
            return False, "Password cannot be blank"
        
        if len(value) < 8:
            return False, "Password must be at least 8 characters"
        
        if len(value) > 128:
            return False, "Password must be 128 characters or less"
        
        # Check for at least one uppercase, lowercase, and number
        if not any(c.isupper() for c in value):
            return False, "Password must contain at least one uppercase letter"
        
        if not any(c.islower() for c in value):
            return False, "Password must contain at least one lowercase letter"
        
        if not any(c.isdigit() for c in value):
            return False, "Password must contain at least one number"
        
        logger.debug("[LOCAL] Password validation passed")
        return True, None

    @staticmethod
    def _find_similar_timezones(value: str, limit: int = 3) -> List[str]:
        """Find similar timezone aliases using simple substring matching.
        
        Args:
            value: User input
            limit: Max suggestions to return
            
        Returns:
            List of similar timezone aliases
        """
        value_upper = value.upper()
        similar = []
        
        for alias in TIMEZONE_ALIASES.keys():
            if value_upper in alias or alias.startswith(value_upper):
                similar.append(alias)
        
        return similar[:limit]

    @staticmethod
    def validate_generic_field(field_type: str, value: str, field_name: str = '') -> Tuple[bool, Optional[str]]:
        """Generic validator dispatcher based on field type/name.
        
        Args:
            field_type: Field type (text, select, etc.)
            value: Value to validate
            field_name: Field name (used to detect special fields)
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        field_name_lower = field_name.lower()
        value = str(value).strip() if value else ''
        
        # Detect field type from name if not explicit
        if 'username' in field_name_lower:
            return FormFieldValidator.validate_username(value)
        elif 'dob' in field_name_lower or 'birth' in field_name_lower or 'date' in field_name_lower:
            return FormFieldValidator.validate_dob(value)
        elif 'timezone' in field_name_lower or 'tz' in field_name_lower:
            return FormFieldValidator.validate_timezone(value)
        elif 'location' in field_name_lower or 'city' in field_name_lower:
            return FormFieldValidator.validate_location(value)
        elif 'role' in field_name_lower:
            return FormFieldValidator.validate_role(value)
        elif 'os' in field_name_lower or 'operating' in field_name_lower or 'system' in field_name_lower:
            return FormFieldValidator.validate_os_type(value)
        elif 'password' in field_name_lower or 'pwd' in field_name_lower:
            return FormFieldValidator.validate_password(value)
        else:
            # Generic: cannot be blank if required
            if not value:
                return False, "This field cannot be blank"
            return True, None
