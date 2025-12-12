"""
Social Media API Clients for Business Intelligence
Integrations: Twitter/X API, Instagram Graph API, public profile data.

Legal Compliance:
- Uses official APIs only
- Respects platform Terms of Service
- Rate limiting per API requirements
- No scraping of non-public data
- User consent for authenticated endpoints

Data Sources:
- Twitter/X: Public followers, following, likes, influence metrics
- Instagram: Business account insights (via Facebook Graph API)
- Public profiles: Bio, links, location, verified status
"""

import os
import time
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass

try:
    import requests
except ImportError:
    requests = None


@dataclass
class SocialProfile:
    """Social media profile data."""
    platform: str  # twitter, instagram, facebook
    username: str
    profile_url: str
    display_name: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None
    followers_count: Optional[int] = None
    following_count: Optional[int] = None
    verified: bool = False
    profile_image_url: Optional[str] = None
    
    # Platform-specific
    twitter_id: Optional[str] = None
    instagram_id: Optional[str] = None
    facebook_page_id: Optional[str] = None


@dataclass
class InfluenceMetrics:
    """Influence and engagement metrics."""
    platform: str
    username: str
    followers: int
    engagement_rate: Optional[float] = None  # percentage
    avg_likes: Optional[int] = None
    avg_comments: Optional[int] = None
    top_hashtags: Optional[List[str]] = None
    audience_location: Optional[str] = None


class TwitterClient:
    """Twitter/X API client for public data extraction."""
    
    def __init__(self, bearer_token: Optional[str] = None):
        """Initialize Twitter client.
        
        Args:
            bearer_token: Twitter API v2 Bearer Token (from .env)
        """
        if requests is None:
            raise ImportError("requests required: pip install requests")
        
        self.bearer_token = bearer_token or os.getenv('TWITTER_BEARER_TOKEN')
        self.base_url = "https://api.twitter.com/2"
        self.rate_limit_remaining = {}
        
    def _headers(self) -> Dict[str, str]:
        """Get authorization headers."""
        if not self.bearer_token:
            raise ValueError("TWITTER_BEARER_TOKEN not set in .env")
        
        return {
            "Authorization": f"Bearer {self.bearer_token}",
            "User-Agent": "uDOS-BIZINTEL/1.0"
        }
    
    def _handle_rate_limit(self, response: requests.Response):
        """Handle rate limiting from API response.
        
        Args:
            response: API response
        """
        if 'x-rate-limit-remaining' in response.headers:
            remaining = int(response.headers['x-rate-limit-remaining'])
            if remaining < 5:
                reset_time = int(response.headers.get('x-rate-limit-reset', 0))
                wait_time = max(0, reset_time - int(time.time()))
                if wait_time > 0:
                    time.sleep(wait_time)
    
    def get_user_by_username(self, username: str) -> Optional[SocialProfile]:
        """Get Twitter user profile by username.
        
        Args:
            username: Twitter username (without @)
            
        Returns:
            SocialProfile or None
        """
        url = f"{self.base_url}/users/by/username/{username}"
        params = {
            'user.fields': 'id,name,username,description,location,url,verified,public_metrics,profile_image_url'
        }
        
        try:
            response = requests.get(url, headers=self._headers(), params=params, timeout=10)
            self._handle_rate_limit(response)
            response.raise_for_status()
            data = response.json()['data']
            
            return SocialProfile(
                platform='twitter',
                username=data['username'],
                profile_url=f"https://twitter.com/{data['username']}",
                display_name=data.get('name'),
                bio=data.get('description'),
                location=data.get('location'),
                website=data.get('url'),
                followers_count=data.get('public_metrics', {}).get('followers_count'),
                following_count=data.get('public_metrics', {}).get('following_count'),
                verified=data.get('verified', False),
                profile_image_url=data.get('profile_image_url'),
                twitter_id=data['id']
            )
        except Exception as e:
            print(f"Error fetching Twitter user {username}: {e}")
            return None
    
    def get_followers(self, user_id: str, max_results: int = 100) -> List[str]:
        """Get list of follower IDs (public data).
        
        Args:
            user_id: Twitter user ID
            max_results: Maximum followers to return (max 1000 per API)
            
        Returns:
            List of follower user IDs
        """
        url = f"{self.base_url}/users/{user_id}/followers"
        params = {'max_results': min(max_results, 1000)}
        
        try:
            response = requests.get(url, headers=self._headers(), params=params, timeout=10)
            self._handle_rate_limit(response)
            response.raise_for_status()
            data = response.json()
            
            return [user['id'] for user in data.get('data', [])]
        except Exception as e:
            print(f"Error fetching followers for {user_id}: {e}")
            return []
    
    def get_influence_metrics(self, username: str) -> Optional[InfluenceMetrics]:
        """Calculate influence metrics for a user.
        
        Args:
            username: Twitter username
            
        Returns:
            InfluenceMetrics or None
        """
        profile = self.get_user_by_username(username)
        if not profile:
            return None
        
        return InfluenceMetrics(
            platform='twitter',
            username=username,
            followers=profile.followers_count or 0,
            # Note: Engagement metrics require tweet data (separate endpoint)
        )


class InstagramGraphClient:
    """Instagram Graph API client (for Business/Creator accounts only)."""
    
    def __init__(self, access_token: Optional[str] = None):
        """Initialize Instagram Graph API client.
        
        Args:
            access_token: Facebook Graph API access token
        """
        if requests is None:
            raise ImportError("requests required: pip install requests")
        
        self.access_token = access_token or os.getenv('FACEBOOK_ACCESS_TOKEN')
        self.base_url = "https://graph.facebook.com/v18.0"
    
    def get_instagram_business_account(self, page_id: str) -> Optional[str]:
        """Get Instagram Business Account ID from Facebook Page.
        
        Args:
            page_id: Facebook Page ID
            
        Returns:
            Instagram Business Account ID or None
        """
        if not self.access_token:
            raise ValueError("FACEBOOK_ACCESS_TOKEN not set in .env")
        
        url = f"{self.base_url}/{page_id}"
        params = {
            'fields': 'instagram_business_account',
            'access_token': self.access_token
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get('instagram_business_account', {}).get('id')
        except Exception as e:
            print(f"Error fetching Instagram account for page {page_id}: {e}")
            return None
    
    def get_profile(self, instagram_account_id: str) -> Optional[SocialProfile]:
        """Get Instagram Business profile data.
        
        Args:
            instagram_account_id: Instagram Business Account ID
            
        Returns:
            SocialProfile or None
        """
        if not self.access_token:
            raise ValueError("FACEBOOK_ACCESS_TOKEN not set in .env")
        
        url = f"{self.base_url}/{instagram_account_id}"
        params = {
            'fields': 'username,name,biography,website,followers_count,follows_count,media_count,profile_picture_url',
            'access_token': self.access_token
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return SocialProfile(
                platform='instagram',
                username=data.get('username'),
                profile_url=f"https://instagram.com/{data.get('username')}",
                display_name=data.get('name'),
                bio=data.get('biography'),
                website=data.get('website'),
                followers_count=data.get('followers_count'),
                following_count=data.get('follows_count'),
                profile_image_url=data.get('profile_picture_url'),
                instagram_id=instagram_account_id
            )
        except Exception as e:
            print(f"Error fetching Instagram profile {instagram_account_id}: {e}")
            return None
    
    def get_influence_metrics(self, instagram_account_id: str) -> Optional[InfluenceMetrics]:
        """Get influence metrics for Instagram Business account.
        
        Args:
            instagram_account_id: Instagram Business Account ID
            
        Returns:
            InfluenceMetrics or None
        """
        profile = self.get_profile(instagram_account_id)
        if not profile:
            return None
        
        # Get insights (requires additional permissions)
        url = f"{self.base_url}/{instagram_account_id}/insights"
        params = {
            'metric': 'impressions,reach,profile_views',
            'period': 'day',
            'access_token': self.access_token
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            insights_data = response.json()
            
            return InfluenceMetrics(
                platform='instagram',
                username=profile.username,
                followers=profile.followers_count or 0,
                # Parse insights for engagement metrics
            )
        except Exception:
            # Return basic metrics if insights unavailable
            return InfluenceMetrics(
                platform='instagram',
                username=profile.username,
                followers=profile.followers_count or 0
            )


class SocialEnrichment:
    """Unified social media enrichment service."""
    
    def __init__(self):
        """Initialize social enrichment with all clients."""
        self.twitter = TwitterClient()
        self.instagram = InstagramGraphClient()
    
    def enrich_from_website(self, website_url: str, website_html: str) -> Dict[str, SocialProfile]:
        """Extract social profiles from website HTML.
        
        Args:
            website_url: Base website URL
            website_html: HTML content
            
        Returns:
            Dictionary of platform -> SocialProfile
        """
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(website_html, 'html.parser')
        profiles = {}
        
        # Find Twitter links
        twitter_links = soup.find_all('a', href=lambda x: x and 'twitter.com' in x)
        for link in twitter_links:
            username_match = link['href'].split('twitter.com/')[-1].split('/')[0].strip('@')
            if username_match:
                profile = self.twitter.get_user_by_username(username_match)
                if profile:
                    profiles['twitter'] = profile
                    break
        
        # Find Instagram links
        instagram_links = soup.find_all('a', href=lambda x: x and 'instagram.com' in x)
        for link in instagram_links:
            username_match = link['href'].split('instagram.com/')[-1].split('/')[0].strip('@')
            if username_match:
                # Note: Would need Facebook Page ID to fetch Business account
                # Store username for manual linking
                profiles['instagram_username'] = username_match
                break
        
        return profiles
    
    def get_all_metrics(self, business_id: str, social_handles: Dict[str, str]) -> List[InfluenceMetrics]:
        """Get influence metrics for all social platforms.
        
        Args:
            business_id: uDOS business ID
            social_handles: Dictionary of platform -> username/id
            
        Returns:
            List of InfluenceMetrics
        """
        metrics = []
        
        if 'twitter' in social_handles:
            twitter_metrics = self.twitter.get_influence_metrics(social_handles['twitter'])
            if twitter_metrics:
                metrics.append(twitter_metrics)
        
        if 'instagram_account_id' in social_handles:
            ig_metrics = self.instagram.get_influence_metrics(social_handles['instagram_account_id'])
            if ig_metrics:
                metrics.append(ig_metrics)
        
        return metrics
