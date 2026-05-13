"""Token definitions for the CJ Secure policy language."""

from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    """All token categories recognized by the policy lexer."""

    ROLE = auto()
    CAN = auto()
    DENY = auto()
    MASK = auto()
    FOR = auto()
    IDENTIFIER = auto()
    COMMA = auto()
    SEMICOLON = auto()
    EOF = auto()


@dataclass(frozen=True)
class Token:
    """One lexical token from the source policy file."""

    token_type: TokenType
    lexeme: str
    line: int
    column: int
