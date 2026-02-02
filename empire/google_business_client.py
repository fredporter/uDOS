"""
Google Business Profile API Client

OAuth2 authentication and API access for Google Business Profile.
Uses same OAuth pattern as Gmail integration.

Capabilities:
- Search for businesses near location (TILE code)
- Get business details (name, address, phone, website, ratings)
- Fetch reviews and photos (if available)
- Map to internal biz-* IDs with google_place_id as anchor

API Docs: https://developers.google.com/my-business/reference/rest
"""

import os
import json
from typing import Optional, Dict, List
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class GoogleBusinessClient:
    """Google Business Profile API client with OAuth2."""

    # OAuth2 scopes
    SCOPES = [
        'https://www.googleapis.com/auth/business.manage',  # Business profile management
    ]

    # Alternative: Use Places API (no OAuth required for basic search)
    PLACES_API_KEY_ENV = 'GOOGLE_PLACES_API_KEY'

    def __init__(self, credentials_path: str = None, token_path: str = None):
        """Initialize Google Business client.

        Args:
            credentials_path: Path to OAuth2 credentials JSON
                             Default: memory/bank/user/google_business_credentials.json
            token_path: Path to save/load tokens
                       Default: .env (GOOGLE_BUSINESS_TOKEN)
        """
        if credentials_path is None:
            # Default to memory/bank/user/
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            credentials_path = os.path.join(project_root, 'memory', 'bank', 'user', 'google_business_credentials.json')

        self.credentials_path = credentials_path
        self.token_path = token_path
        self.creds = None
        self.service = None

        # Check if we have Places API key (simpler, no OAuth needed)
        self.places_api_key = os.getenv(self.PLACES_API_KEY_ENV)

    def authenticate(self) -> bool:
        """Authenticate with Google OAuth2.

        Returns:
            bool: True if authenticated successfully
        """
        # Check for existing token
        if self.token_path and os.path.exists(self.token_path):
            try:
                with open(self.token_path, 'r') as token_file:
                    token_data = json.load(token_file)
                    self.creds = Credentials.from_authorized_user_info(token_data, self.SCOPES)
            except Exception as e:
                print(f"Error loading token: {e}")

        # Refresh or get new token
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                try:
                    self.creds.refresh()
                except Exception as e:
                    print(f"Token refresh failed: {e}")
                    self.creds = None

            if not self.creds:
                if not os.path.exists(self.credentials_path):
                    print(f"Credentials not found: {self.credentials_path}")
                    print("Please download OAuth2 credentials from Google Cloud Console")
                    return False

                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path,
                    self.SCOPES
                )
                self.creds = flow.run_local_server(port=8080)

            # Save token
            if self.token_path:
                with open(self.token_path, 'w') as token_file:
                    token_file.write(self.creds.to_json())

        # Build service
        try:
            self.service = build('mybusinessbusinessinformation', 'v1', credentials=self.creds)
            return True
        except Exception as e:
            print(f"Failed to build service: {e}")
            return False

    def search_businesses(self, query: str, location: str = None, radius: int = 5000) -> List[Dict]:
        """Search for businesses using Places API (no OAuth required).

        Args:
            query: Search query (e.g., "coffee shop", "restaurant")
            location: TILE code or "lat,lng" (e.g., "AA340" or "-33.87,151.21")
            radius: Search radius in meters (default 5000m = 5km)

        Returns:
            List of business dicts with place_id, name, address, etc.
        """
        if not self.places_api_key:
            print(f"No Places API key found in environment variable: {self.PLACES_API_KEY_ENV}")
            print("Add to .env: GOOGLE_PLACES_API_KEY=your_api_key")
            return []

        try:
            # Use Places API New (Text Search)
            import requests

            # Convert TILE to lat/lng if needed
            if location and not ',' in location:
                # TODO: Convert TILE code to lat/lng using grid system
                # For now, use Sydney as default
                location = "-33.87,151.21"

            url = "https://places.googleapis.com/v1/places:searchText"
            headers = {
                'Content-Type': 'application/json',
                'X-Goog-Api-Key': self.places_api_key,
                'X-Goog-FieldMask': 'places.id,places.displayName,places.formattedAddress,places.location,places.websiteUri,places.nationalPhoneNumber,places.rating,places.userRatingCount'
            }

            data = {
                'textQuery': query,
                'locationBias': {
                    'circle': {
                        'center': {
                            'latitude': float(location.split(',')[0]),
                            'longitude': float(location.split(',')[1])
                        },
                        'radius': radius
                    }
                }
            }

            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()

            result = response.json()
            places = result.get('places', [])

            # Normalize to our format
            businesses = []
            for place in places:
                businesses.append({
                    'google_place_id': place.get('id'),
                    'name': place.get('displayName', {}).get('text', 'Unknown'),
                    'raw_address': place.get('formattedAddress', ''),
                    'lat': place.get('location', {}).get('latitude'),
                    'lon': place.get('location', {}).get('longitude'),
                    'website': place.get('websiteUri'),
                    'phone': place.get('nationalPhoneNumber'),
                    'rating': place.get('rating'),
                    'review_count': place.get('userRatingCount'),
                    'source': 'google_places_api'
                })

            return businesses

        except Exception as e:
            print(f"Error searching businesses: {e}")
            return []

    def get_business_details(self, place_id: str) -> Optional[Dict]:
        """Get detailed business information.

        Args:
            place_id: Google Place ID

        Returns:
            Dict with complete business data or None
        """
        if not self.places_api_key:
            print(f"No Places API key found: {self.PLACES_API_KEY_ENV}")
            return None

        try:
            import requests

            url = f"https://places.googleapis.com/v1/places/{place_id}"
            headers = {
                'Content-Type': 'application/json',
                'X-Goog-Api-Key': self.places_api_key,
                'X-Goog-FieldMask': 'id,displayName,formattedAddress,location,websiteUri,nationalPhoneNumber,internationalPhoneNumber,rating,userRatingCount,businessStatus,types,regularOpeningHours'
            }

            response = requests.get(url, headers=headers)
            response.raise_for_status()

            place = response.json()

            # Normalize to our format
            return {
                'google_place_id': place.get('id'),
                'name': place.get('displayName', {}).get('text', 'Unknown'),
                'raw_address': place.get('formattedAddress', ''),
                'lat': place.get('location', {}).get('latitude'),
                'lon': place.get('location', {}).get('longitude'),
                'website': place.get('websiteUri'),
                'phone': place.get('nationalPhoneNumber') or place.get('internationalPhoneNumber'),
                'rating': place.get('rating'),
                'review_count': place.get('userRatingCount'),
                'business_status': place.get('businessStatus'),
                'category': ','.join(place.get('types', [])),
                'hours': place.get('regularOpeningHours'),
                'source': 'google_places_api'
            }

        except Exception as e:
            print(f"Error getting business details: {e}")
            return None

    def extract_website_domain(self, website: str) -> str:
        """Extract domain from website URL.

        Args:
            website: Website URL

        Returns:
            Domain (e.g., "acmecorp.com")
        """
        if not website:
            return ''

        # Remove protocol
        domain = website.lower()
        for prefix in ['https://', 'http://', '//']:
            if domain.startswith(prefix):
                domain = domain[len(prefix):]

        # Remove www.
        if domain.startswith('www.'):
            domain = domain[4:]

        # Remove path
        if '/' in domain:
            domain = domain.split('/')[0]

        return domain
