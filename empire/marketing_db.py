"""
Marketing Database - SQLite wrapper for business intelligence data

Manages 5 core tables in memory/bank/user/contacts.db:
- businesses: Business entities with biz-* IDs
- people: Person entities with prs-* IDs
- business_person_roles: Relationships with rel-* IDs
- audience: Social media metrics with aud-* IDs
- messages: Email messages with msg-* IDs

All external IDs (Google, LinkedIn, Facebook, Twitter) stored as attributes,
never as primary keys. Entity resolution via EntityResolver.
"""

import sqlite3
import os
from datetime import datetime
from typing import Optional, Dict, List, Any
from pathlib import Path


class MarketingDB:
    """SQLite database manager for business intelligence data."""
    
    def __init__(self, db_path: str = None):
        """Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file.
                    Defaults to memory/bank/user/contacts.db
        """
        if db_path is None:
            # Get project root (4 levels up from this file)
            project_root = Path(__file__).parent.parent.parent.parent
            db_path = project_root / "memory" / "bank" / "user" / "contacts.db"
        
        self.db_path = str(db_path)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        self.conn = None
        self._connect()
        self._create_tables()
    
    def _connect(self):
        """Establish database connection."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # Return rows as dicts
    
    def _create_tables(self):
        """Create database schema if tables don't exist."""
        cursor = self.conn.cursor()
        
        # Table 1: Businesses
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS businesses (
                business_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                raw_address TEXT,
                lat REAL,
                lon REAL,
                website TEXT,
                website_domain TEXT,
                
                google_place_id TEXT UNIQUE,
                facebook_page_id TEXT,
                linkedin_company_id TEXT,
                twitter_handle TEXT,
                instagram_handle TEXT,
                
                phone TEXT,
                email TEXT,
                description TEXT,
                category TEXT,
                
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                source TEXT,
                notes TEXT
            )
        ''')
        
        # Indexes for business lookup
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_business_google_place ON businesses(google_place_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_business_domain ON businesses(website_domain)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_business_name ON businesses(name)')
        
        # Table 2: People
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS people (
                person_id TEXT PRIMARY KEY,
                full_name TEXT NOT NULL,
                primary_email TEXT UNIQUE,
                phone TEXT,
                
                linkedin_url TEXT,
                twitter_handle TEXT,
                instagram_url TEXT,
                facebook_url TEXT,
                
                job_title TEXT,
                company_name TEXT,
                
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                source TEXT,
                notes TEXT
            )
        ''')
        
        # Indexes for people lookup
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_people_email ON people(primary_email)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_people_name ON people(full_name)')
        
        # Table 3: Business-Person Roles
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS business_person_roles (
                business_person_role_id TEXT PRIMARY KEY,
                business_id TEXT NOT NULL,
                person_id TEXT NOT NULL,
                
                role_type TEXT,
                role_title TEXT,
                tags TEXT,
                is_primary_contact INTEGER DEFAULT 0,
                
                created_at TEXT NOT NULL,
                source TEXT,
                
                FOREIGN KEY (business_id) REFERENCES businesses(business_id),
                FOREIGN KEY (person_id) REFERENCES people(person_id),
                UNIQUE(business_id, person_id)
            )
        ''')
        
        # Indexes for relationship lookup
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_roles_business ON business_person_roles(business_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_roles_person ON business_person_roles(person_id)')
        
        # Table 4: Audience Metrics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audience (
                audience_id TEXT PRIMARY KEY,
                business_id TEXT NOT NULL,
                platform TEXT NOT NULL,
                
                followers_count INTEGER,
                engagement_score REAL,
                last_synced_at TEXT,
                
                created_at TEXT NOT NULL,
                notes TEXT,
                
                FOREIGN KEY (business_id) REFERENCES businesses(business_id),
                UNIQUE(business_id, platform)
            )
        ''')
        
        # Indexes for audience lookup
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_audience_business ON audience(business_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_audience_platform ON audience(platform)')
        
        # Table 5: Messages (Email tracking)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                message_id TEXT PRIMARY KEY,
                gmail_message_id TEXT UNIQUE NOT NULL,
                thread_id TEXT NOT NULL,
                
                sender_email TEXT NOT NULL,
                sender_name TEXT,
                subject TEXT,
                snippet TEXT,
                compressed_content TEXT,
                
                business_id TEXT,
                person_id TEXT,
                
                sent_at TEXT NOT NULL,
                created_at TEXT NOT NULL,
                is_archived INTEGER DEFAULT 0,
                
                FOREIGN KEY (business_id) REFERENCES businesses(business_id),
                FOREIGN KEY (person_id) REFERENCES people(person_id)
            )
        ''')
        
        # Indexes for message lookup
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_gmail ON messages(gmail_message_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_thread ON messages(thread_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_sender ON messages(sender_email)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_business ON messages(business_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_person ON messages(person_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_archived ON messages(is_archived)')
        
        # Table 6: Social Profiles (extracted from websites/APIs)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS social_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                business_id TEXT,
                person_id TEXT,
                platform TEXT NOT NULL,
                
                username TEXT,
                profile_url TEXT,
                display_name TEXT,
                bio TEXT,
                followers_count INTEGER,
                following_count INTEGER,
                verified INTEGER DEFAULT 0,
                
                platform_user_id TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                
                FOREIGN KEY (business_id) REFERENCES businesses(business_id),
                FOREIGN KEY (person_id) REFERENCES people(person_id)
            )
        ''')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_social_business ON social_profiles(business_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_social_person ON social_profiles(person_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_social_platform ON social_profiles(platform)')
        
        # Table 7: Roles (structured job roles extracted from websites)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS roles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                person_id TEXT NOT NULL,
                business_id TEXT,
                
                role_category TEXT,
                role_title TEXT,
                department TEXT,
                seniority TEXT,
                
                source TEXT,
                created_at TEXT NOT NULL,
                
                FOREIGN KEY (person_id) REFERENCES people(person_id),
                FOREIGN KEY (business_id) REFERENCES businesses(business_id)
            )
        ''')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_roles_person_detailed ON roles(person_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_roles_business_detailed ON roles(business_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_roles_category ON roles(role_category)')
        
        # Table 8: Enrichment Cache (API response caching)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS enrichment_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lookup_key TEXT UNIQUE NOT NULL,
                lookup_type TEXT NOT NULL,
                
                provider TEXT NOT NULL,
                response_data TEXT,
                
                cached_at TEXT NOT NULL,
                expires_at TEXT,
                hit_count INTEGER DEFAULT 0
            )
        ''')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_enrichment_key ON enrichment_cache(lookup_key)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_enrichment_type ON enrichment_cache(lookup_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_enrichment_expires ON enrichment_cache(expires_at)')
        
        self.conn.commit()
    
    # Business CRUD operations
    
    def create_business(self, business_id: str, name: str, **kwargs) -> str:
        """Create a new business record.
        
        Args:
            business_id: Unique biz-* ID
            name: Business name
            **kwargs: Additional fields (raw_address, lat, lon, website, etc.)
        
        Returns:
            str: business_id
        """
        now = datetime.utcnow().isoformat()
        cursor = self.conn.cursor()
        
        fields = ['business_id', 'name', 'created_at', 'updated_at']
        values = [business_id, name, now, now]
        
        for key, value in kwargs.items():
            if key in ['raw_address', 'lat', 'lon', 'website', 'website_domain',
                      'google_place_id', 'facebook_page_id', 'linkedin_company_id',
                      'twitter_handle', 'instagram_handle', 'phone', 'email',
                      'description', 'category', 'source', 'notes']:
                fields.append(key)
                values.append(value)
        
        placeholders = ','.join(['?' for _ in values])
        query = f"INSERT INTO businesses ({','.join(fields)}) VALUES ({placeholders})"
        
        cursor.execute(query, values)
        self.conn.commit()
        return business_id
    
    def get_business(self, business_id: str) -> Optional[Dict]:
        """Get business by ID.
        
        Args:
            business_id: Business ID to retrieve
        
        Returns:
            Dict with business data or None
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM businesses WHERE business_id = ?", (business_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def find_business_by_google_place_id(self, google_place_id: str) -> Optional[Dict]:
        """Find business by Google Place ID.
        
        Args:
            google_place_id: Google Place ID
        
        Returns:
            Dict with business data or None
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM businesses WHERE google_place_id = ?", (google_place_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def find_business_by_domain(self, domain: str) -> Optional[Dict]:
        """Find business by website domain.
        
        Args:
            domain: Website domain (normalized)
        
        Returns:
            Dict with business data or None
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM businesses WHERE website_domain = ?", (domain,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def update_business(self, business_id: str, **kwargs) -> bool:
        """Update business record.
        
        Args:
            business_id: Business ID to update
            **kwargs: Fields to update
        
        Returns:
            bool: True if updated, False if not found
        """
        if not self.get_business(business_id):
            return False
        
        kwargs['updated_at'] = datetime.utcnow().isoformat()
        
        fields = [f"{key} = ?" for key in kwargs.keys()]
        values = list(kwargs.values()) + [business_id]
        
        query = f"UPDATE businesses SET {', '.join(fields)} WHERE business_id = ?"
        cursor = self.conn.cursor()
        cursor.execute(query, values)
        self.conn.commit()
        return True
    
    def list_businesses(self, limit: int = 100) -> List[Dict]:
        """List all businesses.
        
        Args:
            limit: Maximum number to return
        
        Returns:
            List of business dicts
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM businesses ORDER BY created_at DESC LIMIT ?", (limit,))
        return [dict(row) for row in cursor.fetchall()]
    
    # Person CRUD operations
    
    def create_person(self, person_id: str, full_name: str, **kwargs) -> str:
        """Create a new person record.
        
        Args:
            person_id: Unique prs-* ID
            full_name: Person's full name
            **kwargs: Additional fields (primary_email, phone, linkedin_url, etc.)
        
        Returns:
            str: person_id
        """
        now = datetime.utcnow().isoformat()
        cursor = self.conn.cursor()
        
        fields = ['person_id', 'full_name', 'created_at', 'updated_at']
        values = [person_id, full_name, now, now]
        
        for key, value in kwargs.items():
            if key in ['primary_email', 'phone', 'linkedin_url', 'twitter_handle',
                      'instagram_url', 'facebook_url', 'job_title', 'company_name',
                      'source', 'notes']:
                fields.append(key)
                values.append(value)
        
        placeholders = ','.join(['?' for _ in values])
        query = f"INSERT INTO people ({','.join(fields)}) VALUES ({placeholders})"
        
        cursor.execute(query, values)
        self.conn.commit()
        return person_id
    
    def get_person(self, person_id: str) -> Optional[Dict]:
        """Get person by ID.
        
        Args:
            person_id: Person ID to retrieve
        
        Returns:
            Dict with person data or None
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM people WHERE person_id = ?", (person_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def find_person_by_email(self, email: str) -> Optional[Dict]:
        """Find person by email address.
        
        Args:
            email: Email address
        
        Returns:
            Dict with person data or None
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM people WHERE primary_email = ?", (email,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def update_person(self, person_id: str, **kwargs) -> bool:
        """Update person record.
        
        Args:
            person_id: Person ID to update
            **kwargs: Fields to update
        
        Returns:
            bool: True if updated, False if not found
        """
        if not self.get_person(person_id):
            return False
        
        kwargs['updated_at'] = datetime.utcnow().isoformat()
        
        fields = [f"{key} = ?" for key in kwargs.keys()]
        values = list(kwargs.values()) + [person_id]
        
        query = f"UPDATE people SET {', '.join(fields)} WHERE person_id = ?"
        cursor = self.conn.cursor()
        cursor.execute(query, values)
        self.conn.commit()
        return True
    
    def list_people(self, limit: int = 100) -> List[Dict]:
        """List all people.
        
        Args:
            limit: Maximum number to return
        
        Returns:
            List of person dicts
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM people ORDER BY created_at DESC LIMIT ?", (limit,))
        return [dict(row) for row in cursor.fetchall()]
    
    # Relationship CRUD operations
    
    def create_relationship(self, rel_id: str, business_id: str, person_id: str, **kwargs) -> str:
        """Create business-person relationship.
        
        Args:
            rel_id: Unique rel-* ID
            business_id: Business ID
            person_id: Person ID
            **kwargs: Additional fields (role_type, role_title, tags, etc.)
        
        Returns:
            str: rel_id
        """
        now = datetime.utcnow().isoformat()
        cursor = self.conn.cursor()
        
        fields = ['business_person_role_id', 'business_id', 'person_id', 'created_at']
        values = [rel_id, business_id, person_id, now]
        
        for key, value in kwargs.items():
            if key in ['role_type', 'role_title', 'tags', 'is_primary_contact', 'source']:
                fields.append(key)
                values.append(value)
        
        placeholders = ','.join(['?' for _ in values])
        query = f"INSERT INTO business_person_roles ({','.join(fields)}) VALUES ({placeholders})"
        
        cursor.execute(query, values)
        self.conn.commit()
        return rel_id
    
    def get_relationships_for_business(self, business_id: str) -> List[Dict]:
        """Get all people relationships for a business.
        
        Args:
            business_id: Business ID
        
        Returns:
            List of relationship dicts with person data
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT r.*, p.full_name, p.primary_email, p.phone, p.job_title
            FROM business_person_roles r
            JOIN people p ON r.person_id = p.person_id
            WHERE r.business_id = ?
        ''', (business_id,))
        return [dict(row) for row in cursor.fetchall()]
    
    def get_relationships_for_person(self, person_id: str) -> List[Dict]:
        """Get all business relationships for a person.
        
        Args:
            person_id: Person ID
        
        Returns:
            List of relationship dicts with business data
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT r.*, b.name, b.website, b.phone, b.email
            FROM business_person_roles r
            JOIN businesses b ON r.business_id = b.business_id
            WHERE r.person_id = ?
        ''', (person_id,))
        return [dict(row) for row in cursor.fetchall()]
    
    # Message CRUD operations
    
    def create_message(self, message_id: str, gmail_message_id: str, thread_id: str,
                       sender_email: str, sent_at: str, **kwargs) -> str:
        """Create message record.
        
        Args:
            message_id: Unique msg-* ID
            gmail_message_id: Gmail's native message ID
            thread_id: Gmail thread ID
            sender_email: Sender email address
            sent_at: ISO timestamp
            **kwargs: Additional fields (subject, snippet, compressed_content, etc.)
        
        Returns:
            str: message_id
        """
        now = datetime.utcnow().isoformat()
        cursor = self.conn.cursor()
        
        fields = ['message_id', 'gmail_message_id', 'thread_id', 'sender_email', 'sent_at', 'created_at']
        values = [message_id, gmail_message_id, thread_id, sender_email, sent_at, now]
        
        for key, value in kwargs.items():
            if key in ['sender_name', 'subject', 'snippet', 'compressed_content',
                      'business_id', 'person_id', 'is_archived']:
                fields.append(key)
                values.append(value)
        
        placeholders = ','.join(['?' for _ in values])
        query = f"INSERT INTO messages ({','.join(fields)}) VALUES ({placeholders})"
        
        cursor.execute(query, values)
        self.conn.commit()
        return message_id
    
    def get_message(self, message_id: str) -> Optional[Dict]:
        """Get message by ID.
        
        Args:
            message_id: Message ID to retrieve
        
        Returns:
            Dict with message data or None
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM messages WHERE message_id = ?", (message_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_messages_by_thread(self, thread_id: str, include_archived: bool = False) -> List[Dict]:
        """Get all messages in a thread.
        
        Args:
            thread_id: Gmail thread ID
            include_archived: Whether to include archived messages
        
        Returns:
            List of message dicts ordered by sent_at
        """
        cursor = self.conn.cursor()
        if include_archived:
            cursor.execute("SELECT * FROM messages WHERE thread_id = ? ORDER BY sent_at ASC", (thread_id,))
        else:
            cursor.execute("SELECT * FROM messages WHERE thread_id = ? AND is_archived = 0 ORDER BY sent_at ASC", (thread_id,))
        return [dict(row) for row in cursor.fetchall()]
    
    def archive_message(self, message_id: str) -> bool:
        """Mark message as archived.
        
        Args:
            message_id: Message ID to archive
        
        Returns:
            bool: True if archived, False if not found
        """
        cursor = self.conn.cursor()
        cursor.execute("UPDATE messages SET is_archived = 1 WHERE message_id = ?", (message_id,))
        self.conn.commit()
        return cursor.rowcount > 0
    
    def link_message_to_person(self, message_id: str, person_id: str) -> bool:
        """Link message to person.
        
        Args:
            message_id: Message ID
            person_id: Person ID
        
        Returns:
            bool: True if linked, False if not found
        """
        cursor = self.conn.cursor()
        cursor.execute("UPDATE messages SET person_id = ? WHERE message_id = ?", (person_id, message_id))
        self.conn.commit()
        return cursor.rowcount > 0
    
    def link_message_to_business(self, message_id: str, business_id: str) -> bool:
        """Link message to business.
        
        Args:
            message_id: Message ID
            business_id: Business ID
        
        Returns:
            bool: True if linked, False if not found
        """
        cursor = self.conn.cursor()
        cursor.execute("UPDATE messages SET business_id = ? WHERE message_id = ?", (business_id, message_id))
        self.conn.commit()
        return cursor.rowcount > 0
    
    # Social Profiles operations
    
    def create_social_profile(self, business_id: Optional[str], person_id: Optional[str],
                             platform: str, username: str, **kwargs) -> int:
        """Create social profile record.
        
        Args:
            business_id: Optional business ID
            person_id: Optional person ID
            platform: Platform name (twitter, instagram, facebook, linkedin)
            username: Username on platform
            **kwargs: Additional profile data
            
        Returns:
            Row ID of created profile
        """
        cursor = self.conn.cursor()
        now = datetime.now().isoformat()
        
        cursor.execute('''
            INSERT INTO social_profiles (
                business_id, person_id, platform, username,
                profile_url, display_name, bio,
                followers_count, following_count, verified,
                platform_user_id, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            business_id, person_id, platform, username,
            kwargs.get('profile_url'), kwargs.get('display_name'),
            kwargs.get('bio'), kwargs.get('followers_count'),
            kwargs.get('following_count'), 1 if kwargs.get('verified') else 0,
            kwargs.get('platform_user_id'), now, now
        ))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def get_social_profiles(self, business_id: Optional[str] = None,
                           person_id: Optional[str] = None) -> List[Dict]:
        """Get social profiles for business or person.
        
        Args:
            business_id: Filter by business ID
            person_id: Filter by person ID
            
        Returns:
            List of social profile dictionaries
        """
        cursor = self.conn.cursor()
        
        if business_id:
            cursor.execute('SELECT * FROM social_profiles WHERE business_id = ?', (business_id,))
        elif person_id:
            cursor.execute('SELECT * FROM social_profiles WHERE person_id = ?', (person_id,))
        else:
            cursor.execute('SELECT * FROM social_profiles')
        
        return [dict(row) for row in cursor.fetchall()]
    
    # Roles operations
    
    def create_role(self, person_id: str, business_id: Optional[str],
                   role_category: str, role_title: str, **kwargs) -> int:
        """Create role record.
        
        Args:
            person_id: Person ID
            business_id: Optional business ID
            role_category: Role category (Owner, Manager, etc.)
            role_title: Job title
            **kwargs: Additional role data
            
        Returns:
            Row ID of created role
        """
        cursor = self.conn.cursor()
        now = datetime.now().isoformat()
        
        cursor.execute('''
            INSERT INTO roles (
                person_id, business_id, role_category, role_title,
                department, seniority, source, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            person_id, business_id, role_category, role_title,
            kwargs.get('department'), kwargs.get('seniority'),
            kwargs.get('source', 'manual'), now
        ))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def get_roles_for_person(self, person_id: str) -> List[Dict]:
        """Get all roles for a person.
        
        Args:
            person_id: Person ID
            
        Returns:
            List of role dictionaries
        """
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM roles WHERE person_id = ?', (person_id,))
        return [dict(row) for row in cursor.fetchall()]
    
    def get_roles_for_business(self, business_id: str) -> List[Dict]:
        """Get all roles (staff) for a business.
        
        Args:
            business_id: Business ID
            
        Returns:
            List of role dictionaries with person data
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT r.*, p.full_name, p.primary_email
            FROM roles r
            JOIN people p ON r.person_id = p.person_id
            WHERE r.business_id = ?
            ORDER BY r.seniority DESC, r.role_category
        ''', (business_id,))
        return [dict(row) for row in cursor.fetchall()]
    
    # Enrichment Cache operations
    
    def cache_enrichment(self, lookup_key: str, lookup_type: str,
                        provider: str, response_data: str,
                        ttl_hours: int = 168) -> int:  # 1 week default
        """Cache enrichment API response.
        
        Args:
            lookup_key: Lookup key (email, domain, etc.)
            lookup_type: Type of lookup (person, company)
            provider: API provider (clearbit, hunter, pdl)
            response_data: JSON response data
            ttl_hours: Time to live in hours
            
        Returns:
            Row ID of cache entry
        """
        from datetime import timedelta
        
        cursor = self.conn.cursor()
        now = datetime.now()
        cached_at = now.isoformat()
        expires_at = (now + timedelta(hours=ttl_hours)).isoformat()
        
        cursor.execute('''
            INSERT OR REPLACE INTO enrichment_cache (
                lookup_key, lookup_type, provider, response_data,
                cached_at, expires_at, hit_count
            ) VALUES (?, ?, ?, ?, ?, ?, 0)
        ''', (lookup_key, lookup_type, provider, response_data, cached_at, expires_at))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def get_cached_enrichment(self, lookup_key: str) -> Optional[Dict]:
        """Get cached enrichment data if not expired.
        
        Args:
            lookup_key: Lookup key
            
        Returns:
            Cached data or None if expired/missing
        """
        cursor = self.conn.cursor()
        now = datetime.now().isoformat()
        
        cursor.execute('''
            SELECT * FROM enrichment_cache
            WHERE lookup_key = ? AND (expires_at IS NULL OR expires_at > ?)
        ''', (lookup_key, now))
        
        row = cursor.fetchone()
        if row:
            # Increment hit count
            cursor.execute('UPDATE enrichment_cache SET hit_count = hit_count + 1 WHERE id = ?', (row['id'],))
            self.conn.commit()
            return dict(row)
        
        return None
    
    def clear_expired_cache(self) -> int:
        """Clear expired enrichment cache entries.
        
        Returns:
            Number of deleted entries
        """
        cursor = self.conn.cursor()
        now = datetime.now().isoformat()
        
        cursor.execute('DELETE FROM enrichment_cache WHERE expires_at < ?', (now,))
        deleted = cursor.rowcount
        self.conn.commit()
        
        return deleted
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
