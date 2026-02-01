"""
ID Generator - uDOS ID Standard Implementation

Generates unique IDs for business intelligence entities following:
[a-z0-9-]+ format with semantic prefixes

ID Formats:
- biz-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx (Business)
- prs-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx (Person)
- rel-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx (Relationship)
- aud-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx (Audience)
- msg-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx (Message)

All IDs use UUIDv4 hex format (lowercase) with typed prefixes.
"""

import uuid


def generate_business_id() -> str:
    """Generate a unique business ID.
    
    Returns:
        str: Business ID in format biz-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
    
    Example:
        >>> generate_business_id()
        'biz-a13f9bca-2e7c-4e1e-a2a3-d9db8a3f90bf'
    """
    return f"biz-{uuid.uuid4()}"


def generate_person_id() -> str:
    """Generate a unique person ID.
    
    Returns:
        str: Person ID in format prs-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
    
    Example:
        >>> generate_person_id()
        'prs-f1ac03df-baaa-4b4e-b63f-95b2316761ab'
    """
    return f"prs-{uuid.uuid4()}"


def generate_relationship_id() -> str:
    """Generate a unique relationship ID for business-person connections.
    
    Returns:
        str: Relationship ID in format rel-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
    
    Example:
        >>> generate_relationship_id()
        'rel-3c8d9f21-4b7a-4e2c-9d1f-8a3b2c5d6e7f'
    """
    return f"rel-{uuid.uuid4()}"


def generate_audience_id() -> str:
    """Generate a unique audience metrics ID.
    
    Returns:
        str: Audience ID in format aud-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
    
    Example:
        >>> generate_audience_id()
        'aud-7e4f3a2b-1c9d-4e8f-a6b5-c3d2e1f0a9b8'
    """
    return f"aud-{uuid.uuid4()}"


def generate_message_id() -> str:
    """Generate a unique message ID for email tracking.
    
    Returns:
        str: Message ID in format msg-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
    
    Example:
        >>> generate_message_id()
        'msg-9b8a7c6d-5e4f-3a2b-1c0d-9e8f7a6b5c4d'
    """
    return f"msg-{uuid.uuid4()}"


def validate_id(id_string: str, prefix: str) -> bool:
    """Validate that an ID matches the uDOS ID Standard.
    
    Args:
        id_string: The ID to validate
        prefix: Expected prefix (biz, prs, rel, aud, msg)
    
    Returns:
        bool: True if valid, False otherwise
    
    Example:
        >>> validate_id('biz-a13f9bca-2e7c-4e1e-a2a3-d9db8a3f90bf', 'biz')
        True
        >>> validate_id('invalid-id', 'biz')
        False
    """
    if not id_string:
        return False
    
    # Check prefix
    if not id_string.startswith(f"{prefix}-"):
        return False
    
    # Extract UUID part
    uuid_part = id_string[len(prefix) + 1:]
    
    # Validate UUID format
    try:
        uuid.UUID(uuid_part)
        return True
    except ValueError:
        return False
