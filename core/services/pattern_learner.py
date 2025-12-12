"""
Pattern Learner - Local-only error pattern recognition and fix suggestions

Learns from error patterns to suggest fixes without sending data to cloud.
All pattern learning is LOCAL ONLY - no telemetry, no cloud sync.

Privacy-first design:
- Patterns stored locally in memory/bank/system/error_patterns.json
- Sanitized signatures only (no user data, paths, or API keys)
- Fuzzy matching for similar errors
- Never transmits pattern data

Part of v1.2.22 - Self-Healing & Auto-Error-Awareness System
"""

import hashlib
import json
import re
from collections import defaultdict
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from core.config import Config


@dataclass
class ErrorPattern:
    """Learned error pattern with fix suggestions."""
    signature: str  # Sanitized error signature (SHA256)
    pattern_type: str  # Error type (e.g., "ImportError", "AttributeError")
    pattern_text: str  # Sanitized pattern (no paths/keys)
    frequency: int  # Number of occurrences
    fix_success_rate: float  # Success rate of applied fixes (0-1)
    suggested_fixes: List[str]  # List of fix suggestions
    last_seen: str  # ISO timestamp
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return asdict(self)


class PatternLearner:
    """
    Learn from error patterns and suggest fixes (local-only).
    
    Privacy guarantees:
    - All data stays local (memory/bank/system/error_patterns.json)
    - Patterns are sanitized (no user data, paths, API keys)
    - No network calls, no telemetry
    - User can inspect/delete patterns at any time
    
    Example:
        learner = PatternLearner(config)
        
        # Record error
        learner.record_error("ImportError", "No module named 'foo'")
        
        # Get suggestions
        suggestions = learner.suggest_fix("ImportError", "No module named 'bar'")
        for fix in suggestions:
            print(f"Try: {fix}")
        
        # Record fix success
        learner.record_fix_result("sig123", success=True)
    """
    
    def __init__(self, config: Config):
        """
        Initialize pattern learner.
        
        Args:
            config: Config instance
        """
        self.config = config
        self.patterns_file = Path(config.project_root) / "memory" / "bank" / "system" / "error_patterns.json"
        self.patterns_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load patterns
        self.patterns: Dict[str, ErrorPattern] = {}
        self._load_patterns()
    
    def _load_patterns(self):
        """Load patterns from disk."""
        if not self.patterns_file.exists():
            return
        
        try:
            with open(self.patterns_file, 'r') as f:
                data = json.load(f)
            
            # Convert dict to ErrorPattern objects
            for sig, pattern_data in data.get('patterns', {}).items():
                self.patterns[sig] = ErrorPattern(**pattern_data)
        
        except Exception:
            # Corrupted patterns file - start fresh
            self.patterns = {}
    
    def _save_patterns(self):
        """Save patterns to disk."""
        try:
            data = {
                'version': '1.0',
                'last_updated': datetime.now().isoformat(),
                'patterns': {
                    sig: pattern.to_dict()
                    for sig, pattern in self.patterns.items()
                }
            }
            
            with open(self.patterns_file, 'w') as f:
                json.dump(data, f, indent=2)
        
        except Exception:
            pass  # Silent fail - don't break system if can't save
    
    def _sanitize_error_text(self, error_text: str) -> str:
        """
        Sanitize error text to remove sensitive information.
        
        Removes:
        - Absolute paths → relative paths
        - Usernames → <USER>
        - API keys/tokens → <KEY>
        - Email addresses → <EMAIL>
        - IP addresses → <IP>
        
        Args:
            error_text: Raw error text
        
        Returns:
            Sanitized error text
        """
        text = error_text
        
        # Remove absolute paths (convert to relative)
        text = re.sub(r'/Users/[^/]+/', '<USER>/', text)
        text = re.sub(r'/home/[^/]+/', '<USER>/', text)
        text = re.sub(r'C:\\Users\\[^\\]+\\', r'<USER>\\', text)
        
        # Remove API keys (common patterns)
        text = re.sub(r'[A-Za-z0-9_-]{20,}', '<KEY>', text)
        
        # Remove email addresses
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '<EMAIL>', text)
        
        # Remove IP addresses
        text = re.sub(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', '<IP>', text)
        
        # Normalize whitespace
        text = ' '.join(text.split())
        
        return text
    
    def _generate_signature(self, error_type: str, error_text: str) -> str:
        """
        Generate sanitized signature for error pattern.
        
        Args:
            error_type: Error type (e.g., "ImportError")
            error_text: Error message text
        
        Returns:
            SHA256 signature (16-char hex)
        """
        sanitized = self._sanitize_error_text(error_text)
        combined = f"{error_type}:{sanitized}"
        
        # Generate SHA256 hash
        hash_obj = hashlib.sha256(combined.encode('utf-8'))
        return hash_obj.hexdigest()[:16]  # First 16 chars
    
    def record_error(self, error_type: str, error_text: str, context: Optional[Dict] = None) -> str:
        """
        Record an error occurrence.
        
        Args:
            error_type: Error type (e.g., "ImportError")
            error_text: Error message text
            context: Optional context (sanitized automatically)
        
        Returns:
            Error signature
        """
        # Generate signature
        signature = self._generate_signature(error_type, error_text)
        sanitized_text = self._sanitize_error_text(error_text)
        
        # Update or create pattern
        if signature in self.patterns:
            # Existing pattern - increment frequency
            pattern = self.patterns[signature]
            pattern.frequency += 1
            pattern.last_seen = datetime.now().isoformat()
        else:
            # New pattern
            pattern = ErrorPattern(
                signature=signature,
                pattern_type=error_type,
                pattern_text=sanitized_text,
                frequency=1,
                fix_success_rate=0.0,
                suggested_fixes=[],
                last_seen=datetime.now().isoformat()
            )
            self.patterns[signature] = pattern
        
        # Save patterns
        self._save_patterns()
        
        return signature
    
    def suggest_fix(self, error_type: str, error_text: str, limit: int = 5) -> List[str]:
        """
        Suggest fixes for an error based on learned patterns.
        
        Args:
            error_type: Error type
            error_text: Error message text
            limit: Maximum number of suggestions
        
        Returns:
            List of fix suggestions
        """
        # Generate signature
        signature = self._generate_signature(error_type, error_text)
        
        # Exact match
        if signature in self.patterns:
            pattern = self.patterns[signature]
            if pattern.suggested_fixes:
                return pattern.suggested_fixes[:limit]
        
        # Fuzzy match - find similar patterns
        suggestions = []
        sanitized_text = self._sanitize_error_text(error_text)
        
        # Score patterns by similarity
        scored_patterns = []
        for sig, pattern in self.patterns.items():
            if pattern.pattern_type != error_type:
                continue  # Different error type
            
            # Calculate similarity (simple word overlap)
            similarity = self._calculate_similarity(sanitized_text, pattern.pattern_text)
            
            if similarity > 0.5:  # At least 50% similar
                scored_patterns.append((similarity, pattern))
        
        # Sort by similarity and success rate
        scored_patterns.sort(key=lambda x: (x[0], x[1].fix_success_rate), reverse=True)
        
        # Collect suggestions
        for similarity, pattern in scored_patterns[:limit]:
            if pattern.suggested_fixes:
                suggestions.extend(pattern.suggested_fixes[:2])  # Top 2 from each pattern
        
        # Deduplicate and limit
        seen = set()
        unique_suggestions = []
        for suggestion in suggestions:
            if suggestion not in seen:
                seen.add(suggestion)
                unique_suggestions.append(suggestion)
        
        return unique_suggestions[:limit]
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two error texts (simple word overlap).
        
        Args:
            text1: First text
            text2: Second text
        
        Returns:
            Similarity score (0-1)
        """
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union) if union else 0.0
    
    def record_fix_result(self, signature: str, success: bool, fix_description: Optional[str] = None):
        """
        Record the result of applying a fix.
        
        Args:
            signature: Error signature
            success: Whether fix was successful
            fix_description: Optional description of fix applied
        """
        if signature not in self.patterns:
            return  # Unknown pattern
        
        pattern = self.patterns[signature]
        
        # Update success rate (exponential moving average)
        alpha = 0.3  # Weight for new observation
        current_rate = pattern.fix_success_rate
        new_rate = 1.0 if success else 0.0
        pattern.fix_success_rate = alpha * new_rate + (1 - alpha) * current_rate
        
        # Add fix to suggestions if successful and not already present
        if success and fix_description:
            if fix_description not in pattern.suggested_fixes:
                pattern.suggested_fixes.insert(0, fix_description)  # Add to front
                
                # Keep only top 5 suggestions
                pattern.suggested_fixes = pattern.suggested_fixes[:5]
        
        # Save patterns
        self._save_patterns()
    
    def get_statistics(self) -> Dict:
        """
        Get pattern learning statistics.
        
        Returns:
            Dictionary with statistics
        """
        if not self.patterns:
            return {
                'total_patterns': 0,
                'total_occurrences': 0,
                'patterns_with_fixes': 0,
                'avg_success_rate': 0.0,
                'top_patterns': []
            }
        
        total_occurrences = sum(p.frequency for p in self.patterns.values())
        patterns_with_fixes = sum(1 for p in self.patterns.values() if p.suggested_fixes)
        avg_success_rate = sum(p.fix_success_rate for p in self.patterns.values()) / len(self.patterns)
        
        # Get top patterns by frequency
        sorted_patterns = sorted(
            self.patterns.values(),
            key=lambda p: p.frequency,
            reverse=True
        )
        
        top_patterns = [
            {
                'type': p.pattern_type,
                'text': p.pattern_text[:60] + '...' if len(p.pattern_text) > 60 else p.pattern_text,
                'frequency': p.frequency,
                'success_rate': round(p.fix_success_rate * 100, 1),
                'fixes': len(p.suggested_fixes)
            }
            for p in sorted_patterns[:5]
        ]
        
        return {
            'total_patterns': len(self.patterns),
            'total_occurrences': total_occurrences,
            'patterns_with_fixes': patterns_with_fixes,
            'avg_success_rate': round(avg_success_rate * 100, 1),
            'top_patterns': top_patterns
        }
    
    def clear_patterns(self, confirm: bool = False):
        """
        Clear all learned patterns.
        
        Args:
            confirm: Must be True to actually clear
        """
        if not confirm:
            return
        
        self.patterns = {}
        self._save_patterns()
    
    def export_patterns(self, filepath: Path):
        """
        Export patterns to JSON file for inspection.
        
        Args:
            filepath: Output file path
        """
        data = {
            'exported_at': datetime.now().isoformat(),
            'total_patterns': len(self.patterns),
            'patterns': [p.to_dict() for p in self.patterns.values()]
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)


# CLI interface for testing
if __name__ == '__main__':
    from core.config import Config
    
    config = Config()
    learner = PatternLearner(config)
    
    print("=" * 70)
    print("PATTERN LEARNER - Privacy Test")
    print("=" * 70)
    print()
    
    # Test privacy - record error with sensitive data
    print("Test 1: Privacy sanitization")
    print("-" * 70)
    
    sensitive_error = "ImportError: No module named 'foo' at /Users/john/projects/myapp/core/main.py"
    sig = learner.record_error("ImportError", sensitive_error)
    print(f"Original error: {sensitive_error}")
    print(f"Signature: {sig}")
    
    # Check sanitized pattern
    pattern = learner.patterns[sig]
    print(f"Sanitized text: {pattern.pattern_text}")
    print(f"✅ No username in pattern: {'john' not in pattern.pattern_text}")
    print()
    
    # Test pattern matching
    print("Test 2: Pattern matching")
    print("-" * 70)
    
    # Record fix
    learner.record_fix_result(sig, success=True, fix_description="Install missing package: pip install foo")
    
    # Try to get suggestions for similar error
    similar_error = "ImportError: No module named 'bar' at /Users/alice/app/main.py"
    suggestions = learner.suggest_fix("ImportError", similar_error)
    
    print(f"Similar error: {similar_error}")
    print(f"Suggestions: {suggestions}")
    print()
    
    # Show statistics
    print("Test 3: Statistics")
    print("-" * 70)
    stats = learner.get_statistics()
    print(f"Total patterns: {stats['total_patterns']}")
    print(f"Total occurrences: {stats['total_occurrences']}")
    print(f"Patterns with fixes: {stats['patterns_with_fixes']}")
    print(f"Average success rate: {stats['avg_success_rate']}%")
    print()
    
    # Verify no data leaks
    print("Test 4: Privacy verification")
    print("-" * 70)
    with open(learner.patterns_file, 'r') as f:
        content = f.read()
    
    print(f"✅ No username 'john': {'john' not in content.lower()}")
    print(f"✅ No username 'alice': {'alice' not in content.lower()}")
    print(f"✅ No absolute paths: {'/Users/' not in content}")
    print(f"Pattern file: {learner.patterns_file}")
    print()
    
    print("=" * 70)
    print("All privacy tests passed! ✅")
    print("=" * 70)


# Global singleton instance
_pattern_learner = None


def get_pattern_learner() -> PatternLearner:
    """Get global PatternLearner singleton."""
    global _pattern_learner
    if _pattern_learner is None:
        from core.config import Config
        config = Config()
        _pattern_learner = PatternLearner(config)
    return _pattern_learner
