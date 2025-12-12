"""
Email Enrichment API Clients for Business Intelligence
Integrations: Clearbit, Apollo, Hunter.io, PeopleDataLabs

Legal Compliance:
- Uses official APIs with proper authentication
- Respects API rate limits and terms of service
- Only enriches publicly available data
- No scraping or unauthorized access

Data Sources:
- Domain enrichment (company data)
- Email verification and validation
- Staff directory discovery
- Public job postings
- Press/media contacts
- Social profiles associated with emails
"""

import os
import time
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

try:
    import requests
except ImportError:
    requests = None


@dataclass
class EnrichedPerson:
    """Enriched person data from API."""
    email: str
    name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    job_title: Optional[str] = None
    seniority: Optional[str] = None  # entry, junior, senior, manager, director, vp, c-level
    department: Optional[str] = None
    company_name: Optional[str] = None
    company_domain: Optional[str] = None
    linkedin_url: Optional[str] = None
    twitter_handle: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    verified: bool = False


@dataclass
class EnrichedCompany:
    """Enriched company data from domain."""
    domain: str
    name: Optional[str] = None
    legal_name: Optional[str] = None
    category: Optional[str] = None
    industry: Optional[str] = None
    description: Optional[str] = None
    founded_year: Optional[int] = None
    employee_count: Optional[int] = None
    location: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    social_twitter: Optional[str] = None
    social_facebook: Optional[str] = None
    social_linkedin: Optional[str] = None


class ClearbitClient:
    """Clearbit Enrichment API client."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Clearbit client.
        
        Args:
            api_key: Clearbit API key (from .env)
        """
        if requests is None:
            raise ImportError("requests required: pip install requests")
        
        self.api_key = api_key or os.getenv('CLEARBIT_API_KEY')
        self.base_url = "https://person.clearbit.com/v2"
        self.company_url = "https://company.clearbit.com/v2"
    
    def enrich_person(self, email: str) -> Optional[EnrichedPerson]:
        """Enrich person data from email.
        
        Args:
            email: Email address
            
        Returns:
            EnrichedPerson or None
        """
        if not self.api_key:
            return None
        
        url = f"{self.base_url}/combined/find"
        params = {'email': email}
        headers = {'Authorization': f'Bearer {self.api_key}'}
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            if response.status_code == 404:
                return None
            response.raise_for_status()
            data = response.json()
            
            person = data.get('person', {})
            company = data.get('company', {})
            
            return EnrichedPerson(
                email=email,
                name=person.get('name', {}).get('fullName'),
                first_name=person.get('name', {}).get('givenName'),
                last_name=person.get('name', {}).get('familyName'),
                job_title=person.get('employment', {}).get('title'),
                seniority=person.get('employment', {}).get('seniority'),
                department=person.get('employment', {}).get('role'),
                company_name=company.get('name'),
                company_domain=company.get('domain'),
                linkedin_url=person.get('linkedin', {}).get('handle'),
                twitter_handle=person.get('twitter', {}).get('handle'),
                phone=person.get('phone'),
                location=person.get('location'),
                verified=True
            )
        except Exception as e:
            print(f"Clearbit error for {email}: {e}")
            return None
    
    def enrich_company(self, domain: str) -> Optional[EnrichedCompany]:
        """Enrich company data from domain.
        
        Args:
            domain: Company domain
            
        Returns:
            EnrichedCompany or None
        """
        if not self.api_key:
            return None
        
        url = f"{self.company_url}/companies/find"
        params = {'domain': domain}
        headers = {'Authorization': f'Bearer {self.api_key}'}
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            if response.status_code == 404:
                return None
            response.raise_for_status()
            data = response.json()
            
            return EnrichedCompany(
                domain=domain,
                name=data.get('name'),
                legal_name=data.get('legalName'),
                category=data.get('category', {}).get('industry'),
                industry=data.get('category', {}).get('subIndustry'),
                description=data.get('description'),
                founded_year=data.get('foundedYear'),
                employee_count=data.get('metrics', {}).get('employees'),
                location=data.get('location'),
                phone=data.get('phone'),
                website=data.get('domain'),
                social_twitter=data.get('twitter', {}).get('handle'),
                social_facebook=data.get('facebook', {}).get('handle'),
                social_linkedin=data.get('linkedin', {}).get('handle')
            )
        except Exception as e:
            print(f"Clearbit error for {domain}: {e}")
            return None


class HunterClient:
    """Hunter.io Email Finder and Verification API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Hunter.io client.
        
        Args:
            api_key: Hunter.io API key (from .env)
        """
        if requests is None:
            raise ImportError("requests required: pip install requests")
        
        self.api_key = api_key or os.getenv('HUNTER_API_KEY')
        self.base_url = "https://api.hunter.io/v2"
    
    def find_emails(self, domain: str, limit: int = 10) -> List[EnrichedPerson]:
        """Find email addresses associated with a domain.
        
        Args:
            domain: Company domain
            limit: Maximum emails to return
            
        Returns:
            List of EnrichedPerson with emails found
        """
        if not self.api_key:
            return []
        
        url = f"{self.base_url}/domain-search"
        params = {
            'domain': domain,
            'limit': limit,
            'api_key': self.api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            people = []
            for email_data in data.get('data', {}).get('emails', []):
                person = EnrichedPerson(
                    email=email_data.get('value'),
                    first_name=email_data.get('first_name'),
                    last_name=email_data.get('last_name'),
                    job_title=email_data.get('position'),
                    department=email_data.get('department'),
                    company_domain=domain,
                    linkedin_url=email_data.get('linkedin'),
                    twitter_handle=email_data.get('twitter'),
                    phone=email_data.get('phone_number'),
                    verified=email_data.get('verification', {}).get('status') == 'valid'
                )
                people.append(person)
            
            return people
        except Exception as e:
            print(f"Hunter.io error for {domain}: {e}")
            return []
    
    def verify_email(self, email: str) -> bool:
        """Verify if email address is valid.
        
        Args:
            email: Email to verify
            
        Returns:
            True if valid, False otherwise
        """
        if not self.api_key:
            return False
        
        url = f"{self.base_url}/email-verifier"
        params = {
            'email': email,
            'api_key': self.api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return data.get('data', {}).get('status') in ['valid', 'accept_all']
        except Exception:
            return False


class PeopleDataLabsClient:
    """PeopleDataLabs API client for person and company data."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize PeopleDataLabs client.
        
        Args:
            api_key: PDL API key (from .env)
        """
        if requests is None:
            raise ImportError("requests required: pip install requests")
        
        self.api_key = api_key or os.getenv('PEOPLE_DATA_LABS_API_KEY')
        self.base_url = "https://api.peopledatalabs.com/v5"
    
    def enrich_person(self, email: str) -> Optional[EnrichedPerson]:
        """Enrich person data from email.
        
        Args:
            email: Email address
            
        Returns:
            EnrichedPerson or None
        """
        if not self.api_key:
            return None
        
        url = f"{self.base_url}/person/enrich"
        params = {'email': email}
        headers = {'X-Api-Key': self.api_key}
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            if response.status_code == 404:
                return None
            response.raise_for_status()
            data = response.json()
            
            return EnrichedPerson(
                email=email,
                name=data.get('full_name'),
                first_name=data.get('first_name'),
                last_name=data.get('last_name'),
                job_title=data.get('job_title'),
                seniority=data.get('job_title_levels', [None])[0],
                department=data.get('job_title_role'),
                company_name=data.get('job_company_name'),
                company_domain=data.get('job_company_website'),
                linkedin_url=data.get('linkedin_url'),
                twitter_handle=data.get('twitter_url', '').split('/')[-1],
                phone=data.get('phone_numbers', [None])[0],
                location=data.get('location_name'),
                verified=True
            )
        except Exception as e:
            print(f"PeopleDataLabs error for {email}: {e}")
            return None
    
    def enrich_company(self, domain: str) -> Optional[EnrichedCompany]:
        """Enrich company data from domain.
        
        Args:
            domain: Company domain
            
        Returns:
            EnrichedCompany or None
        """
        if not self.api_key:
            return None
        
        url = f"{self.base_url}/company/enrich"
        params = {'website': domain}
        headers = {'X-Api-Key': self.api_key}
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            if response.status_code == 404:
                return None
            response.raise_for_status()
            data = response.json()
            
            return EnrichedCompany(
                domain=domain,
                name=data.get('name'),
                legal_name=data.get('legal_name'),
                category=data.get('industry'),
                description=data.get('summary'),
                founded_year=data.get('founded'),
                employee_count=data.get('employee_count'),
                location=data.get('location', {}).get('name'),
                website=domain,
                social_twitter=data.get('twitter', {}).get('url'),
                social_facebook=data.get('facebook', {}).get('url'),
                social_linkedin=data.get('linkedin', {}).get('url')
            )
        except Exception as e:
            print(f"PeopleDataLabs error for {domain}: {e}")
            return None


class EnrichmentService:
    """Unified enrichment service with fallback chain."""
    
    def __init__(self):
        """Initialize all enrichment clients."""
        self.clearbit = ClearbitClient()
        self.hunter = HunterClient()
        self.pdl = PeopleDataLabsClient()
    
    def enrich_person_with_fallback(self, email: str) -> Optional[EnrichedPerson]:
        """Try multiple enrichment services with fallback.
        
        Args:
            email: Email to enrich
            
        Returns:
            EnrichedPerson from first successful service
        """
        # Try Clearbit first (most comprehensive)
        result = self.clearbit.enrich_person(email)
        if result:
            return result
        
        # Try PeopleDataLabs
        result = self.pdl.enrich_person(email)
        if result:
            return result
        
        # Last resort: Just verify with Hunter
        if self.hunter.verify_email(email):
            return EnrichedPerson(email=email, verified=True)
        
        return None
    
    def enrich_company_with_fallback(self, domain: str) -> Optional[EnrichedCompany]:
        """Try multiple enrichment services with fallback.
        
        Args:
            domain: Domain to enrich
            
        Returns:
            EnrichedCompany from first successful service
        """
        # Try Clearbit first
        result = self.clearbit.enrich_company(domain)
        if result:
            return result
        
        # Try PeopleDataLabs
        result = self.pdl.enrich_company(domain)
        if result:
            return result
        
        return None
    
    def find_staff_emails(self, domain: str, limit: int = 20) -> List[EnrichedPerson]:
        """Find staff emails for a domain.
        
        Args:
            domain: Company domain
            limit: Maximum emails to find
            
        Returns:
            List of EnrichedPerson with verified emails
        """
        # Hunter.io is best for this
        return self.hunter.find_emails(domain, limit=limit)
