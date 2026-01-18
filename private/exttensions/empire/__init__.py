"""
Empire - Business Intelligence & CRM Extension

Unified CRM system integrating:
- Contact management (local SQLite)
- HubSpot free CRM synchronization
- Gmail contact extraction
- Google Business Profile integration
- Website parsing for staff directories
- Social media enrichment
- Email enrichment APIs
- Entity resolution

Data stored in: memory/bank/user/contacts.db
"""

from .empire import Empire
from .id_generator import (
    generate_business_id,
    generate_person_id,
    generate_relationship_id,
    generate_audience_id,
    generate_message_id,
    validate_id
)
from .marketing_db import MarketingDB
from .entity_resolver import EntityResolver
from .contact_extractor import ContactExtractor
from .message_pruner import MessagePruner
from .google_business_client import GoogleBusinessClient
from .website_parser import WebsiteParser
from .social_clients import (
    TwitterClient,
    InstagramGraphClient,
    SocialEnrichment,
    SocialProfile,
    InfluenceMetrics
)
from .enrichment_client import (
    ClearbitClient,
    HunterClient,
    PeopleDataLabsClient,
    EnrichmentService,
    EnrichedPerson,
    EnrichedCompany
)
from .keyword_generator import (
    KeywordGenerator,
    KeywordSet
)
from .location_resolver import (
    LocationResolver,
    LocationData
)

__all__ = [
    # Main Interface
    'Empire',
    
    # ID Generators
    'generate_business_id',
    'generate_person_id',
    'generate_relationship_id',
    'generate_audience_id',
    'generate_message_id',
    'validate_id',
    
    # Core Services
    'MarketingDB',
    'EntityResolver',
    'ContactExtractor',
    'MessagePruner',
    'GoogleBusinessClient',
    
    # Website & Social
    'WebsiteParser',
    'TwitterClient',
    'InstagramGraphClient',
    'SocialEnrichment',
    'SocialProfile',
    'InfluenceMetrics',
    
    # Enrichment
    'ClearbitClient',
    'HunterClient',
    'PeopleDataLabsClient',
    'EnrichmentService',
    'EnrichedPerson',
    'EnrichedCompany',
    
    # Workflow Automation
    'KeywordGenerator',
    'KeywordSet',
    'LocationResolver',
    'LocationData',
]
