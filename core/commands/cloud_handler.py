"""
Cloud Command Handler - Business Intelligence Commands

Unified command interface for BIZINTEL system:
- CLOUD EMAIL SYNC - Process Gmail messages and extract contacts
- CLOUD CONTACTS LIST - List people and their businesses
- CLOUD BUSINESS SEARCH - Search Google Places API
- CLOUD BUSINESS LIST - List all businesses
- CLOUD LINK - Manually link message/person/business
- CLOUD PRUNE - Archive old messages
- CLOUD EXPORT - Export to CSV/JSON

Integrates:
- extensions/cloud/bizintel/marketing_db.py - Data storage
- extensions/cloud/bizintel/contact_extractor.py - Email parsing
- extensions/cloud/bizintel/entity_resolver.py - Deduplication
- extensions/cloud/bizintel/google_business_client.py - Places API
- extensions/cloud/bizintel/message_pruner.py - Message archiving
"""

import os
import sys
import json
import csv
from pathlib import Path
from typing import List, Dict

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.commands.base_handler import BaseCommandHandler


class CloudHandler(BaseCommandHandler):
    """Handle CLOUD commands for business intelligence."""
    
    def __init__(self, **kwargs):
        """Initialize cloud handler."""
        super().__init__(**kwargs)
        
        # Lazy load bizintel modules
        self.db = None
        self.extractor = None
        self.resolver = None
        self.pruner = None
        self.google_client = None
    
    def _ensure_initialized(self):
        """Lazy load bizintel modules."""
        if self.db is None:
            from extensions.cloud.bizintel.marketing_db import MarketingDB
            from extensions.cloud.bizintel.contact_extractor import ContactExtractor
            from extensions.cloud.bizintel.entity_resolver import EntityResolver
            from extensions.cloud.bizintel.message_pruner import MessagePruner
            from extensions.cloud.bizintel.google_business_client import GoogleBusinessClient
            
            self.db = MarketingDB()
            self.extractor = ContactExtractor(self.db)
            self.resolver = EntityResolver(self.db)
            self.pruner = MessagePruner(self.db)
            self.google_client = GoogleBusinessClient()
    
    def handle_command(self, params: List[str]) -> str:
        """Route CLOUD subcommands.
        
        Args:
            params: Command parameters [CLOUD, subcommand, ...args]
        
        Returns:
            Command output
        """
        if len(params) < 2:
            return self._show_usage()
        
        subcommand = params[1].upper()
        args = params[2:] if len(params) > 2 else []
        
        if subcommand == 'EMAIL':
            return self._handle_email(args)
        elif subcommand == 'CONTACTS':
            return self._handle_contacts(args)
        elif subcommand == 'BUSINESS':
            return self._handle_business(args)
        elif subcommand == 'LINK':
            return self._handle_link(args)
        elif subcommand == 'PRUNE':
            return self._handle_prune(args)
        elif subcommand == 'EXPORT':
            return self._handle_export(args)
        elif subcommand == 'STATS':
            return self._handle_stats(args)
        elif subcommand == 'WEBSITE':
            return self._handle_website(args)
        elif subcommand == 'SOCIAL':
            return self._handle_social(args)
        elif subcommand == 'ENRICH':
            return self._handle_enrich(args)
        elif subcommand == 'GENERATE':
            return self._handle_generate(args)
        elif subcommand == 'RESOLVE':
            return self._handle_resolve(args)
        else:
            return f"Unknown subcommand: {subcommand}\n\n{self._show_usage()}"
    
    def _handle_email(self, args: List[str]) -> str:
        """Handle CLOUD EMAIL subcommands.
        
        Args:
            args: [SYNC]
        
        Returns:
            Command output
        """
        if not args:
            return "Usage: CLOUD EMAIL SYNC"
        
        action = args[0].upper()
        
        if action == 'SYNC':
            self._ensure_initialized()
            
            # TODO: Integrate with actual Gmail service
            # For now, show example of how it would work
            return """
📧 Gmail Contact Extraction
           
To sync Gmail messages:
1. Ensure Gmail authentication is set up (see: wiki/Google-Cloud-Sync.md)
2. Run: EMAIL LIST to fetch recent messages
3. Messages will be automatically processed by BIZINTEL

Contact extraction will:
- Filter system emails (noreply@, notifications)
- Parse sender information and signatures
- Detect businesses from email domains
- Generate biz-*/prs-* IDs
- Link messages to contacts
- Auto-prune old messages (keep 4 most recent per thread)

Status: BIZINTEL ready, awaiting Gmail service integration
"""
        
        return f"Unknown email action: {action}"
    
    def _handle_contacts(self, args: List[str]) -> str:
        """Handle CLOUD CONTACTS subcommands.
        
        Args:
            args: [LIST, --business <biz_id>]
        
        Returns:
            Command output
        """
        self._ensure_initialized()
        
        if not args or args[0].upper() == 'LIST':
            # Parse flags
            business_id = None
            if '--business' in args:
                idx = args.index('--business')
                if idx + 1 < len(args):
                    business_id = args[idx + 1]
            
            if business_id:
                # List contacts for specific business
                relationships = self.db.get_relationships_for_business(business_id)
                
                if not relationships:
                    return f"No contacts found for business: {business_id}"
                
                output = [f"📇 Contacts for {business_id}\n"]
                for rel in relationships:
                    output.append(f"{rel['full_name']}")
                    if rel.get('primary_email'):
                        output.append(f"  📧 {rel['primary_email']}")
                    if rel.get('phone'):
                        output.append(f"  📞 {rel['phone']}")
                    if rel.get('role_title'):
                        output.append(f"  💼 {rel['role_title']}")
                    output.append("")
                
                return '\n'.join(output)
            else:
                # List all people
                people = self.db.list_people(limit=50)
                
                if not people:
                    return "No contacts found.\n\nRun: CLOUD EMAIL SYNC to extract contacts from Gmail"
                
                output = [f"📇 Contacts ({len(people)})\n"]
                for person in people:
                    output.append(f"{person['full_name']}")
                    if person.get('primary_email'):
                        output.append(f"  📧 {person['primary_email']}")
                    if person.get('job_title'):
                        output.append(f"  💼 {person['job_title']}")
                    if person.get('company_name'):
                        output.append(f"  🏢 {person['company_name']}")
                    output.append("")
                
                return '\n'.join(output)
        
        return "Usage: CLOUD CONTACTS LIST [--business <biz_id>]"
    
    def _handle_business(self, args: List[str]) -> str:
        """Handle CLOUD BUSINESS subcommands.
        
        Args:
            args: [SEARCH <query> | LIST]
        
        Returns:
            Command output
        """
        self._ensure_initialized()
        
        if not args:
            return "Usage: CLOUD BUSINESS [SEARCH <query> | LIST]"
        
        action = args[0].upper()
        
        if action == 'SEARCH':
            if len(args) < 2:
                return "Usage: CLOUD BUSINESS SEARCH <query> [--location TILE]"
            
            query = ' '.join([a for a in args[1:] if not a.startswith('--')])
            
            # Parse location flag
            location = None
            if '--location' in args:
                idx = args.index('--location')
                if idx + 1 < len(args):
                    location = args[idx + 1]
            
            # Search Google Places
            results = self.google_client.search_businesses(query, location)
            
            if not results:
                return f"No businesses found for: {query}"
            
            output = [f"🔍 Found {len(results)} business(es)\n"]
            
            for i, biz in enumerate(results, 1):
                output.append(f"{i}. {biz['name']}")
                if biz.get('raw_address'):
                    output.append(f"   📍 {biz['raw_address']}")
                if biz.get('phone'):
                    output.append(f"   📞 {biz['phone']}")
                if biz.get('website'):
                    output.append(f"   🌐 {biz['website']}")
                if biz.get('rating'):
                    output.append(f"   ⭐ {biz['rating']} ({biz.get('review_count', 0)} reviews)")
                
                # Check if already in database
                existing = self.db.find_business_by_google_place_id(biz['google_place_id'])
                if existing:
                    output.append(f"   ✅ In database: {existing['business_id']}")
                else:
                    # Auto-import
                    business_id = self.resolver.resolve_or_create_business(**biz)
                    output.append(f"   ➕ Added to database: {business_id}")
                
                output.append("")
            
            return '\n'.join(output)
        
        elif action == 'LIST':
            businesses = self.db.list_businesses(limit=50)
            
            if not businesses:
                return "No businesses found.\n\nRun: CLOUD BUSINESS SEARCH <query> to find businesses"
            
            output = [f"🏢 Businesses ({len(businesses)})\n"]
            
            for biz in businesses:
                output.append(f"{biz['name']}")
                output.append(f"  ID: {biz['business_id']}")
                if biz.get('raw_address'):
                    output.append(f"  📍 {biz['raw_address']}")
                if biz.get('website'):
                    output.append(f"  🌐 {biz['website']}")
                if biz.get('source'):
                    output.append(f"  📥 Source: {biz['source']}")
                output.append("")
            
            return '\n'.join(output)
        
        return "Usage: CLOUD BUSINESS [SEARCH <query> | LIST]"
    
    def _handle_link(self, args: List[str]) -> str:
        """Handle CLOUD LINK command.
        
        Args:
            args: [MSG <msg_id> TO <biz_id|prs_id>]
        
        Returns:
            Command output
        """
        self._ensure_initialized()
        
        if len(args) < 4:
            return "Usage: CLOUD LINK MSG <msg_id> TO <biz_id|prs_id>"
        
        if args[0].upper() != 'MSG':
            return "Only MSG linking supported for now"
        
        msg_id = args[1]
        target_id = args[3]
        
        # Determine target type
        if target_id.startswith('biz-'):
            success = self.db.link_message_to_business(msg_id, target_id)
            if success:
                return f"✅ Linked message {msg_id} to business {target_id}"
            return f"❌ Failed to link (check IDs exist)"
        
        elif target_id.startswith('prs-'):
            success = self.db.link_message_to_person(msg_id, target_id)
            if success:
                return f"✅ Linked message {msg_id} to person {target_id}"
            return f"❌ Failed to link (check IDs exist)"
        
        return f"Unknown ID type: {target_id} (expected biz-* or prs-*)"
    
    def _handle_prune(self, args: List[str]) -> str:
        """Handle CLOUD PRUNE command.
        
        Args:
            args: []
        
        Returns:
            Command output
        """
        self._ensure_initialized()
        
        stats = self.pruner.prune_all_threads()
        
        output = [
            "🗑️ Message Pruning Complete\n",
            f"Threads processed: {stats['threads']}",
            f"Messages kept: {stats['kept']}",
            f"Messages archived: {stats['archived']}",
            f"Messages compressed: {stats['compressed']}\n"
        ]
        
        # Show archive stats
        archive_stats = self.pruner.get_archive_stats()
        output.append(f"Archive: {archive_stats['messages']} messages in {archive_stats['threads']} threads ({archive_stats['size_mb']} MB)")
        
        return '\n'.join(output)
    
    def _handle_export(self, args: List[str]) -> str:
        """Handle CLOUD EXPORT command.
        
        Args:
            args: [CSV|JSON] [businesses|people|contacts]
        
        Returns:
            Command output
        """
        self._ensure_initialized()
        
        if len(args) < 2:
            return "Usage: CLOUD EXPORT [CSV|JSON] [businesses|people|contacts]"
        
        format_type = args[0].upper()
        data_type = args[1].lower()
        
        # Get data
        if data_type == 'businesses':
            data = self.db.list_businesses(limit=1000)
        elif data_type == 'people':
            data = self.db.list_people(limit=1000)
        elif data_type == 'contacts':
            # Combined export with relationships
            data = []
            people = self.db.list_people(limit=1000)
            for person in people:
                rels = self.db.get_relationships_for_person(person['person_id'])
                person['businesses'] = [{'name': r['name'], 'role': r.get('role_title')} for r in rels]
                data.append(person)
        else:
            return f"Unknown data type: {data_type} (use: businesses, people, contacts)"
        
        # Export
        project_root = Path(__file__).parent.parent.parent
        export_dir = project_root / "memory" / "bank" / "user" / "exports"
        export_dir.mkdir(parents=True, exist_ok=True)
        
        if format_type == 'CSV':
            filepath = export_dir / f"{data_type}.csv"
            
            if not data:
                return f"No data to export for: {data_type}"
            
            with open(filepath, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            
            return f"✅ Exported {len(data)} records to: {filepath}"
        
        elif format_type == 'JSON':
            filepath = export_dir / f"{data_type}.json"
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            return f"✅ Exported {len(data)} records to: {filepath}"
        
        return f"Unknown format: {format_type} (use: CSV, JSON)"
    
    def _handle_stats(self, args: List[str]) -> str:
        """Handle CLOUD STATS command.
        
        Returns:
            Database statistics
        """
        self._ensure_initialized()
        
        cursor = self.db.conn.cursor()
        
        # Count records
        cursor.execute("SELECT COUNT(*) FROM businesses")
        business_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM people")
        people_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM business_person_roles")
        relationship_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM messages WHERE is_archived = 0")
        message_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM messages WHERE is_archived = 1")
        archived_count = cursor.fetchone()[0]
        
        # Archive stats
        archive_stats = self.pruner.get_archive_stats()
        
        output = [
            "📊 BIZINTEL Statistics\n",
            f"Businesses: {business_count}",
            f"People: {people_count}",
            f"Relationships: {relationship_count}",
            f"Messages (active): {message_count}",
            f"Messages (archived): {archived_count}\n",
            f"Archive: {archive_stats['threads']} threads, {archive_stats['size_mb']} MB\n",
            f"Database: {self.db.db_path}"
        ]
        
        return '\n'.join(output)
    
    def _handle_website(self, args: List[str]) -> str:
        """Handle CLOUD WEBSITE PARSE command.
        
        Args:
            args: [PARSE, url, business_id (optional)]
        
        Returns:
            Website parsing results
        """
        self._ensure_initialized()
        
        if len(args) < 2 or args[0].upper() != 'PARSE':
            return "Usage: CLOUD WEBSITE PARSE <url> [business_id]"
        
        url = args[1]
        business_id = args[2] if len(args) > 2 else None
        
        try:
            from extensions.cloud.bizintel.website_parser import WebsiteParser
            
            parser = WebsiteParser()
            result = parser.parse_website(url)
            
            output = [
                f"\n✅ Parsed website: {url}",
                f"   Found {len(result['staff'])} staff members",
                f"   Found {len(result['contacts'])} contact emails",
                f"   Found {len(result['team_pages_found'])} team pages",
                ""
            ]
            
            # Import staff members
            for staff_data in result['staff']:
                # Create or resolve person
                person_data = {
                    'email': staff_data.get('email'),
                    'name': staff_data['name']
                }
                person_id = self.resolver.resolve_or_create_person(person_data)
                
                # Create role
                if business_id and staff_data.get('role'):
                    role_category = staff_data['role']  # Already normalized
                    self.db.create_role(
                        person_id=person_id,
                        business_id=business_id,
                        role_category=role_category,
                        role_title=staff_data.get('role'),
                        source='website_parse'
                    )
                
                output.append(f"   ✓ {staff_data['name']} - {staff_data.get('role', 'Unknown role')}")
            
            # Import contacts
            for contact_data in result['contacts']:
                output.append(f"   📧 {contact_data['type']}: {contact_data['email']}")
            
            return '\n'.join(output)
        
        except Exception as e:
            return f"Error parsing website: {str(e)}"
    
    def _handle_social(self, args: List[str]) -> str:
        """Handle CLOUD SOCIAL commands.
        
        Args:
            args: [ENRICH|SEARCH, twitter|instagram, handle/query]
        
        Returns:
            Social media data
        """
        self._ensure_initialized()
        
        if len(args) < 3:
            return "Usage: CLOUD SOCIAL ENRICH twitter <handle>\n       CLOUD SOCIAL ENRICH instagram <account_id>"
        
        action = args[0].upper()
        platform = args[1].lower()
        handle = args[2]
        
        try:
            from extensions.cloud.bizintel.social_clients import SocialEnrichment
            
            enrichment = SocialEnrichment()
            
            if action == 'ENRICH':
                if platform == 'twitter':
                    profile = enrichment.twitter.get_user_by_username(handle)
                    if profile:
                        output = [
                            f"\n✅ Twitter profile: @{profile.username}",
                            f"   Name: {profile.display_name}",
                            f"   Bio: {profile.bio}",
                            f"   Followers: {profile.followers_count:,}",
                            f"   Following: {profile.following_count:,}",
                            f"   Verified: {profile.verified}",
                            f"   URL: {profile.profile_url}",
                        ]
                        
                        # Optionally link to business/person
                        # Store social profile in database
                        
                        return '\n'.join(output)
                    else:
                        return f"❌ Twitter user not found: {handle}"
                
                elif platform == 'instagram':
                    profile = enrichment.instagram.get_profile(handle)
                    if profile:
                        output = [
                            f"\n✅ Instagram profile: @{profile.username}",
                            f"   Name: {profile.display_name}",
                            f"   Bio: {profile.bio}",
                            f"   Followers: {profile.followers_count:,}",
                            f"   URL: {profile.profile_url}",
                        ]
                        return '\n'.join(output)
                    else:
                        return f"❌ Instagram account not found: {handle}"
            
            return f"Unknown action: {action}"
        
        except Exception as e:
            return f"Error enriching social profile: {str(e)}"
    
    def _handle_enrich(self, args: List[str]) -> str:
        """Handle CLOUD ENRICH commands.
        
        Args:
            args: [EMAIL|DOMAIN, email/domain]
        
        Returns:
            Enrichment data
        """
        self._ensure_initialized()
        
        if len(args) < 2:
            return "Usage: CLOUD ENRICH EMAIL <email>\n       CLOUD ENRICH DOMAIN <domain>\n       CLOUD ENRICH STAFF <domain>"
        
        lookup_type = args[0].upper()
        lookup_value = args[1]
        
        try:
            from extensions.cloud.bizintel.enrichment_client import EnrichmentService
            import json as json_lib
            
            enrichment = EnrichmentService()
            
            # Check cache first
            cached = self.db.get_cached_enrichment(lookup_value)
            if cached:
                output = [f"✅ Found in cache (hit #{cached['hit_count']})"]
                data = json_lib.loads(cached['response_data'])
            else:
                data = None
            
            if lookup_type == 'EMAIL':
                if not cached:
                    enriched = enrichment.enrich_person_with_fallback(lookup_value)
                    if enriched:
                        # Cache result
                        self.db.cache_enrichment(
                            lookup_key=lookup_value,
                            lookup_type='person',
                            provider='cascade',
                            response_data=json_lib.dumps(enriched.__dict__)
                        )
                        data = enriched.__dict__
                
                if data:
                    output = [
                        f"\n✅ Enriched person: {lookup_value}",
                        f"   Name: {data.get('name', 'Unknown')}",
                        f"   Title: {data.get('job_title', 'Unknown')}",
                        f"   Company: {data.get('company_name', 'Unknown')}",
                        f"   LinkedIn: {data.get('linkedin_url', 'N/A')}",
                        f"   Twitter: @{data.get('twitter_handle', 'N/A')}",
                        f"   Verified: {data.get('verified', False)}",
                    ]
                    return '\n'.join(output)
                else:
                    return f"❌ No enrichment data found for: {lookup_value}"
            
            elif lookup_type == 'DOMAIN':
                if not cached:
                    enriched = enrichment.enrich_company_with_fallback(lookup_value)
                    if enriched:
                        self.db.cache_enrichment(
                            lookup_key=lookup_value,
                            lookup_type='company',
                            provider='cascade',
                            response_data=json_lib.dumps(enriched.__dict__)
                        )
                        data = enriched.__dict__
                
                if data:
                    output = [
                        f"\n✅ Enriched company: {lookup_value}",
                        f"   Name: {data.get('name', 'Unknown')}",
                        f"   Industry: {data.get('industry', 'Unknown')}",
                        f"   Employees: {data.get('employee_count', 'Unknown')}",
                        f"   Location: {data.get('location', 'Unknown')}",
                        f"   Description: {data.get('description', 'N/A')[:100]}...",
                    ]
                    return '\n'.join(output)
                else:
                    return f"❌ No enrichment data found for: {lookup_value}"
            
            elif lookup_type == 'STAFF':
                # Find staff emails for domain
                staff_list = enrichment.find_staff_emails(lookup_value, limit=20)
                
                if staff_list:
                    output = [
                        f"\n✅ Found {len(staff_list)} staff members for {lookup_value}:",
                        ""
                    ]
                    
                    for person in staff_list:
                        output.append(f"   {person.email}")
                        if person.name:
                            output.append(f"      Name: {person.name}")
                        if person.job_title:
                            output.append(f"      Title: {person.job_title}")
                        output.append("")
                    
                    return '\n'.join(output)
                else:
                    return f"❌ No staff found for domain: {lookup_value}"
            else:
                return f"❌ Unknown enrichment type: {lookup_type}"
                    
        except Exception as e:
            return f"Error enriching data: {str(e)}"
    
    def _handle_generate(self, args: List[str]) -> str:
        """Handle CLOUD GENERATE KEYWORDS command.
        
        Args:
            args: [KEYWORDS, industry, --location location, --type business_type]
        
        Returns:
            Generated keywords for workflow automation
        """
        self._ensure_initialized()
        
        if len(args) < 2 or args[0].upper() != 'KEYWORDS':
            return "Usage: CLOUD GENERATE KEYWORDS <industry> [--location <location>] [--type <business_type>] [--upy]"
        
        industry = args[1]
        location_context = None
        business_type = None
        export_upy = '--upy' in args
        
        # Parse optional arguments
        i = 2
        while i < len(args):
            if args[i] == '--location' and i + 1 < len(args):
                location_context = args[i + 1]
                i += 2
            elif args[i] == '--type' and i + 1 < len(args):
                business_type = args[i + 1]
                i += 2
            else:
                i += 1
        
        try:
            # Import keyword generator
            from extensions.cloud.bizintel.keyword_generator import KeywordGenerator
            
            generator = KeywordGenerator()
            keyword_set = generator.generate_keywords(
                industry=industry,
                location_context=location_context,
                business_type=business_type
            )
            
            if not keyword_set:
                return "❌ Failed to generate keywords"
            
            # Export as uPY variables if requested
            if export_upy:
                return "\n" + generator.export_for_upy(keyword_set)
            
            # Otherwise, display formatted output
            output = [
                f"\n✅ Generated keywords for: {industry}",
                ""
            ]
            
            if keyword_set.primary_keywords:
                output.append(f"Primary Keywords ({len(keyword_set.primary_keywords)}):")
                for kw in keyword_set.primary_keywords[:10]:
                    output.append(f"   • {kw}")
                output.append("")
            
            if keyword_set.location_variants:
                output.append(f"Location Variants ({len(keyword_set.location_variants)}):")
                for kw in keyword_set.location_variants[:5]:
                    output.append(f"   • {kw}")
                output.append("")
            
            if keyword_set.industry_terms:
                output.append(f"Industry Terms ({len(keyword_set.industry_terms)}):")
                for kw in keyword_set.industry_terms[:5]:
                    output.append(f"   • {kw}")
                output.append("")
            
            output.append(f"Source: {keyword_set.context.get('source', 'unknown')}")
            output.append("")
            output.append("Tip: Add --upy to export for workflow automation")
            
            return '\n'.join(output)
        
        except Exception as e:
            return f"Error generating keywords: {str(e)}"
    
    def _handle_resolve(self, args: List[str]) -> str:
        """Handle CLOUD RESOLVE LOCATION command.
        
        Args:
            args: [LOCATION, address, --layer layer, --upy]
        
        Returns:
            Resolved TILE code and MeshCore position
        """
        self._ensure_initialized()
        
        if len(args) < 2 or args[0].upper() != 'LOCATION':
            return "Usage: CLOUD RESOLVE LOCATION <address> [--layer <100-500>] [--upy]"
        
        # Join address parts (may contain spaces)
        address_parts = []
        layer = 300  # Default to city layer
        export_upy = '--upy' in args
        
        i = 1
        while i < len(args):
            if args[i] == '--layer' and i + 1 < len(args):
                layer = int(args[i + 1])
                i += 2
            elif args[i] == '--upy':
                i += 1
            else:
                address_parts.append(args[i])
                i += 1
        
        address = ' '.join(address_parts)
        
        if not address:
            return "Error: No address provided"
        
        try:
            from extensions.cloud.bizintel.location_resolver import LocationResolver
            
            resolver = LocationResolver()
            location_data = resolver.resolve_address(address, preferred_layer=layer)
            
            if not location_data:
                return f"❌ Could not resolve address: {address}"
            
            if export_upy:
                # Export as uPY variables
                return "\n" + resolver.format_for_upy(location_data)
            else:
                # Human-readable output
                output = [
                    f"\n✅ Resolved location: {location_data.address}",
                    "",
                    f"📍 Coordinates: {location_data.lat:.6f}, {location_data.lon:.6f}",
                    f"🗺️  TILE Code: {location_data.tile_code}",
                    f"🗺️  Full TILE: {location_data.tile_code_full}",
                    f"📐 Layer: {location_data.layer} (cell size: {location_data.meshcore_position['cell_size_m']}m)",
                    "",
                    f"🔌 MeshCore Position:",
                    f"   Grid X: {location_data.meshcore_position['grid_x']}",
                    f"   Grid Y: {location_data.meshcore_position['grid_y']}",
                    f"   Layer: {location_data.meshcore_position['layer']}",
                    "",
                    f"Confidence: {location_data.confidence}",
                    "",
                    "Tip: Add --upy to export for workflow automation"
                ]
                
                return '\n'.join(output)
        
        except Exception as e:
            return f"Error resolving location: {str(e)}"
    
    def _show_usage(self) -> str:
        """Show CLOUD command usage."""
        return """
╔══════════════════════════════════════════════════════════════╗
║  CLOUD BIZINTEL - Business Intelligence System               ║
╚══════════════════════════════════════════════════════════════╝

EMAIL & CONTACTS
  CLOUD EMAIL SYNC                    Extract contacts from Gmail
  CLOUD CONTACTS LIST                 List all people
  CLOUD CONTACTS LIST --business <id> List contacts for business

BUSINESS SEARCH
  CLOUD BUSINESS SEARCH <query>       Search Google Places API
  CLOUD BUSINESS LIST                 List all businesses

WEBSITE PARSING (robots.txt compliant)
  CLOUD WEBSITE PARSE <url> [biz_id]  Extract staff & contacts from website

SOCIAL MEDIA ENRICHMENT
  CLOUD SOCIAL ENRICH twitter <handle>        Get Twitter profile
  CLOUD SOCIAL ENRICH instagram <account_id>  Get Instagram data

EMAIL ENRICHMENT (Clearbit/Hunter.io/PDL)
  CLOUD ENRICH EMAIL <email>          Enrich person data
  CLOUD ENRICH DOMAIN <domain>        Enrich company data
  CLOUD ENRICH STAFF <domain>         Find staff emails

WORKFLOW AUTOMATION
  CLOUD GENERATE KEYWORDS <industry> [--location <loc>] [--upy]
                                      Generate search keywords with Gemini AI
  CLOUD RESOLVE LOCATION <address> [--layer <100-500>] [--upy]
                                      Convert address to TILE code + MeshCore position

DATA MANAGEMENT
  CLOUD LINK MSG <msg_id> TO <id>     Link message to person/business
  CLOUD PRUNE                         Archive old messages
  CLOUD EXPORT CSV|JSON <type>        Export data (businesses|people|contacts)
  CLOUD STATS                         Show database statistics

Examples:
  CLOUD BUSINESS SEARCH coffee shops --location AA340
  CLOUD WEBSITE PARSE https://example.com biz-abc123
  CLOUD SOCIAL ENRICH twitter elonmusk
  CLOUD ENRICH EMAIL contact@example.com
  CLOUD ENRICH STAFF example.com
  CLOUD GENERATE KEYWORDS "live music venues" --location "Sydney" --upy
  CLOUD RESOLVE LOCATION "123 George St, Sydney NSW" --layer 300
  CLOUD EXPORT CSV businesses
  CLOUD STATS

API Keys Required (.env):
  GOOGLE_PLACES_API_KEY          Google Places API
  TWITTER_BEARER_TOKEN           Twitter/X API v2
  FACEBOOK_ACCESS_TOKEN          Instagram Graph API
  CLEARBIT_API_KEY               Clearbit Enrichment
  HUNTER_API_KEY                 Hunter.io Email Finder
  PEOPLE_DATA_LABS_API_KEY       PeopleDataLabs
  GOOGLE_GEOCODING_API_KEY       Google Geocoding (for RESOLVE LOCATION)
  GEMINI_API_KEY                 Google Gemini (for GENERATE KEYWORDS)
"""
