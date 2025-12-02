"""
Tests for uPY Parser

Tests the new COMMAND(args) syntax with Python alignment.
"""

import pytest
from core.runtime.upy_parser import (
    UPYParser,
    UPYParseError,
    migrate_ucode_to_upy
)


@pytest.fixture
def parser():
    """Fresh parser for each test"""
    return UPYParser()


def test_parse_simple_command(parser):
    """Test parsing simple command with no args"""
    result = parser.parse_command("SYSTEM-STATUS()")

    assert result is not None
    assert result[0] == "SYSTEM-STATUS"
    assert result[1] == []


def test_parse_command_with_string(parser):
    """Test command with string argument"""
    result = parser.parse_command("FILE-SAVE('test.txt')")

    assert result is not None
    assert result[0] == "FILE-SAVE"
    assert result[1] == ['test.txt']


def test_parse_command_with_multiple_args(parser):
    """Test command with multiple arguments"""
    result = parser.parse_command("SPRITE-SET('HP'|100)")

    assert result is not None
    assert result[0] == "SPRITE-SET"
    assert result[1] == ['HP', 100]


def test_parse_command_with_variable(parser):
    """Test command with variable reference"""
    parser.variables['SPRITE-HP-MAX'] = 100
    result = parser.parse_command("SPRITE-SET('HP'|$SPRITE-HP-MAX)")

    assert result is not None
    assert result[0] == "SPRITE-SET"
    assert result[1] == ['HP', 100]


def test_parse_command_with_mixed_args(parser):
    """Test command with mixed argument types"""
    parser.variables['NAME'] = 'Hero'
    result = parser.parse_command("GAME-SETUP($NAME|5.5|TRUE|'test')")

    assert result is not None
    assert result[0] == "GAME-SETUP"
    assert result[1] == ['Hero', 5.5, True, 'test']


def test_parse_conditional_simple(parser):
    """Test simple conditional"""
    result = parser.parse_conditional("{IF $SPRITE-HP < 50: GAME-HEAL(25)}")

    assert result is not None
    assert result['condition'] == '$SPRITE-HP < 50'
    assert result['if_command'] == 'GAME-HEAL(25)'
    assert result['else_command'] is None


def test_parse_conditional_with_else(parser):
    """Test conditional with ELSE"""
    result = parser.parse_conditional(
        "{IF $SPRITE-HP < 50: GAME-HEAL(25) ELSE: SYSTEM-STATUS()}"
    )

    assert result is not None
    assert result['condition'] == '$SPRITE-HP < 50'
    assert result['if_command'] == 'GAME-HEAL(25)'
    assert result['else_command'] == 'SYSTEM-STATUS()'


def test_parse_block(parser):
    """Test block parsing"""
    result = parser.parse_block("[INIT: SPRITE-SET('HP'|100)]")

    assert result is not None
    assert result['label'] == 'INIT'
    assert 'SPRITE-SET' in result['commands']


def test_evaluate_condition_true(parser):
    """Test condition evaluation - true"""
    parser.variables['SPRITE-HP'] = 30

    assert parser.evaluate_condition('$SPRITE-HP < 50')


def test_evaluate_condition_false(parser):
    """Test condition evaluation - false"""
    parser.variables['SPRITE-HP'] = 75

    assert not parser.evaluate_condition('$SPRITE-HP < 50')


def test_parse_line_command(parser):
    """Test parsing command line"""
    result = parser.parse_line("FILE-SAVE('test.txt')")

    assert result['type'] == 'command'
    assert result['command'] == 'FILE-SAVE'
    assert result['args'] == ['test.txt']


def test_parse_line_conditional(parser):
    """Test parsing conditional line"""
    result = parser.parse_line("{IF $HP < 50: HEAL(25)}")

    assert result['type'] == 'conditional'
    assert '$HP < 50' in result['condition']


def test_parse_line_block(parser):
    """Test parsing block line"""
    result = parser.parse_line("[INIT: commands]")

    assert result['type'] == 'block'
    assert result['label'] == 'INIT'


def test_parse_line_comment(parser):
    """Test skipping comments"""
    result = parser.parse_line("# This is a comment")

    assert result is None


def test_parse_line_empty(parser):
    """Test skipping empty lines"""
    result = parser.parse_line("")

    assert result is None


def test_parse_script(parser):
    """Test parsing complete script"""
    script = """
# Test script
SYSTEM-STATUS()
FILE-SAVE('test.txt')
{IF $HP < 50: HEAL(25)}
SPRITE-SET('NAME'|'Hero')
"""

    statements = parser.parse(script)

    assert len(statements) == 4
    assert statements[0]['type'] == 'command'
    assert statements[1]['type'] == 'command'
    assert statements[2]['type'] == 'conditional'
    assert statements[3]['type'] == 'command'


def test_to_python_simple(parser):
    """Test converting uPY to Python"""
    script = """
SYSTEM-STATUS()
FILE-SAVE('test.txt')
"""

    python = parser.to_python(script)

    assert 'def main():' in python
    assert 'registry.execute' in python
    assert 'SYSTEM-STATUS' in python
    assert 'FILE-SAVE' in python


def test_migrate_ucode_simple():
    """Test migrating old uCODE to new uPY"""
    old = "[SYSTEM|STATUS]"
    new = migrate_ucode_to_upy(old)

    assert new == "SYSTEM-STATUS()"


def test_migrate_ucode_with_args():
    """Test migrating uCODE with arguments"""
    old = "[FILE|SAVE*test.txt]"
    new = migrate_ucode_to_upy(old)

    assert new == "FILE-SAVE('test.txt')"


def test_migrate_ucode_multiple_args():
    """Test migrating uCODE with multiple arguments"""
    old = "[SPRITE|SET*HP*100]"
    new = migrate_ucode_to_upy(old)

    assert new == "SPRITE-SET('HP'|100)"


def test_migrate_ucode_with_variable():
    """Test migrating uCODE with variable"""
    old = "[SPRITE|GET*$HP]"
    new = migrate_ucode_to_upy(old)

    assert new == "SPRITE-GET($HP)"  # Variables don't get quoted


def test_parse_command_double_quotes(parser):
    """Test command with double quotes"""
    result = parser.parse_command('FILE-SAVE("test.txt")')

    assert result is not None
    assert result[1] == ['test.txt']


def test_parse_command_nested_hyphen(parser):
    """Test command with multiple hyphens"""
    result = parser.parse_command("KNOWLEDGE-SEARCH-ADVANCED('water')")

    assert result is not None
    assert result[0] == "KNOWLEDGE-SEARCH-ADVANCED"


def test_parse_args_float(parser):
    """Test parsing float arguments"""
    args = parser.parse_args("3.14|2.5")

    assert args == [3.14, 2.5]


def test_parse_args_negative_number(parser):
    """Test parsing negative numbers"""
    args = parser.parse_args("-10|5")

    assert args == [-10, 5]


def test_parse_args_boolean(parser):
    """Test parsing boolean values"""
    args = parser.parse_args("TRUE|FALSE")

    assert args == [True, False]


def test_conditional_complex_condition(parser):
    """Test complex conditional expression"""
    parser.variables['SPRITE-HP'] = 50
    parser.variables['SPRITE-HP-MAX'] = 100

    # Simple numeric comparisons work
    assert parser.evaluate_condition('$SPRITE-HP < 100')
    assert parser.evaluate_condition('$SPRITE-HP-MAX > 50')


def test_invalid_command_format(parser):
    """Test invalid command format returns None"""
    result = parser.parse_command("INVALID COMMAND")

    assert result is None


def test_parse_multiline_block(parser):
    """Test parsing multiline block syntax"""
    block_text = """[INIT:
        SPRITE-SET('HP'|100)
        SPRITE-SET('NAME'|'Hero')
    ]"""

    result = parser.parse_block(block_text)

    assert result is not None
    assert result['label'] == 'INIT'
    assert 'SPRITE-SET' in result['commands']
