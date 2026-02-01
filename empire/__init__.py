"""
BIZINTEL - Business Intelligence Module for uDOS Cloud Extension

Unified business intelligence system integrating:
- Gmail contact extraction
- Google Business Profile API scraping
- Website parsing for staff directories
- Social media enrichment (Twitter/X, Instagram)
- Email enrichment APIs (Clearbit, Hunter.io, PeopleDataLabs)
- Entity resolution (businesses, people, relationships)
- Message archiving and thread compression
- ID generation following uDOS ID Standard

Data stored in: memory/bank/user/contacts.db
"""

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
