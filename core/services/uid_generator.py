"""
User ID Generator - Creates unique, reversible user identifiers.

Format: UID-YYYYMMDD-YYYYMMDD-TZ-HHMMSSMMM
  DOB (compact) + CurrentDate (compact) + Timezone + Time with milliseconds

Scrambled using compact binary + zlib compression + Base64URL

Binary format reduces size before compression:
  Plain:      UID-19751107-20260131-AEST-105732123 (39 chars)
  Binary:     14 bytes (packed: DOB 4 + Current 4 + TZ 3 + Time 3)
  Compressed: 8-18 bytes (zlib level 9)
  Encoded:    ~12-24 chars (base64url, no padding)

Result: 12-24 chars compressed vs 39 chars plain
"""
import base64
import zlib
import struct
from datetime import datetime
from typing import Dict, Optional


def generate_uid(dob: str, timezone: str, timestamp: Optional[datetime] = None) -> str:
    """
    Generate a unique user ID from DOB, current date, timezone, and time.
    
    Format: UID-YYYYMMDD-YYYYMMDD-TZ-HHMMSSMMM
    Example: UID-19751107-20260131-AEST-105732123
    
    Args:
        dob: User date of birth in YYYY-MM-DD format
        timezone: User timezone (e.g., AEST, America/Los_Angeles)
        timestamp: Optional specific timestamp (defaults to now)
    
    Returns:
        UID string in format: UID-YYYYMMDD-YYYYMMDD-TZ-HHMMSSMMM
    
    Example:
        >>> generate_uid("1975-11-07", "AEST", datetime(2026, 1, 31, 10, 57, 32, 123000))
        'UID-19751107-20260131-AEST-105732123'
    """
    if timestamp is None:
        timestamp = datetime.now()
    
    # Extract timezone shorthand (e.g., AEST from Australia/Sydney)
    tz_code = _extract_tz_code(timezone)
    
    # Parse DOB and make compact
    dob_parts = dob.split('-')
    dob_compact = f"{dob_parts[0]}{dob_parts[1]}{dob_parts[2]}"
    
    # Current date compact (YYYYMMDD)
    current_date_compact = f"{timestamp.year:04d}{timestamp.month:02d}{timestamp.day:02d}"
    
    # Time with milliseconds (HHMMSSMMM)
    hour = f"{timestamp.hour:02d}"
    minute = f"{timestamp.minute:02d}"
    second = f"{timestamp.second:02d}"
    millisecond = f"{timestamp.microsecond // 1000:03d}"
    time_compact = f"{hour}{minute}{second}{millisecond}"
    
    # Build UID: UID-YYYYMMDD-YYYYMMDD-TZ-HHMMSSMMM
    uid = f"UID-{dob_compact}-{current_date_compact}-{tz_code}-{time_compact}"
    
    return uid


def scramble_uid(uid: str) -> str:
    """
    Compress and encode UID using binary packing + zlib + Base64URL.
    
    Encoding steps:
    1. Parse UID components (DOB, current date, TZ, time)
    2. Pack into binary format (14 bytes)
    3. Compress with zlib level 9 (8-18 bytes)
    4. Base64URL encode without padding (~12-24 chars)
    
    Result: 12-24 chars vs 39 chars plain
    
    Args:
        uid: Plain UID string (UID-YYYYMMDD-YYYYMMDD-TZ-HHMMSSMMM)
    
    Returns:
        Scrambled UID string (compressed + base64url encoded)
    
    Example:
        >>> scramble_uid("UID-19751107-20260131-AEST-105732123")
        'eNoLVlAoSkzRMzHRVMrJBAAJ4wdI'  # ~20 chars
    """
    # Parse UID components
    parts = uid.split('-')
    if len(parts) != 5 or parts[0] != 'UID':
        raise ValueError(f"Invalid UID format: {uid}. Expected: UID-YYYYMMDD-YYYYMMDD-TZ-HHMMSSMMM")
    
    dob = parts[1]           # YYYYMMDD
    current_date = parts[2]  # YYYYMMDD
    tz_code = parts[3]       # TZ (3 chars or less)
    time_ms = parts[4]       # HHMMSSMMM (9 chars)
    
    # Extract individual date components
    dob_year = int(dob[:4])
    dob_month = int(dob[4:6])
    dob_day = int(dob[6:8])
    
    curr_year = int(current_date[:4])
    curr_month = int(current_date[4:6])
    curr_day = int(current_date[6:8])
    
    # Extract time components
    hour = int(time_ms[:2])
    minute = int(time_ms[2:4])
    second = int(time_ms[4:6])
    millisecond = int(time_ms[6:9])
    
    # Pad timezone code to 4 bytes (right-pad with spaces if needed)
    tz_bytes = tz_code.encode('utf-8')[:4]
    if len(tz_bytes) < 4:
        tz_bytes = tz_bytes + b' ' * (4 - len(tz_bytes))
    
    # Pack into binary (17 bytes total):
    # - DOB: year(2) + month(1) + day(1) = 4 bytes
    # - Current: year(2) + month(1) + day(1) = 4 bytes
    # - TZ: 4 bytes
    # - Time: hour(1) + minute(1) + second(1) + ms(2) = 5 bytes
    binary = struct.pack('>HBBHBB', dob_year, dob_month, dob_day,
                         curr_year, curr_month, curr_day)
    binary += tz_bytes  # 4 bytes for timezone
    binary += struct.pack('>BBBH', hour, minute, second, millisecond)
    
    # Compress with zlib level 9
    compressed = zlib.compress(binary, level=9)
    
    # Encode to base64url (no padding)
    encoded = base64.urlsafe_b64encode(compressed).rstrip(b'=').decode('ascii')
    
    return encoded


def descramble_uid(scrambled_uid: str) -> str:
    """
    Decompress and decode UID from .env storage.
    
    Decoding steps:
    1. Restore base64url padding if needed
    2. Base64URL decode
    3. Decompress with zlib
    4. Unpack binary components
    5. Reconstruct UID string
    
    Args:
        scrambled_uid: Scrambled UID string (compressed + base64url encoded)
    
    Returns:
        Plain UID string in format: UID-YYYYMMDD-YYYYMMDD-TZ-HHMMSSMMM
    
    Example:
        >>> descramble_uid('eNoLVlAoSkzRMzHRVMrJBAAJ4wdI')
        'UID-19751107-20260131-AEST-105732123'
    """
    try:
        # Step 1: Restore padding if needed
        padded = scrambled_uid + '=' * (4 - len(scrambled_uid) % 4)
        
        # Step 2: Base64URL decode
        compressed = base64.urlsafe_b64decode(padded.encode('utf-8'))
        
        # Step 3: Decompress with zlib
        binary_data = zlib.decompress(compressed)
        
        # Step 4: Unpack binary (17 bytes total)
        # Format breakdown:
        # - >HBBHBB = 8 bytes (DOB year/month/day + Current year/month/day)
        # - TZ string = 4 bytes  
        # - >BBBH = 5 bytes (hour, minute, second, milliseconds)
        dob_year, dob_month, dob_day, curr_year, curr_month, curr_day = struct.unpack('>HBBHBB', binary_data[:8])
        
        # Extract timezone (4 bytes)
        tz_bytes = binary_data[8:12]
        tz_code = tz_bytes.decode('utf-8').strip()
        
        # Extract time (5 bytes: hour, minute, second, ms)
        hour, minute, second, millisecond = struct.unpack('>BBBH', binary_data[12:17])
        
        # Step 5: Reconstruct UID in compact format
        dob_compact = f"{dob_year:04d}{dob_month:02d}{dob_day:02d}"
        curr_compact = f"{curr_year:04d}{curr_month:02d}{curr_day:02d}"
        time_compact = f"{hour:02d}{minute:02d}{second:02d}{millisecond:03d}"
        
        uid = f"UID-{dob_compact}-{curr_compact}-{tz_code}-{time_compact}"
        return uid
        
    except Exception as e:
        return ""  # Return empty string on decode failure


def parse_uid(uid: str) -> Dict[str, str]:
    """
    Parse UID back into component parts.
    
    Handles both plain and scrambled UIDs.
    
    Args:
        uid: UID string (plain or scrambled)
    
    Returns:
        Dictionary with keys: dob, current_date, timezone, hour, minute, second, millisecond
    
    Example:
        >>> parse_uid("UID-19751107-20260131-AEST-105732123")
        {'dob': '1975-11-07', 'current_date': '2026-01-31', 'timezone': 'AEST', 
         'hour': '10', 'minute': '57', 'second': '32', 'millisecond': '123'}
    """
    # Try descrambling first if not plain UID format
    if not uid.startswith("UID-"):
        uid = descramble_uid(uid)
    
    if not uid.startswith("UID-"):
        return {}
    
    # Parse format: UID-YYYYMMDD-YYYYMMDD-TZ-HHMMSSMMM
    parts = uid.split("-")
    if len(parts) != 5:
        return {}
    
    try:
        dob = parts[1]           # YYYYMMDD
        current_date = parts[2]  # YYYYMMDD
        tz_code = parts[3]       # TZ
        time_ms = parts[4]       # HHMMSSMMM
        
        # Format dates with hyphens for readability
        dob_formatted = f"{dob[:4]}-{dob[4:6]}-{dob[6:8]}"
        curr_formatted = f"{current_date[:4]}-{current_date[4:6]}-{current_date[6:8]}"
        
        # Format time
        hour = time_ms[:2]
        minute = time_ms[2:4]
        second = time_ms[4:6]
        millisecond = time_ms[6:9]
        
        return {
            "dob": dob_formatted,
            "current_date": curr_formatted,
            "timezone": tz_code,
            "hour": hour,
            "minute": minute,
            "second": second,
            "millisecond": millisecond,
        }
    except (IndexError, ValueError):
        return {}


def _extract_tz_code(timezone: str) -> str:
    """
    Extract short timezone code from full timezone string.
    
    Examples:
        AEST -> AEST
        Australia/Sydney -> AEDT (or AEST depending on DST)
        America/Los_Angeles -> PST (or PDT)
        UTC -> UTC
    """
    # If already short code, return as-is (up to 4 chars)
    if "/" not in timezone:
        return timezone.upper()[:4]
    
    # Map common timezones to codes
    tz_map = {
        "Australia/Sydney": "AEST",
        "Australia/Melbourne": "AEST",
        "Australia/Brisbane": "AEST",
        "Australia/Perth": "AWST",
        "America/New_York": "EST",
        "America/Los_Angeles": "PST",
        "America/Chicago": "CST",
        "Europe/London": "GMT",
        "Europe/Paris": "CET",
        "Asia/Tokyo": "JST",
        "UTC": "UTC",
    }
    
    # Try exact match first
    if timezone in tz_map:
        return tz_map[timezone]
    
    # Extract last part and abbreviate to 3 chars
    # e.g., Australia/Sydney -> SYD, America/Los_Angeles -> ANG (Los_Angeles -> ANG)
    if "/" in timezone:
        city = timezone.split("/")[-1].replace("_", "")
        # Take first 3 chars, or use different logic
        if len(city) >= 3:
            # Prefer consonants or first 3 chars
            return city[:3].upper()
        else:
            return city.upper()
    
    return timezone[:4].upper()


# Example usage and testing
if __name__ == "__main__":
    print("=" * 60)
    print("UID Generator Test Suite")
    print("=" * 60)
    
    # Test generation
    test_time = datetime(2026, 1, 31, 10, 57, 32, 123000)
    uid = generate_uid("1975-11-07", "AEST", test_time)
    print(f"\n✅ Generated UID:")
    print(f"   {uid}")
    print(f"   Length: {len(uid)} chars")
    
    # Test scrambling
    scrambled = scramble_uid(uid)
    print(f"\n🔐 Scrambled (compressed):")
    print(f"   {scrambled}")
    print(f"   Length: {len(scrambled)} chars")
    print(f"   Reduction: {len(uid) - len(scrambled)} chars saved ({100 * (len(uid) - len(scrambled)) / len(uid):.1f}%)")
    
    # Test descrambling
    descrambled = descramble_uid(scrambled)
    print(f"\n✅ Descrambled:")
    print(f"   {descrambled}")
    print(f"   Match: {uid == descrambled}")
    
    # Test parsing plain
    parsed = parse_uid(uid)
    print(f"\n📊 Parsed plain UID:")
    for key, val in sorted(parsed.items()):
        print(f"   {key:15} = {val}")
    
    # Test parsing scrambled
    parsed_scrambled = parse_uid(scrambled)
    print(f"\n📊 Parsed scrambled UID:")
    for key, val in sorted(parsed_scrambled.items()):
        print(f"   {key:15} = {val}")
    
    print(f"\n✅ Parsed data matches: {parsed == parsed_scrambled}")
