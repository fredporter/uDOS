"""
Keyword Generator for Business Intelligence Automation
Uses Gemini API to generate contextual search keywords for website scraping and business discovery.

Integration:
- uDOS workflows (TypeScript in .md files)
- Automated business research
- Market analysis campaigns
- Competitor discovery

Example Usage:
    generator = KeywordGenerator()
    keywords = generator.generate_keywords(
        industry="live music venues",
        location_context="Sydney, Australia",
        business_type="small_medium"
    )
    # Returns: ["live music Sydney", "concert venues NSW", "music bars inner west", ...]
"""

import os
import json
from typing import List, Dict, Optional
from dataclasses import dataclass

try:
    import google.generativeai as genai
except ImportError:
    genai = None


@dataclass
class KeywordSet:
    """Generated keyword set with metadata."""
    primary_keywords: List[str]  # Main search terms
    location_variants: List[str]  # Location-specific variations
    industry_terms: List[str]     # Industry-specific terminology
    competitor_terms: List[str]   # Competitor discovery terms
    niche_terms: List[str]        # Niche/specialized keywords
    context: Dict                 # Original generation context


class KeywordGenerator:
    """Generate contextual keywords using Gemini API for business intelligence automation."""
    
    # Industry templates for offline fallback
    INDUSTRY_TEMPLATES = {
        'music_venue': [
            "{location} live music",
            "{location} concert venues",
            "{location} music bars",
            "{location} performance spaces",
            "gig venues {location}",
            "music clubs {location}"
        ],
        'restaurant': [
            "{location} restaurants",
            "{location} dining",
            "{location} cafes",
            "best restaurants {location}",
            "food {location}",
            "{location} eateries"
        ],
        'retail': [
            "{location} shops",
            "{location} stores",
            "{location} boutiques",
            "shopping {location}",
            "{location} retail"
        ],
        'professional_services': [
            "{location} services",
            "{location} consultants",
            "{location} professionals",
            "business services {location}"
        ]
    }
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize keyword generator.
        
        Args:
            api_key: Gemini API key (from .env if not provided)
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        self.model = None
        
        if genai and self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def generate_keywords(
        self,
        industry: str,
        location_context: Optional[str] = None,
        business_type: Optional[str] = None,
        additional_context: Optional[str] = None,
        max_keywords: int = 20
    ) -> KeywordSet:
        """Generate contextual keywords for business search.
        
        Args:
            industry: Industry/category (e.g., "live music venues", "coffee shops")
            location_context: Location description (e.g., "Sydney CBD", "Brooklyn")
            business_type: Business size/type (e.g., "small_medium", "enterprise", "independent")
            additional_context: Extra context for generation
            max_keywords: Maximum keywords to generate
            
        Returns:
            KeywordSet with categorized keywords
        """
        if self.model:
            return self._generate_with_gemini(
                industry, location_context, business_type,
                additional_context, max_keywords
            )
        else:
            return self._generate_offline(
                industry, location_context, max_keywords
            )
    
    def _generate_with_gemini(
        self,
        industry: str,
        location_context: Optional[str],
        business_type: Optional[str],
        additional_context: Optional[str],
        max_keywords: int
    ) -> KeywordSet:
        """Generate keywords using Gemini API.
        
        Args:
            industry: Industry/category
            location_context: Location description
            business_type: Business size/type
            additional_context: Extra context
            max_keywords: Maximum keywords
            
        Returns:
            KeywordSet with AI-generated keywords
        """
        prompt = self._build_gemini_prompt(
            industry, location_context, business_type,
            additional_context, max_keywords
        )
        
        try:
            response = self.model.generate_content(prompt)
            return self._parse_gemini_response(
                response.text,
                industry,
                location_context
            )
        except Exception as e:
            print(f"Gemini API error: {e}")
            # Fallback to offline generation
            return self._generate_offline(industry, location_context, max_keywords)
    
    def _build_gemini_prompt(
        self,
        industry: str,
        location_context: Optional[str],
        business_type: Optional[str],
        additional_context: Optional[str],
        max_keywords: int
    ) -> str:
        """Build Gemini prompt for keyword generation.
        
        Args:
            industry: Industry/category
            location_context: Location description
            business_type: Business size/type
            additional_context: Extra context
            max_keywords: Maximum keywords
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""Generate {max_keywords} search keywords for finding businesses in this category:

Industry: {industry}
"""
        
        if location_context:
            prompt += f"Location: {location_context}\n"
        
        if business_type:
            prompt += f"Business Type: {business_type}\n"
        
        if additional_context:
            prompt += f"Additional Context: {additional_context}\n"
        
        prompt += """
Return keywords in JSON format with these categories:

{
  "primary_keywords": ["main search terms"],
  "location_variants": ["location-specific variations"],
  "industry_terms": ["industry-specific terminology"],
  "competitor_terms": ["competitor discovery terms"],
  "niche_terms": ["niche/specialized keywords"]
}

Guidelines:
1. Primary keywords should be broad, high-volume search terms
2. Location variants should include neighborhoods, regions, abbreviations
3. Industry terms should use insider jargon and technical terms
4. Competitor terms should help find similar businesses
5. Niche terms should target specific sub-categories or specializations

Return ONLY the JSON, no explanation."""
        
        return prompt
    
    def _parse_gemini_response(
        self,
        response_text: str,
        industry: str,
        location_context: Optional[str]
    ) -> KeywordSet:
        """Parse Gemini API response into KeywordSet.
        
        Args:
            response_text: Raw response from Gemini
            industry: Original industry input
            location_context: Original location input
            
        Returns:
            Parsed KeywordSet
        """
        try:
            # Extract JSON from response (may have markdown formatting)
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_text = response_text[json_start:json_end]
                data = json.loads(json_text)
                
                return KeywordSet(
                    primary_keywords=data.get('primary_keywords', []),
                    location_variants=data.get('location_variants', []),
                    industry_terms=data.get('industry_terms', []),
                    competitor_terms=data.get('competitor_terms', []),
                    niche_terms=data.get('niche_terms', []),
                    context={
                        'industry': industry,
                        'location': location_context,
                        'source': 'gemini_api'
                    }
                )
            else:
                raise ValueError("No JSON found in response")
        
        except Exception as e:
            print(f"Error parsing Gemini response: {e}")
            # Fallback to offline generation
            return self._generate_offline(industry, location_context, 20)
    
    def _generate_offline(
        self,
        industry: str,
        location_context: Optional[str],
        max_keywords: Optional[int] = None
    ) -> KeywordSet:
        """Generate keywords using offline templates (no API required).
        
        Args:
            industry: Industry/category
            location_context: Location description
            max_keywords: Maximum keywords (default: 20)
            
        Returns:
            KeywordSet with template-based keywords
        """
        if max_keywords is None:
            max_keywords = 20
        
        # Detect industry template
        industry_lower = industry.lower()
        template_key = None
        
        for key in self.INDUSTRY_TEMPLATES:
            if key.replace('_', ' ') in industry_lower:
                template_key = key
                break
        
        # Use generic template if no match
        if not template_key:
            template_key = 'professional_services'
        
        templates = self.INDUSTRY_TEMPLATES[template_key]
        location = location_context or ""
        
        # Generate primary keywords
        primary_keywords = []
        for template in templates:
            keyword = template.format(location=location).strip()
            if keyword:
                primary_keywords.append(keyword)
        
        # Add industry term variations
        industry_terms = [
            industry,
            industry.replace(' ', ''),
            industry.replace('_', ' ')
        ]
        
        # Location variants
        location_variants = []
        if location_context:
            # Extract city/region
            parts = location_context.split(',')
            for part in parts:
                location_variants.append(part.strip())
            
            # Add common abbreviations
            if 'Australia' in location_context:
                location_variants.append('AU')
            if 'Sydney' in location_context:
                location_variants.extend(['SYD', 'NSW'])
        
        return KeywordSet(
            primary_keywords=primary_keywords[:max_keywords//2],
            location_variants=list(set(location_variants))[:max_keywords//5],
            industry_terms=list(set(industry_terms))[:max_keywords//5],
            competitor_terms=[],
            niche_terms=[],
            context={
                'industry': industry,
                'location': location_context,
                'source': 'offline_templates'
            }
        )
    
    def generate_for_workflow(
        self,
        workflow_config: Dict
    ) -> KeywordSet:
        """Generate keywords from uDOS workflow configuration.
        
        Args:
            workflow_config: Workflow dict with industry, location, filters
            
        Returns:
            KeywordSet optimized for workflow automation
            
        Example:
            config = {
                'industry': 'live music venues',
                'location': 'Sydney CBD',
                'business_type': 'small_medium',
                'filters': {
                    'min_capacity': 100,
                    'has_liquor_license': True
                }
            }
        """
        return self.generate_keywords(
            industry=workflow_config.get('industry', ''),
            location_context=workflow_config.get('location'),
            business_type=workflow_config.get('business_type'),
            additional_context=json.dumps(workflow_config.get('filters', {}))
        )
    
    def export_for_script(self, keyword_set: KeywordSet) -> str:
        """Export keywords for TypeScript script embedding.
        
        Args:
            keyword_set: KeywordSet to export
            
        Returns:
            TypeScript script snippet with keyword variables
        """
        output = [
            "# Generated Keywords",
            f"{{$KEYWORDS.PRIMARY}} = {json.dumps(keyword_set.primary_keywords)}",
            f"{{$KEYWORDS.LOCATION}} = {json.dumps(keyword_set.location_variants)}",
            f"{{$KEYWORDS.INDUSTRY}} = {json.dumps(keyword_set.industry_terms)}",
            f"{{$KEYWORDS.COMPETITOR}} = {json.dumps(keyword_set.competitor_terms)}",
            f"{{$KEYWORDS.NICHE}} = {json.dumps(keyword_set.niche_terms)}",
            "",
            "# Usage in workflow:",
            "# LOOP {$KEYWORDS.PRIMARY}",
            "#   CLOUD BUSINESS SEARCH {$ITEM}",
            "# END LOOP"
        ]
        
        return '\n'.join(output)
