"""
Entity Resolver - Match and merge business/person entities

Implements priority matching per uDOS ID Standard:
1. google_place_id (strongest anchor)
2. linkedin_company_id
3. website_domain (normalized)
4. facebook_page_id
5. twitter_handle
6. Fuzzy match (name + normalized address)

If no confident match found → create new business_id (biz-...)
"""

from typing import Optional, Dict, List
from difflib import SequenceMatcher
from .marketing_db import MarketingDB
from .id_generator import generate_business_id, generate_person_id


class EntityResolver:
    """Resolve and merge business/person entities."""
    
    def __init__(self, db: MarketingDB):
        """Initialize entity resolver.
        
        Args:
            db: MarketingDB instance
        """
        self.db = db
        self.fuzzy_threshold = 0.85  # 85% similarity for fuzzy matching
    
    def match_business(self, **kwargs) -> Optional[str]:
        """Match business using priority cascade.
        
        Args:
            **kwargs: Candidate fields (google_place_id, linkedin_company_id,
                     website_domain, facebook_page_id, twitter_handle, name, raw_address)
        
        Returns:
            business_id if match found, None otherwise
        """
        # Priority 1: Google Place ID
        if kwargs.get('google_place_id'):
            result = self.db.find_business_by_google_place_id(kwargs['google_place_id'])
            if result:
                return result['business_id']
        
        # Priority 2: LinkedIn Company ID
        if kwargs.get('linkedin_company_id'):
            result = self._find_by_field('linkedin_company_id', kwargs['linkedin_company_id'])
            if result:
                return result['business_id']
        
        # Priority 3: Website domain (normalized)
        if kwargs.get('website_domain'):
            domain = self._normalize_domain(kwargs['website_domain'])
            result = self.db.find_business_by_domain(domain)
            if result:
                return result['business_id']
        
        # Priority 4: Facebook Page ID
        if kwargs.get('facebook_page_id'):
            result = self._find_by_field('facebook_page_id', kwargs['facebook_page_id'])
            if result:
                return result['business_id']
        
        # Priority 5: Twitter handle
        if kwargs.get('twitter_handle'):
            handle = self._normalize_handle(kwargs['twitter_handle'])
            result = self._find_by_field('twitter_handle', handle)
            if result:
                return result['business_id']
        
        # Priority 6: Fuzzy match on name + address
        if kwargs.get('name'):
            result = self._fuzzy_match_business(
                name=kwargs['name'],
                address=kwargs.get('raw_address', '')
            )
            if result:
                return result['business_id']
        
        return None
    
    def match_person(self, **kwargs) -> Optional[str]:
        """Match person using email or name.
        
        Args:
            **kwargs: Candidate fields (primary_email, full_name)
        
        Returns:
            person_id if match found, None otherwise
        """
        # Priority 1: Email address (strongest anchor)
        if kwargs.get('primary_email'):
            result = self.db.find_person_by_email(kwargs['primary_email'])
            if result:
                return result['person_id']
        
        # Priority 2: Fuzzy match on full name
        if kwargs.get('full_name'):
            result = self._fuzzy_match_person(kwargs['full_name'])
            if result:
                return result['person_id']
        
        return None
    
    def resolve_or_create_business(self, **kwargs) -> str:
        """Resolve existing business or create new one.
        
        Args:
            **kwargs: Business fields
        
        Returns:
            business_id (existing or newly created)
        """
        # Try to match existing
        business_id = self.match_business(**kwargs)
        
        if business_id:
            # Update external IDs if new anchors provided
            self.update_business_external_ids(business_id, **kwargs)
            return business_id
        
        # Create new business
        business_id = generate_business_id()
        
        # Normalize domain if website provided
        if kwargs.get('website') and not kwargs.get('website_domain'):
            kwargs['website_domain'] = self._normalize_domain(kwargs['website'])
        
        self.db.create_business(business_id, kwargs.get('name', 'Unknown'), **kwargs)
        return business_id
    
    def resolve_or_create_person(self, **kwargs) -> str:
        """Resolve existing person or create new one.
        
        Args:
            **kwargs: Person fields
        
        Returns:
            person_id (existing or newly created)
        """
        # Try to match existing
        person_id = self.match_person(**kwargs)
        
        if person_id:
            # Update fields if new data provided
            self.update_person_fields(person_id, **kwargs)
            return person_id
        
        # Create new person
        person_id = generate_person_id()
        self.db.create_person(person_id, kwargs.get('full_name', 'Unknown'), **kwargs)
        return person_id
    
    def update_business_external_ids(self, business_id: str, **kwargs):
        """Update business external ID anchors if new ones provided.
        
        Args:
            business_id: Business to update
            **kwargs: Fields that may contain new external IDs
        """
        update_fields = {}
        
        for field in ['google_place_id', 'linkedin_company_id', 'facebook_page_id',
                     'twitter_handle', 'instagram_handle', 'website', 'website_domain']:
            if kwargs.get(field):
                update_fields[field] = kwargs[field]
        
        if update_fields:
            self.db.update_business(business_id, **update_fields)
    
    def update_person_fields(self, person_id: str, **kwargs):
        """Update person fields if new data provided.
        
        Args:
            person_id: Person to update
            **kwargs: Fields to update
        """
        update_fields = {}
        
        for field in ['phone', 'linkedin_url', 'twitter_handle', 'instagram_url',
                     'facebook_url', 'job_title', 'company_name']:
            if kwargs.get(field):
                update_fields[field] = kwargs[field]
        
        if update_fields:
            self.db.update_person(person_id, **update_fields)
    
    def merge_businesses(self, keep_id: str, merge_id: str) -> bool:
        """Merge two business records (manual deduplication).
        
        Args:
            keep_id: Business ID to keep
            merge_id: Business ID to merge into keep_id
        
        Returns:
            bool: True if merged successfully
        """
        keep = self.db.get_business(keep_id)
        merge = self.db.get_business(merge_id)
        
        if not keep or not merge:
            return False
        
        # Merge external IDs (keep wins, but fill nulls from merge)
        update_fields = {}
        for field in ['google_place_id', 'linkedin_company_id', 'facebook_page_id',
                     'twitter_handle', 'instagram_handle', 'phone', 'email']:
            if not keep.get(field) and merge.get(field):
                update_fields[field] = merge[field]
        
        if update_fields:
            self.db.update_business(keep_id, **update_fields)
        
        # Update all relationships pointing to merge_id
        cursor = self.db.conn.cursor()
        cursor.execute(
            "UPDATE business_person_roles SET business_id = ? WHERE business_id = ?",
            (keep_id, merge_id)
        )
        cursor.execute(
            "UPDATE audience SET business_id = ? WHERE business_id = ?",
            (keep_id, merge_id)
        )
        cursor.execute(
            "UPDATE messages SET business_id = ? WHERE business_id = ?",
            (keep_id, merge_id)
        )
        
        # Delete merged business
        cursor.execute("DELETE FROM businesses WHERE business_id = ?", (merge_id,))
        self.db.conn.commit()
        
        return True
    
    def merge_people(self, keep_id: str, merge_id: str) -> bool:
        """Merge two person records (manual deduplication).
        
        Args:
            keep_id: Person ID to keep
            merge_id: Person ID to merge into keep_id
        
        Returns:
            bool: True if merged successfully
        """
        keep = self.db.get_person(keep_id)
        merge = self.db.get_person(merge_id)
        
        if not keep or not merge:
            return False
        
        # Merge fields (keep wins, but fill nulls from merge)
        update_fields = {}
        for field in ['phone', 'linkedin_url', 'twitter_handle', 'instagram_url',
                     'facebook_url', 'job_title', 'company_name']:
            if not keep.get(field) and merge.get(field):
                update_fields[field] = merge[field]
        
        if update_fields:
            self.db.update_person(keep_id, **update_fields)
        
        # Update all relationships pointing to merge_id
        cursor = self.db.conn.cursor()
        cursor.execute(
            "UPDATE business_person_roles SET person_id = ? WHERE person_id = ?",
            (keep_id, merge_id)
        )
        cursor.execute(
            "UPDATE messages SET person_id = ? WHERE person_id = ?",
            (keep_id, merge_id)
        )
        
        # Delete merged person
        cursor.execute("DELETE FROM people WHERE person_id = ?", (merge_id,))
        self.db.conn.commit()
        
        return True
    
    # Helper methods
    
    def _find_by_field(self, field: str, value: str) -> Optional[Dict]:
        """Find business by arbitrary field.
        
        Args:
            field: Field name
            value: Field value
        
        Returns:
            Business dict or None
        """
        cursor = self.db.conn.cursor()
        cursor.execute(f"SELECT * FROM businesses WHERE {field} = ?", (value,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def _normalize_domain(self, url_or_domain: str) -> str:
        """Normalize domain for matching.
        
        Args:
            url_or_domain: URL or domain string
        
        Returns:
            Normalized domain (lowercase, no www)
        """
        domain = url_or_domain.lower()
        
        # Remove protocol
        for prefix in ['https://', 'http://', '//']:
            if domain.startswith(prefix):
                domain = domain[len(prefix):]
        
        # Remove www.
        if domain.startswith('www.'):
            domain = domain[4:]
        
        # Remove path/query
        if '/' in domain:
            domain = domain.split('/')[0]
        if '?' in domain:
            domain = domain.split('?')[0]
        
        return domain
    
    def _normalize_handle(self, handle: str) -> str:
        """Normalize social media handle.
        
        Args:
            handle: Handle string (may include @)
        
        Returns:
            Normalized handle (lowercase, no @)
        """
        handle = handle.lower().strip()
        if handle.startswith('@'):
            handle = handle[1:]
        return handle
    
    def _fuzzy_match_business(self, name: str, address: str = '') -> Optional[Dict]:
        """Fuzzy match business by name and address.
        
        Args:
            name: Business name
            address: Raw address (optional)
        
        Returns:
            Business dict if confident match, None otherwise
        """
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT * FROM businesses")
        
        best_match = None
        best_score = 0.0
        
        for row in cursor.fetchall():
            business = dict(row)
            
            # Calculate name similarity
            name_score = SequenceMatcher(None, name.lower(), business['name'].lower()).ratio()
            
            # Calculate address similarity (if provided)
            addr_score = 0.0
            if address and business.get('raw_address'):
                addr_score = SequenceMatcher(
                    None,
                    address.lower(),
                    business['raw_address'].lower()
                ).ratio()
            
            # Combined score (name weighted 70%, address 30%)
            if address and business.get('raw_address'):
                combined_score = (name_score * 0.7) + (addr_score * 0.3)
            else:
                combined_score = name_score
            
            if combined_score > best_score:
                best_score = combined_score
                best_match = business
        
        # Return match only if above threshold
        if best_score >= self.fuzzy_threshold:
            return best_match
        
        return None
    
    def _fuzzy_match_person(self, full_name: str) -> Optional[Dict]:
        """Fuzzy match person by name.
        
        Args:
            full_name: Person's full name
        
        Returns:
            Person dict if confident match, None otherwise
        """
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT * FROM people")
        
        best_match = None
        best_score = 0.0
        
        for row in cursor.fetchall():
            person = dict(row)
            score = SequenceMatcher(None, full_name.lower(), person['full_name'].lower()).ratio()
            
            if score > best_score:
                best_score = score
                best_match = person
        
        # Return match only if above threshold (stricter for people - 90%)
        if best_score >= 0.90:
            return best_match
        
        return None
