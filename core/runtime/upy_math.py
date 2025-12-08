"""
uPY Math Expression Parser (v1.2.x)

Parses and evaluates arithmetic expressions with variables.

Supports:
- Basic operators: +, -, *, /, %, ** (power)
- Parentheses for grouping
- Variable substitution: {$var}
- Order of operations (PEMDAS)
- Type coercion (int/float)

Examples:
- "{$x} + 5" → 15 (if x=10)
- "{$hp} * 2" → 200 (if hp=100)
- "({$a} + {$b}) / 2" → 7.5 (if a=10, b=5)
- "{$base} ** 2" → 100 (if base=10)
"""

import re
from typing import Any, Union, Callable, Dict


class MathParser:
    """
    Simple recursive descent parser for arithmetic expressions.

    Grammar (simplified PEMDAS):
    expression := term (('+' | '-') term)*
    term       := factor (('*' | '/' | '%') factor)*
    factor     := power ('**' power)*
    power      := ('+'|'-')? atom
    atom       := number | variable | '(' expression ')'
    """

    def __init__(self):
        self.pos = 0
        self.text = ""
        self.variables = {}

    def parse(self, expression: str, variables: Dict[str, Any] = None) -> Union[int, float]:
        """
        Parse and evaluate arithmetic expression.

        Args:
            expression: Math expression string (may contain {$variables})
            variables: Dictionary of variable values

        Returns:
            Numeric result (int or float)

        Raises:
            ValueError: If expression is invalid
        """
        self.text = expression.strip()
        self.pos = 0
        self.variables = variables or {}

        if not self.text:
            raise ValueError("Empty expression")

        result = self.expression()

        # Check for unparsed content
        if self.pos < len(self.text):
            raise ValueError(f"Unexpected character at position {self.pos}: '{self.text[self.pos]}'")

        return result

    def current_char(self) -> str:
        """Get current character or empty string if at end."""
        if self.pos < len(self.text):
            return self.text[self.pos]
        return ''

    def peek_char(self, offset: int = 1) -> str:
        """Peek ahead at character."""
        pos = self.pos + offset
        if pos < len(self.text):
            return self.text[pos]
        return ''

    def advance(self):
        """Move to next character."""
        self.pos += 1

    def skip_whitespace(self):
        """Skip whitespace characters."""
        while self.current_char().isspace():
            self.advance()

    def expression(self) -> Union[int, float]:
        """Parse expression: term (('+' | '-') term)*"""
        self.skip_whitespace()
        result = self.term()

        while True:
            self.skip_whitespace()
            char = self.current_char()

            if char == '+':
                self.advance()
                result = result + self.term()
            elif char == '-':
                self.advance()
                result = result - self.term()
            else:
                break

        return result

    def term(self) -> Union[int, float]:
        """Parse term: factor (('*' | '/' | '%') factor)*"""
        self.skip_whitespace()
        result = self.factor()

        while True:
            self.skip_whitespace()
            char = self.current_char()

            if char == '*' and self.peek_char() != '*':
                self.advance()
                result = result * self.factor()
            elif char == '/':
                self.advance()
                divisor = self.factor()
                if divisor == 0:
                    raise ValueError("Division by zero")
                result = result / divisor
            elif char == '%':
                self.advance()
                divisor = self.factor()
                if divisor == 0:
                    raise ValueError("Modulo by zero")
                result = result % divisor
            else:
                break

        return result

    def factor(self) -> Union[int, float]:
        """Parse factor: power ('**' power)*"""
        self.skip_whitespace()
        result = self.power()

        while True:
            self.skip_whitespace()

            # Check for ** (exponentiation)
            if self.current_char() == '*' and self.peek_char() == '*':
                self.advance()
                self.advance()
                result = result ** self.power()
            else:
                break

        return result

    def power(self) -> Union[int, float]:
        """Parse power: ('+'|'-')? atom"""
        self.skip_whitespace()

        # Unary plus/minus
        sign = 1
        if self.current_char() in ('+', '-'):
            if self.current_char() == '-':
                sign = -1
            self.advance()

        return sign * self.atom()

    def atom(self) -> Union[int, float]:
        """Parse atom: number | variable | '(' expression ')'"""
        self.skip_whitespace()

        # Parentheses
        if self.current_char() == '(':
            self.advance()
            result = self.expression()
            self.skip_whitespace()
            if self.current_char() != ')':
                raise ValueError(f"Expected ')' at position {self.pos}")
            self.advance()
            return result

        # Variable: {$name}
        if self.current_char() == '{':
            return self.parse_variable()

        # Number
        return self.parse_number()

    def parse_number(self) -> Union[int, float]:
        """Parse numeric literal."""
        self.skip_whitespace()

        start = self.pos
        has_dot = False

        # Optional leading digit before decimal point
        while self.current_char().isdigit():
            self.advance()

        # Decimal point
        if self.current_char() == '.':
            has_dot = True
            self.advance()

            # Digits after decimal point
            while self.current_char().isdigit():
                self.advance()

        number_str = self.text[start:self.pos]

        if not number_str or number_str == '.':
            raise ValueError(f"Expected number at position {self.pos}")

        # Return int or float
        if has_dot:
            return float(number_str)
        else:
            return int(number_str)

    def parse_variable(self) -> Union[int, float]:
        """Parse variable: {$name}"""
        if self.current_char() != '{':
            raise ValueError(f"Expected '{{' at position {self.pos}")

        self.advance()

        if self.current_char() != '$':
            raise ValueError(f"Expected '$' at position {self.pos}")

        self.advance()

        # Read variable name
        start = self.pos
        while self.current_char() and self.current_char() not in '}':
            self.advance()

        var_name = self.text[start:self.pos]

        if not var_name:
            raise ValueError(f"Empty variable name at position {self.pos}")

        if self.current_char() != '}':
            raise ValueError(f"Expected '}}' at position {self.pos}")

        self.advance()

        # Look up variable value
        if var_name not in self.variables:
            raise ValueError(f"Undefined variable: {var_name}")

        value = self.variables[var_name]

        # Convert to number if needed
        if isinstance(value, (int, float)):
            return value
        elif isinstance(value, str):
            try:
                if '.' in value:
                    return float(value)
                else:
                    return int(value)
            except ValueError:
                raise ValueError(f"Variable '{var_name}' is not numeric: {value}")
        else:
            raise ValueError(f"Variable '{var_name}' has invalid type: {type(value)}")


# Convenience function
def evaluate(expression: str, variables: Dict[str, Any] = None) -> Union[int, float]:
    """
    Evaluate arithmetic expression.

    Args:
        expression: Math expression (e.g., "{$x} + 5")
        variables: Variable values dictionary

    Returns:
        Numeric result

    Example:
        >>> evaluate("{$hp} * 2", {"hp": 100})
        200
    """
    parser = MathParser()
    return parser.parse(expression, variables)
