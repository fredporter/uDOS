"""
Website Parser for Business Intelligence
Extracts staff directories, team pages, contact information from business websites.

Legal Compliance:
- Respects robots.txt
- Only extracts publicly visible data
- No bypass of technical restrictions
- Rate limiting per domain
- User-Agent identification

Extraction Targets:
- Staff directories
- Management bios
- Contact emails
- Artist/performer rosters
- Team pages ("Crew", "About Us", "Who We Are", "Contact")
- Press contacts
- Booking + management emails
- Job roles & departments
"""

import re
import time
import urllib.robotparser
from typing import Dict, List, Optional, Set
from urllib.parse import urljoin, urlparse
from dataclasses import dataclass
from datetime import datetime, timedelta

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    requests = None
    BeautifulSoup = None


@dataclass
class StaffMember:
    """Extracted staff member data."""
    name: str
    role: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    bio: Optional[str] = None
    department: Optional[str] = None


@dataclass
class BusinessContact:
    """Extracted business contact data."""
    contact_type: str  # booking, press, management, general
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


class WebsiteParser:
    """Parse business websites for staff and contact information."""
    
    # URLs that commonly contain staff/team information
    TEAM_PAGE_PATTERNS = [
        r'/team',
        r'/about',
        r'/about-us',
        r'/who-we-are',
        r'/our-team',
        r'/crew',
        r'/staff',
        r'/people',
        r'/management',
        r'/contact',
        r'/artists',
        r'/performers',
        r'/roster',
    ]
    
    # Email patterns for different contact types
    CONTACT_EMAIL_PATTERNS = {
        'booking': r'(booking|bookings|book)@',
        'press': r'(press|media|pr)@',
        'management': r'(management|manager|mgmt)@',
        'info': r'(info|contact|hello|hi)@',
    }
    
    # Job title keywords for role detection
    ROLE_KEYWORDS = {
        'Owner': ['owner', 'founder', 'co-founder', 'proprietor'],
        'Manager': ['manager', 'general manager', 'gm', 'managing director'],
        'Director': ['director', 'exec director', 'executive director'],
        'Artist': ['artist', 'performer', 'musician', 'dj', 'mc', 'rapper', 'singer'],
        'Promoter': ['promoter', 'event manager', 'events manager'],
        'Booking': ['booking agent', 'booking manager', 'talent buyer'],
        'Press': ['press officer', 'pr manager', 'media manager', 'publicist'],
        'Marketing': ['marketing manager', 'marketing director', 'social media'],
        'Operations': ['operations manager', 'ops manager', 'venue manager'],
    }
    
    def __init__(self, user_agent: str = "uDOS-BIZINTEL/1.0"):
        """Initialize website parser.
        
        Args:
            user_agent: User-Agent string for HTTP requests
        """
        if requests is None or BeautifulSoup is None:
            raise ImportError("requests and beautifulsoup4 required: pip install requests beautifulsoup4")
        
        self.user_agent = user_agent
        self.robots_cache: Dict[str, urllib.robotparser.RobotFileParser] = {}
        self.rate_limits: Dict[str, datetime] = {}  # domain -> last request time
        self.min_delay = 1.0  # minimum seconds between requests to same domain
        
    def can_fetch(self, url: str) -> bool:
        """Check if URL is allowed by robots.txt.
        
        Args:
            url: URL to check
            
        Returns:
            True if allowed, False otherwise
        """
        parsed = urlparse(url)
        domain = parsed.netloc
        
        # Check robots.txt cache
        if domain not in self.robots_cache:
            rp = urllib.robotparser.RobotFileParser()
            robots_url = f"{parsed.scheme}://{domain}/robots.txt"
            try:
                rp.set_url(robots_url)
                rp.read()
                self.robots_cache[domain] = rp
            except Exception:
                # If robots.txt can't be fetched, assume allowed
                return True
        
        return self.robots_cache[domain].can_fetch(self.user_agent, url)
    
    def _rate_limit(self, domain: str):
        """Enforce rate limiting per domain.
        
        Args:
            domain: Domain to rate limit
        """
        if domain in self.rate_limits:
            elapsed = (datetime.now() - self.rate_limits[domain]).total_seconds()
            if elapsed < self.min_delay:
                time.sleep(self.min_delay - elapsed)
        
        self.rate_limits[domain] = datetime.now()
    
    def _fetch_page(self, url: str) -> Optional[str]:
        """Fetch webpage content with compliance checks.
        
        Args:
            url: URL to fetch
            
        Returns:
            HTML content or None if blocked/error
        """
        # Check robots.txt
        if not self.can_fetch(url):
            return None
        
        # Rate limiting
        domain = urlparse(url).netloc
        self._rate_limit(domain)
        
        # Fetch
        try:
            headers = {'User-Agent': self.user_agent}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def find_team_pages(self, base_url: str) -> List[str]:
        """Find potential team/staff pages on website.
        
        Args:
            base_url: Base URL of website
            
        Returns:
            List of URLs that likely contain team information
        """
        html = self._fetch_page(base_url)
        if not html:
            return []
        
        soup = BeautifulSoup(html, 'html.parser')
        team_urls = set()
        
        # Find all links
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(base_url, href)
            
            # Check if URL matches team page patterns
            for pattern in self.TEAM_PAGE_PATTERNS:
                if re.search(pattern, full_url.lower()):
                    team_urls.add(full_url)
                    break
        
        return list(team_urls)
    
    def extract_staff(self, url: str) -> List[StaffMember]:
        """Extract staff members from a page.
        
        Args:
            url: URL to parse
            
        Returns:
            List of StaffMember objects
        """
        html = self._fetch_page(url)
        if not html:
            return []
        
        soup = BeautifulSoup(html, 'html.parser')
        staff = []
        
        # Look for common staff listing patterns
        # Pattern 1: <div class="team-member"> or similar
        for container in soup.find_all(['div', 'li'], class_=re.compile(r'(team|staff|person|member|artist|crew)')):
            member = self._extract_staff_from_container(container)
            if member:
                staff.append(member)
        
        # Pattern 2: <h3>Name</h3><p>Role</p> sequences
        headings = soup.find_all(['h2', 'h3', 'h4'])
        for heading in headings:
            member = self._extract_staff_from_heading(heading)
            if member:
                staff.append(member)
        
        return staff
    
    def _extract_staff_from_container(self, container) -> Optional[StaffMember]:
        """Extract staff member from a container element.
        
        Args:
            container: BeautifulSoup element
            
        Returns:
            StaffMember or None
        """
        # Extract name (usually in h2/h3/h4 or strong/b)
        name_elem = container.find(['h2', 'h3', 'h4', 'strong', 'b'])
        if not name_elem:
            return None
        
        name = name_elem.get_text(strip=True)
        if not name or len(name) < 2:
            return None
        
        # Extract role
        role = None
        role_elem = container.find(class_=re.compile(r'(role|title|position|job)'))
        if role_elem:
            role = role_elem.get_text(strip=True)
        else:
            # Look for text after name
            text = container.get_text()
            role_match = re.search(r'-\s*([^-\n]+)', text)
            if role_match:
                role = role_match.group(1).strip()
        
        # Extract email
        email = None
        email_elem = container.find('a', href=re.compile(r'mailto:'))
        if email_elem:
            email = email_elem['href'].replace('mailto:', '')
        
        # Extract LinkedIn
        linkedin_url = None
        linkedin_elem = container.find('a', href=re.compile(r'linkedin\.com'))
        if linkedin_elem:
            linkedin_url = linkedin_elem['href']
        
        # Extract bio
        bio = None
        bio_elem = container.find(['p', 'div'], class_=re.compile(r'(bio|description|about)'))
        if bio_elem:
            bio = bio_elem.get_text(strip=True)
        
        return StaffMember(
            name=name,
            role=self._normalize_role(role) if role else None,
            email=email,
            linkedin_url=linkedin_url,
            bio=bio
        )
    
    def _extract_staff_from_heading(self, heading) -> Optional[StaffMember]:
        """Extract staff member from heading + following content.
        
        Args:
            heading: BeautifulSoup heading element
            
        Returns:
            StaffMember or None
        """
        name = heading.get_text(strip=True)
        if not name or len(name) < 2:
            return None
        
        # Look for role in next sibling
        role = None
        next_elem = heading.find_next_sibling()
        if next_elem:
            role_text = next_elem.get_text(strip=True)
            if len(role_text) < 100:  # Likely a role, not a bio
                role = role_text
        
        return StaffMember(
            name=name,
            role=self._normalize_role(role) if role else None
        )
    
    def _normalize_role(self, role_text: str) -> str:
        """Normalize role text to standard categories.
        
        Args:
            role_text: Raw role text
            
        Returns:
            Normalized role category or original text
        """
        role_lower = role_text.lower()
        
        for category, keywords in self.ROLE_KEYWORDS.items():
            for keyword in keywords:
                if keyword in role_lower:
                    return category
        
        return role_text
    
    def extract_contacts(self, url: str) -> List[BusinessContact]:
        """Extract business contact information from a page.
        
        Args:
            url: URL to parse
            
        Returns:
            List of BusinessContact objects
        """
        html = self._fetch_page(url)
        if not html:
            return []
        
        soup = BeautifulSoup(html, 'html.parser')
        contacts = []
        
        # Find all email links
        for email_link in soup.find_all('a', href=re.compile(r'mailto:')):
            email = email_link['href'].replace('mailto:', '').strip()
            
            # Classify email type
            contact_type = 'general'
            for ctype, pattern in self.CONTACT_EMAIL_PATTERNS.items():
                if re.search(pattern, email, re.IGNORECASE):
                    contact_type = ctype
                    break
            
            # Try to find associated name (look in parent or nearby text)
            name = None
            parent = email_link.find_parent(['p', 'div', 'li'])
            if parent:
                text = parent.get_text()
                # Look for name before email
                name_match = re.search(r'([A-Z][a-z]+\s+[A-Z][a-z]+)\s*[:–-]?\s*' + re.escape(email), text)
                if name_match:
                    name = name_match.group(1)
            
            contacts.append(BusinessContact(
                contact_type=contact_type,
                email=email,
                name=name
            ))
        
        return contacts
    
    def parse_website(self, base_url: str) -> Dict:
        """Parse entire website for business intelligence.
        
        Args:
            base_url: Base URL of business website
            
        Returns:
            Dictionary with staff, contacts, and metadata
        """
        result = {
            'base_url': base_url,
            'parsed_at': datetime.now().isoformat(),
            'staff': [],
            'contacts': [],
            'team_pages_found': [],
        }
        
        # Find team pages
        team_urls = self.find_team_pages(base_url)
        result['team_pages_found'] = team_urls
        
        # Parse each team page
        all_staff = []
        all_contacts = []
        
        for url in team_urls[:5]:  # Limit to 5 pages to avoid abuse
            staff = self.extract_staff(url)
            contacts = self.extract_contacts(url)
            all_staff.extend(staff)
            all_contacts.extend(contacts)
        
        # Deduplicate staff by name
        seen_names = set()
        for member in all_staff:
            if member.name not in seen_names:
                seen_names.add(member.name)
                result['staff'].append({
                    'name': member.name,
                    'role': member.role,
                    'email': member.email,
                    'phone': member.phone,
                    'linkedin_url': member.linkedin_url,
                    'bio': member.bio,
                    'department': member.department,
                })
        
        # Deduplicate contacts by email
        seen_emails = set()
        for contact in all_contacts:
            if contact.email not in seen_emails:
                seen_emails.add(contact.email)
                result['contacts'].append({
                    'type': contact.contact_type,
                    'name': contact.name,
                    'email': contact.email,
                    'phone': contact.phone,
                })
        
        return result
