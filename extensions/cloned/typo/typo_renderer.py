"""
Typo Extension Mock - Beautiful Typography Rendering
====================================================

Date: 20251213-172500UTC
Purpose: Mock implementation for testing Typo integration

Real Typo Extension:
- Install from: extensions/cloned/typo/
- Full Unicode typography support
- Multiple style presets

This mock provides basic transformations for testing:
- Commands → Bold Unicode
- Variables → Italic Unicode  
- Functions → Monospace Unicode
- Tags → Star symbols
"""

class TypoRenderer:
    """Mock Typo renderer for testing"""
    
    # Unicode character maps
    BOLD = {
        'A': '𝗔', 'B': '𝗕', 'C': '𝗖', 'D': '𝗗', 'E': '𝗘', 'F': '𝗙', 'G': '𝗚',
        'H': '𝗛', 'I': '𝗜', 'J': '𝗝', 'K': '𝗞', 'L': '𝗟', 'M': '𝗠', 'N': '𝗡',
        'O': '𝗢', 'P': '𝗣', 'Q': '𝗤', 'R': '𝗥', 'S': '𝗦', 'T': '𝗧', 'U': '𝗨',
        'V': '𝗩', 'W': '𝗪', 'X': '𝗫', 'Y': '𝗬', 'Z': '𝗭',
    }
    
    ITALIC = {
        'a': '𝘢', 'b': '𝘣', 'c': '𝘤', 'd': '𝘥', 'e': '𝘦', 'f': '𝘧', 'g': '𝘨',
        'h': '𝘩', 'i': '𝘪', 'j': '𝘫', 'k': '𝘬', 'l': '𝘭', 'm': '𝘮', 'n': '𝘯',
        'o': '𝘰', 'p': '𝘱', 'q': '𝘲', 'r': '𝘳', 's': '𝘴', 't': '𝘵', 'u': '𝘶',
        'v': '𝘷', 'w': '𝘸', 'x': '𝘹', 'y': '𝘺', 'z': '𝘻',
    }
    
    MONO = {
        'a': '𝚊', 'b': '𝚋', 'c': '𝚌', 'd': '𝚍', 'e': '𝚎', 'f': '𝚏', 'g': '𝚐',
        'h': '𝚑', 'i': '𝚒', 'j': '𝚓', 'k': '𝚔', 'l': '𝚕', 'm': '𝚖', 'n': '𝚗',
        'o': '𝚘', 'p': '𝚙', 'q': '𝚚', 'r': '𝚛', 's': '𝚜', 't': '𝚝', 'u': '𝚞',
        'v': '𝚟', 'w': '𝚠', 'x': '𝚡', 'y': '𝚢', 'z': '𝚣',
    }
    
    def render(self, text: str, style: str = 'ucode') -> str:
        """Render text with beautiful typography
        
        Args:
            text: Input text (uCODE syntax)
            style: Rendering style ('ucode' for uCODE scripts)
        
        Returns:
            Typography-enhanced text
        """
        if style != 'ucode':
            return text
        
        result = text
        
        # Commands (UPPERCASE) → Bold
        import re
        def bold_command(match):
            word = match.group(0)
            return ''.join(self.BOLD.get(c, c) for c in word)
        result = re.sub(r'\b[A-Z][A-Z-]+\b', bold_command, result)
        
        # Variables ($prefix) → Italic
        def italic_var(match):
            var = match.group(1)
            return '$' + ''.join(self.ITALIC.get(c, c) for c in var.replace('-', ''))
        result = re.sub(r'\$([a-z-]+)', italic_var, result)
        
        # Functions (@prefix) → Monospace
        def mono_func(match):
            func = match.group(1)
            return '@' + ''.join(self.MONO.get(c, c) for c in func.replace('-', ''))
        result = re.sub(r'@([a-z-]+)', mono_func, result)
        
        # Tags (*) → Star symbol
        result = result.replace('*', '⭐')
        
        return result
    
    def parse(self, text: str, source_style: str = 'ucode') -> str:
        """Parse typography back to plain text
        
        Args:
            text: Typography-enhanced text
            source_style: Original style ('ucode')
        
        Returns:
            Plain uCODE text
        """
        if source_style != 'ucode':
            return text
        
        # Reverse mappings
        reverse_bold = {v: k for k, v in self.BOLD.items()}
        reverse_italic = {v: k for k, v in self.ITALIC.items()}
        reverse_mono = {v: k for k, v in self.MONO.items()}
        
        result = text
        
        # Reverse transformations
        for typo_char, plain_char in reverse_bold.items():
            result = result.replace(typo_char, plain_char)
        
        for typo_char, plain_char in reverse_italic.items():
            result = result.replace(typo_char, plain_char)
        
        for typo_char, plain_char in reverse_mono.items():
            result = result.replace(typo_char, plain_char)
        
        # Star back to asterisk
        result = result.replace('⭐', '*')
        
        return result

if __name__ == '__main__':
    print("Typo Extension Mock - Test")
    print("=" * 60)
    
    renderer = TypoRenderer()
    
    test_cases = [
        "PRINT['Hello World']",
        "CLONE*DEV",
        "@heal-sprite[20]",
        "$player-hp = 100",
    ]
    
    for ucode in test_cases:
        typo = renderer.render(ucode, style='ucode')
        back = renderer.parse(typo, source_style='ucode')
        print(f"Original: {ucode}")
        print(f"Typo:     {typo}")
        print(f"Back:     {back}")
        print(f"Match:    {'✅' if back == ucode else '❌'}")
        print()
