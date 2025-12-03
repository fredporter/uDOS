# uDOS v1.2.0 - Offline-First AI Engine

"""
Enhanced offline AI system with intelligent knowledge synthesis.

Features (v1.2.0):
- Knowledge bank integration (166+ survival guides)
- FAQ system with keyword matching
- User memory and context tracking
- Prompt template system
- Intent analysis with confidence scoring
- Response synthesis from multiple sources
- Offline-first architecture (no API calls by default)

Target: 90%+ queries answered offline using local knowledge
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
from urllib.request import urlopen
from urllib.error import URLError


@dataclass
class OfflineResponse:
    """Response from offline AI engine."""
    content: str
    confidence: float  # 0.0-1.0
    sources: List[str]  # Source files/FAQs used
    method: str  # knowledge_bank | faq | template | pattern
    suggestions: List[str]  # Related queries/topics


class OfflineEngine:
    """
    Offline-first AI engine using knowledge bank synthesis.
    No API calls - everything from local resources.
    """

    def __init__(self, knowledge_file='core/data/faq.json', prompt_templates_file='core/data/prompts.json'):
        self.knowledge_file = knowledge_file
        self.prompt_templates_file = prompt_templates_file
        
        # Load components
        self.faq = self.load_knowledge()  # Legacy name for FAQ data
        self.knowledge = self.faq  # Alias for backward compatibility
        self.prompt_templates = self.load_prompt_templates()
        self.is_online = self.check_connection()
        self.command_history = []  # Track recent commands for context
        
        # Lazy load heavy components
        self._knowledge_manager = None
        self._user_memory = None

    @property
    def knowledge_manager(self):
        """Lazy load knowledge manager."""
        if self._knowledge_manager is None:
            try:
                from core.knowledge.bank import get_knowledge_manager
                self._knowledge_manager = get_knowledge_manager()
            except Exception as e:
                # Fallback if knowledge manager unavailable
                self._knowledge_manager = None
        return self._knowledge_manager
    
    @property
    def user_memory(self):
        """Lazy load user memory manager."""
        if self._user_memory is None:
            self._user_memory = UserMemoryManager()
        return self._user_memory

    def load_knowledge(self):
        """Load offline knowledge base from unified FAQ"""
        try:
            with open(self.knowledge_file, 'r') as f:
                return json.load(f)
        except:
            # Fallback minimal knowledge if file doesn't exist
            return {
                "FAQ": {},
                "QUICK_TIPS": {},
                "OFFLINE_ASSISTANCE": {
                    "PROMPTS": {},
                    "RESPONSES": {
                        "OFFLINE_MODE": "Working offline. AI features unavailable.",
                        "NO_MATCH": "Not sure what you mean. Try 'HELP'."
                    }
                }
            }
    
    def load_prompt_templates(self):
        """Load prompt templates for response generation."""
        try:
            if os.path.exists(self.prompt_templates_file):
                with open(self.prompt_templates_file, 'r') as f:
                    return json.load(f)
        except:
            pass
        
        # Default templates if file doesn't exist
        return {
            "question_answer": {
                "system": "You are a survival knowledge expert. Provide accurate, practical information based on the knowledge bank.",
                "user": "Question: {query}\n\nContext from knowledge bank:\n{context}\n\nProvide a comprehensive answer."
            },
            "guide_summary": {
                "system": "Summarize survival guides in clear, actionable points.",
                "user": "Summarize this guide:\n{content}"
            },
            "concept_explain": {
                "system": "Explain survival concepts in simple terms.",
                "user": "Explain: {concept}\n\nReference material:\n{context}"
            }
        }

    def check_connection(self):
        """Check if internet connection is available."""
        try:
            urlopen('https://www.google.com', timeout=2)
            return True
        except (URLError, Exception):
            return False
    
    def generate(self, query: str, context: Dict[str, Any] = None) -> OfflineResponse:
        """
        Generate response using local resources only (primary entry point).
        
        Args:
            query: User query/question
            context: Optional context dict with additional info
            
        Returns:
            OfflineResponse with synthesized answer
        """
        # Step 1: Analyze intent
        intent = self._analyze_intent(query)
        
        # Step 2: Search knowledge bank (highest priority)
        kb_results = self._search_knowledge_bank(query)
        
        # Step 3: Search FAQ
        faq_results = self.search_faq(query)
        
        # Step 4: Check user memory
        user_context = self._get_user_context(query)
        
        # Step 5: Select appropriate template
        template = self._select_template(intent, kb_results, faq_results)
        
        # Step 6: Synthesize response
        response_text = self._synthesize_response(
            query=query,
            intent=intent,
            kb_results=kb_results,
            faq_results=faq_results,
            user_context=user_context,
            template=template,
            context=context
        )
        
        # Step 7: Calculate confidence and collect sources
        confidence = self._calculate_confidence(kb_results, faq_results)
        sources = self._extract_sources(kb_results, faq_results)
        suggestions = self._generate_suggestions(query, kb_results)
        
        return OfflineResponse(
            content=response_text,
            confidence=confidence,
            sources=sources,
            method=self._determine_method(kb_results, faq_results),
            suggestions=suggestions
        )
    
    def _search_knowledge_bank(self, query: str) -> List[Dict]:
        """Search knowledge bank for relevant guides."""
        if not self.knowledge_manager:
            return []
        
        try:
            # Use knowledge manager's full-text search
            results = self.knowledge_manager.search(query, limit=5)
            return results
        except Exception as e:
            return []
    
    def _get_user_context(self, query: str) -> Dict:
        """Get relevant context from user memory."""
        return {
            "recent_commands": self.command_history[-5:],
            "query_history": []  # TODO: Track query history
        }
    
    def _analyze_intent(self, query: str) -> str:
        """
        Analyze query intent.
        
        Returns:
            Intent type: question | explanation | how_to | summary | comparison | list
        """
        query_lower = query.lower()
        
        # Question patterns
        if any(q in query_lower for q in ["what is", "what are", "what's", "who", "when", "where"]):
            return "question"
        
        # Explanation patterns
        if any(e in query_lower for e in ["explain", "why", "how does", "how do"]):
            return "explanation"
        
        # How-to patterns
        if any(h in query_lower for h in ["how to", "how can i", "steps to", "guide to"]):
            return "how_to"
        
        # Summary patterns
        if any(s in query_lower for s in ["summarize", "summary", "overview", "brief"]):
            return "summary"
        
        # Comparison patterns
        if any(c in query_lower for c in ["compare", "difference", "versus", "vs", "better"]):
            return "comparison"
        
        # List patterns
        if any(l in query_lower for l in ["list", "types of", "kinds of", "methods for"]):
            return "list"
        
        # Default
        return "question"
    
    def _select_template(self, intent: str, kb_results: List, faq_results: List) -> Dict:
        """Select appropriate prompt template based on intent and available data."""
        # If we have knowledge bank results, use question_answer template
        if kb_results:
            return self.prompt_templates.get("question_answer", {})
        
        # If FAQ match, use FAQ template
        if faq_results:
            return {"system": "Answer based on FAQ", "user": "{query}"}
        
        # Intent-specific templates
        template_map = {
            "summary": "guide_summary",
            "explanation": "concept_explain",
            "how_to": "question_answer",
            "comparison": "question_answer"
        }
        
        template_name = template_map.get(intent, "question_answer")
        return self.prompt_templates.get(template_name, {})
    
    def _synthesize_response(self, query: str, intent: str, kb_results: List,
                            faq_results: List, user_context: Dict, 
                            template: Dict, context: Any) -> str:
        """
        Synthesize response from multiple sources.
        This is the core intelligence of the offline AI.
        """
        # Priority 1: Direct FAQ match (fastest)
        if faq_results:
            faq_id, faq_entry = faq_results[0]
            response = f"💡 {faq_entry.get('answer', '')}\n\n"
            if faq_entry.get('commands'):
                response += f"**Related commands:** {', '.join(faq_entry['commands'])}\n"
            return response.strip()
        
        # Priority 2: Knowledge bank synthesis (most comprehensive)
        if kb_results:
            return self._synthesize_from_knowledge_bank(query, kb_results, intent)
        
        # Priority 3: Pattern matching fallback
        return self._pattern_matching_fallback(query, intent, context)
    
    def _synthesize_from_knowledge_bank(self, query: str, kb_results: List, intent: str) -> str:
        """
        Synthesize response from knowledge bank search results.
        Intelligently combines multiple sources into coherent answer.
        """
        if not kb_results:
            return self._pattern_matching_fallback(query, intent, None)
        
        # Build response header
        response_parts = []
        response_parts.append(f"📚 **Knowledge Bank Results** (found {len(kb_results)} guides)")
        response_parts.append("")
        
        # For how-to and explanation intents, provide detailed synthesis
        if intent in ["how_to", "explanation"]:
            # Use the top result for detailed answer
            top_result = kb_results[0]
            response_parts.append(f"### {top_result.get('title', 'Guide')}")
            response_parts.append("")
            
            # Extract key sections from content
            content = top_result.get('content', '')
            key_sections = self._extract_key_sections(content, query)
            
            if key_sections:
                response_parts.append(key_sections)
            else:
                # Fallback: First 500 chars
                preview = content[:500].strip()
                if len(content) > 500:
                    preview += "..."
                response_parts.append(preview)
            
            response_parts.append("")
            response_parts.append(f"📖 **Source:** `{top_result.get('file_path', 'unknown')}`")
            
            # Add related guides
            if len(kb_results) > 1:
                response_parts.append("")
                response_parts.append("**Related guides:**")
                for result in kb_results[1:4]:  # Show up to 3 more
                    title = result.get('title', 'Untitled')
                    file_path = result.get('file_path', '')
                    response_parts.append(f"  • {title} (`{file_path}`)")
        
        # For list intents, show multiple results
        elif intent == "list":
            response_parts.append("**Available guides on this topic:**")
            response_parts.append("")
            for i, result in enumerate(kb_results[:10], 1):  # List up to 10
                title = result.get('title', 'Untitled')
                category = result.get('category', 'general')
                word_count = result.get('word_count', 0)
                response_parts.append(f"{i}. **{title}**")
                response_parts.append(f"   Category: {category} | Words: {word_count}")
                response_parts.append("")
        
        # For comparison intents, compare multiple guides
        elif intent == "comparison":
            response_parts.append("**Comparison of methods:**")
            response_parts.append("")
            for result in kb_results[:3]:  # Compare up to 3
                title = result.get('title', 'Method')
                content = result.get('content', '')
                # Extract first paragraph or summary
                summary = self._extract_summary(content)
                response_parts.append(f"**{title}:**")
                response_parts.append(summary)
                response_parts.append("")
        
        # For questions and summaries, provide concise overview
        else:
            top_result = kb_results[0]
            response_parts.append(f"**{top_result.get('title', 'Guide')}**")
            response_parts.append("")
            summary = self._extract_summary(top_result.get('content', ''))
            response_parts.append(summary)
            response_parts.append("")
            response_parts.append(f"📖 Source: `{top_result.get('file_path', 'unknown')}`")
        
        # Add footer with search info
        response_parts.append("")
        response_parts.append("---")
        response_parts.append("💡 **Tip:** Use `CAT <file>` to read the full guide")
        
        return "\n".join(response_parts)
    
    def _extract_key_sections(self, content: str, query: str) -> str:
        """Extract sections from content most relevant to query."""
        # Split content into paragraphs
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        # Find query keywords
        keywords = set(query.lower().split())
        keywords = {k for k in keywords if len(k) > 3}  # Filter short words
        
        # Score paragraphs by keyword matches
        scored_paragraphs = []
        for para in paragraphs:
            para_lower = para.lower()
            score = sum(1 for keyword in keywords if keyword in para_lower)
            if score > 0:
                scored_paragraphs.append((score, para))
        
        # Sort by score and take top 3 paragraphs
        scored_paragraphs.sort(reverse=True, key=lambda x: x[0])
        top_paragraphs = [para for score, para in scored_paragraphs[:3]]
        
        if top_paragraphs:
            return "\n\n".join(top_paragraphs)
        
        return ""
    
    def _extract_summary(self, content: str) -> str:
        """Extract a concise summary from content."""
        # Try to find a summary section
        summary_patterns = [
            r'##\s+Summary\s*\n\n(.+?)(?=\n##|\Z)',
            r'##\s+Overview\s*\n\n(.+?)(?=\n##|\Z)',
            r'##\s+Introduction\s*\n\n(.+?)(?=\n##|\Z)'
        ]
        
        for pattern in summary_patterns:
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if match:
                summary = match.group(1).strip()
                # Limit to first 300 chars
                if len(summary) > 300:
                    summary = summary[:300] + "..."
                return summary
        
        # Fallback: First paragraph after title
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip() and not p.startswith('#')]
        if paragraphs:
            summary = paragraphs[0]
            if len(summary) > 300:
                summary = summary[:300] + "..."
            return summary
        
        return "No summary available."
    
    def _pattern_matching_fallback(self, query: str, intent: str, context: Any) -> str:
        """Fallback to pattern matching when no knowledge bank results."""
        prompts = self.faq.get('OFFLINE_ASSISTANCE', {}).get('PROMPTS', {})
        
        # Try pattern matching
        intent_match, confidence, intent_data = self.analyze_intent(query)
        
        if intent_match and confidence > 0.7:
            if intent_match == 'HELP_REQUEST':
                return self._handle_help_request(query, intent_data)
            elif intent_match == 'FILE_SUGGESTION':
                return self._handle_file_suggestion(query, intent_data)
            elif intent_match == 'COMMAND_SUGGESTION':
                return self._handle_command_suggestion(query, intent_data)
        
        # Ultimate fallback
        return (
            f"ℹ️  No direct match found in knowledge bank.\n\n"
            f"**Suggestions:**\n"
            f"  • Try more specific keywords\n"
            f"  • Use `MEMORY SEARCH <topic>` to search all knowledge tiers\n"
            f"  • Use `GUIDE <category>` to browse survival guides\n"
            f"  • Use `HELP` to see available commands\n\n"
            f"💡 For AI-powered answers, ensure GEMINI_API_KEY is set and use online mode."
        )
    
    def _calculate_confidence(self, kb_results: List, faq_results: List) -> float:
        """Calculate confidence score based on available data."""
        if not kb_results and not faq_results:
            return 0.3  # Low confidence with no data
        
        confidence = 0.5  # Base confidence
        
        # Knowledge bank results boost confidence significantly
        if kb_results:
            # More results = higher confidence (up to a point)
            kb_boost = min(len(kb_results) * 0.15, 0.4)
            confidence += kb_boost
        
        # FAQ match boosts confidence
        if faq_results:
            confidence += 0.2
        
        # Cap at 0.95 (never 100% without human verification)
        return min(confidence, 0.95)
    
    def _extract_sources(self, kb_results: List, faq_results: List) -> List[str]:
        """Extract source references."""
        sources = []
        
        # Add knowledge bank sources
        for result in kb_results[:5]:
            file_path = result.get('file_path', '')
            if file_path:
                sources.append(file_path)
        
        # Add FAQ sources
        for faq_id, faq_entry in faq_results[:3]:
            sources.append(f"FAQ: {faq_id}")
        
        return sources
    
    def _determine_method(self, kb_results: List, faq_results: List) -> str:
        """Determine which method was used for response."""
        if kb_results:
            return "knowledge_bank"
        elif faq_results:
            return "faq"
        else:
            return "pattern"
    
    def _generate_suggestions(self, query: str, kb_results: List) -> List[str]:
        """Generate related query suggestions."""
        suggestions = []
        
        # If we have KB results, suggest related categories
        if kb_results:
            categories = set(r.get('category', '') for r in kb_results if r.get('category'))
            for cat in list(categories)[:3]:
                suggestions.append(f"Explore more in: {cat}")
        
        # Suggest command variations
        if "how to" in query.lower():
            suggestions.append("Try: GUIDE <category> for step-by-step guides")
        
        return suggestions
    
    # ========================================================================
    # LEGACY COMPATIBILITY METHODS (maintain backward compatibility)
    # ========================================================================
    
    def generate_response(self, user_input, context=None):
        """
        Legacy method for backward compatibility.
        Redirects to new generate() method.
        """
        response = self.generate(user_input, context)
        
        # Format for legacy callers
        return response.content

    def analyze_intent(self, user_input):
        """
        Analyze user input to determine intent using pattern matching.
        Legacy method - returns (intent_type, confidence, matched_data)
        """
        user_input_lower = user_input.lower()

        prompts = self.faq.get('OFFLINE_ASSISTANCE', {}).get('PROMPTS', {})

        for intent_name, intent_data in prompts.items():
            patterns = intent_data.get('PATTERN', [])
            regex_patterns = intent_data.get('REGEX', [])

            # Check simple patterns
            for pattern in patterns:
                if pattern.lower() in user_input_lower:
                    return intent_name, 0.8, intent_data

            # Check regex patterns
            for regex_pattern in regex_patterns:
                try:
                    if re.search(regex_pattern, user_input_lower, re.IGNORECASE):
                        return intent_name, 0.9, intent_data  # Higher confidence for regex
                except re.error:
                    # Invalid regex, skip
                    continue

        return None, 0.0, None

    def search_faq(self, user_input):
        """Search FAQ for relevant answers based on keywords."""
        user_input_lower = user_input.lower()
        faq_data = self.faq.get('FAQ', {})
        matches = []

        for faq_id, faq_entry in faq_data.items():
            keywords = faq_entry.get('keywords', [])
            # Check if any keyword matches
            for keyword in keywords:
                if keyword.lower() in user_input_lower:
                    matches.append((faq_id, faq_entry, len(keyword)))  # Track keyword length for relevance
                    break

        # Sort by keyword length (longer = more specific = more relevant)
        matches.sort(key=lambda x: x[2], reverse=True)

        return [m[:2] for m in matches]  # Return (faq_id, faq_entry) tuples

    def analyze_intent(self, user_input):
        """
        Analyze user input to determine intent using pattern matching.
        Supports both simple string matching and regex patterns.
        Returns: (intent_type, confidence, matched_data)
        """
        user_input_lower = user_input.lower()

        prompts = self.knowledge.get('OFFLINE_ASSISTANCE', {}).get('PROMPTS', {})

        for intent_name, intent_data in prompts.items():
            patterns = intent_data.get('PATTERN', [])
            regex_patterns = intent_data.get('REGEX', [])

            # Check simple patterns
            for pattern in patterns:
                if pattern.lower() in user_input_lower:
                    return intent_name, 0.8, intent_data

            # Check regex patterns
            for regex_pattern in regex_patterns:
                try:
                    if re.search(regex_pattern, user_input_lower, re.IGNORECASE):
                        return intent_name, 0.9, intent_data  # Higher confidence for regex
                except re.error:
                    # Invalid regex, skip
                    continue

        return None, 0.0, None

    def search_faq(self, user_input):
        """Search FAQ for relevant answers based on keywords."""
        user_input_lower = user_input.lower()
        faq_data = self.faq.get('FAQ', {})
        matches = []

        for faq_id, faq_entry in faq_data.items():
            keywords = faq_entry.get('keywords', [])
            # Check if any keyword matches
            for keyword in keywords:
                if keyword.lower() in user_input_lower:
                    matches.append((faq_id, faq_entry, len(keyword)))  # Track keyword length for relevance
                    break

        # Sort by keyword length (longer = more specific = more relevant)
        matches.sort(key=lambda x: x[2], reverse=True)

        return [m[:2] for m in matches]  # Return (faq_id, faq_entry) tuples

    def generate_response(self, user_input, context=None):
        """
        Generate a helpful response based on user input.
        Falls back to offline logic when internet unavailable.
        """
        # First check FAQ for direct answers
        faq_matches = self.search_faq(user_input)
        if faq_matches:
            faq_id, faq_entry = faq_matches[0]  # Use best match
            response = f"💡 {faq_entry.get('answer', '')}\n\n"
            if faq_entry.get('commands'):
                response += f"Related commands: {', '.join(faq_entry['commands'])}"
            return response

        # Fall back to pattern matching
        intent, confidence, intent_data = self.analyze_intent(user_input)

        if not intent:
            return self.prompts.get('RESPONSES', {}).get('NO_MATCH',
                "Not sure what you mean. Try 'HELP'.")

        # Generate response based on intent
        if intent == 'HELP_REQUEST':
            return self._handle_help_request(user_input, intent_data)
        elif intent == 'FILE_SUGGESTION':
            return self._handle_file_suggestion(user_input, intent_data)
        elif intent == 'SUMMARIZE_REQUEST':
            return self._handle_summarize(user_input, intent_data, context)
        elif intent == 'COMMAND_SUGGESTION':
            return self._handle_command_suggestion(user_input, intent_data)
        elif intent == 'ERROR_HELP':
            return self._handle_error_help(user_input, intent_data)
        elif intent == 'OFFLINE_ANALYSIS':
            return self._handle_analysis(user_input, intent_data, context)

        return intent_data.get('FALLBACK', "I can help with that. Try being more specific.")

    def _handle_help_request(self, user_input, intent_data):
        """Handle help-related questions."""
        # Extract topic from user input
        topic = user_input.replace('help', '').replace('how do i', '').replace('what is', '').strip()

        response = intent_data.get('RESPONSE_TEMPLATE', '{info}')
        info = f"Available commands: CATALOG, LOAD, SAVE, ASK, GRID, HELP, REPAIR, UNDO, REDO"

        return response.format(topic=topic or 'commands', info=info)

    def _handle_file_suggestion(self, user_input, intent_data):
        """Handle file finding requests."""
        query = user_input.replace('find', '').replace('locate', '').replace('where is', '').strip()
        return intent_data.get('RESPONSE_TEMPLATE', '').format(query=query or 'files')

    def _handle_summarize(self, user_input, intent_data, context):
        """Handle summarization requests (offline)."""
        if self.is_online:
            return "For AI summarization, use: ASK \"Summarize this\" FROM \"<panel>\""

        # Offline summary - basic stats
        if context and hasattr(context, 'panels'):
            # Try to find content to summarize
            return intent_data.get('RESPONSE_TEMPLATE', '').format(file='<filename>')

        return "Offline mode: Load content with LOAD, then I can provide basic stats."

    def _handle_command_suggestion(self, user_input, intent_data):
        """Suggest commands based on user intent."""
        keywords = intent_data.get('KEYWORDS', {})

        for phrase, command in keywords.items():
            if phrase in user_input.lower():
                return f"Try this command:\n  {command}"

        return "What would you like to do? Try: CATALOG, LOAD, SAVE, ASK, or HELP"

    def _handle_error_help(self, user_input, intent_data):
        """Help with error messages."""
        common_fixes = intent_data.get('COMMON_FIXES', {})

        # Check for common error keywords
        for error_type, fix in common_fixes.items():
            if error_type in user_input.lower():
                return f"💡 {fix}"

        return "Try: REPAIR to fix common issues, or HELP <command> for specific commands."

    def _handle_analysis(self, user_input, intent_data, context):
        """Perform offline analysis on content."""
        methods = intent_data.get('METHODS', {})

        if not context:
            return "Load content first with: LOAD \"<file>\" TO \"<panel>\""

        # Return available analysis methods
        return "Offline analysis available:\n" + "\n".join([f"  • {desc}" for desc in methods.values()])

    def analyze_content(self, content):
        """Perform basic content analysis (offline)."""
        if not content:
            return "No content to analyze."

        lines = content.split('\n')
        words = content.split()

        analysis = {
            'lines': len(lines),
            'words': len(words),
            'characters': len(content),
            'non_empty_lines': len([l for l in lines if l.strip()])
        }

        # Try to detect structure
        if content.strip().startswith('{'):
            analysis['type'] = 'JSON/UDO structure detected'
            try:
                json.loads(content)
                analysis['valid_json'] = True
            except:
                analysis['valid_json'] = False

        return analysis

    def format_analysis(self, analysis):
        """Format analysis results for display."""
        if isinstance(analysis, str):
            return analysis

        result = "📊 Content Analysis (Offline):\n"
        result += f"  Lines: {analysis.get('lines', 0)}\n"
        result += f"  Words: {analysis.get('words', 0)}\n"
        result += f"  Characters: {analysis.get('characters', 0)}\n"

        if 'type' in analysis:
            result += f"  Type: {analysis['type']}\n"
        if 'valid_json' in analysis:
            status = "✅ Valid" if analysis['valid_json'] else "❌ Invalid"
            result += f"  JSON: {status}\n"

        return result

    def track_command(self, command):
        """Track command for context and chaining suggestions."""
        self.command_history.append(command.upper())
        # Keep only last 10 commands
        if len(self.command_history) > 10:
            self.command_history.pop(0)

    def suggest_next_command(self):
        """Suggest next command based on recent history."""
        if not self.command_history:
            return None

        last_command = self.command_history[-1]

        # Common command chains
        chains = {
            'LOAD': ['SHOW', 'EDIT', 'ASK'],
            'CATALOG': ['LOAD', 'EDIT'],
            'SAVE': ['SHOW', 'EDIT'],
            'GRID PANEL CREATE': ['LOAD', 'SHOW'],
            'ASK': ['SHOW', 'SAVE'],
            'EDIT': ['SHOW', 'SAVE']
        }

        for cmd_prefix, suggestions in chains.items():
            if last_command.startswith(cmd_prefix):
                # Don't suggest if already done
                for suggestion in suggestions:
                    if not any(h.startswith(suggestion) for h in self.command_history[-3:]):
                        return suggestion

        return None


class UserMemoryManager:
    """Manages user memory for context and personalization."""
    
    def __init__(self):
        self.memory_dir = Path("memory/user")
        self.memory_file = self.memory_dir / "context.json"
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing memory
        self.memory = self._load_memory()
    
    def _load_memory(self) -> Dict:
        """Load user memory from disk."""
        if self.memory_file.exists():
            try:
                with open(self.memory_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        return {
            "query_history": [],
            "preferences": {},
            "context": {}
        }
    
    def save_query(self, query: str, response_confidence: float):
        """Save query to history."""
        self.memory["query_history"].append({
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "confidence": response_confidence
        })
        
        # Keep last 100 queries
        if len(self.memory["query_history"]) > 100:
            self.memory["query_history"] = self.memory["query_history"][-100:]
        
        self._save_memory()
    
    def _save_memory(self):
        """Save memory to disk."""
        try:
            with open(self.memory_file, 'w') as f:
                json.dump(self.memory, f, indent=2)
        except:
            pass
    
    def get_context(self) -> Dict:
        """Get current context."""
        return self.memory.get("context", {})

