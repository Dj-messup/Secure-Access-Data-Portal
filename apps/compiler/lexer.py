"""Lexer for the CJ Secure policy language.

The lexer performs the first compiler phase. It reads raw source text and
converts it into a token stream for the parser.
"""

from apps.compiler.errors import LexError
from apps.compiler.tokens import Token, TokenType


KEYWORDS: dict[str, TokenType] = {
    "role": TokenType.ROLE,
    "can": TokenType.CAN,
    "deny": TokenType.DENY,
    "mask": TokenType.MASK,
    "for": TokenType.FOR,
}


class PolicyLexer:
    """Convert policy source text into tokens."""

    def __init__(self, source: str) -> None:
        self.source = source
        self.current = 0
        self.line = 1
        self.column = 1

    def tokenize(self) -> list[Token]:
        """Return the full token list ending with EOF."""
        tokens: list[Token] = []

        while not self._at_end():
            ch = self._peek()

            if ch in " \t\r":
                self._advance()
                continue

            if ch == "\n":
                self._advance_line()
                continue

            if ch == "#":
                self._skip_comment()
                continue

            if ch == ",":
                tokens.append(self._single_char_token(TokenType.COMMA))
                continue

            if ch == ";":
                tokens.append(self._single_char_token(TokenType.SEMICOLON))
                continue

            if ch.isalpha() or ch == "_":
                tokens.append(self._identifier())
                continue

            raise LexError(
                f"Unexpected character {ch!r} at line {self.line}, "
                f"column {self.column}."
            )

        tokens.append(Token(TokenType.EOF, "", self.line, self.column))
        return tokens

    def _at_end(self) -> bool:
        return self.current >= len(self.source)

    def _peek(self) -> str:
        return self.source[self.current]

    def _advance(self) -> str:
        ch = self.source[self.current]
        self.current += 1
        self.column += 1
        return ch

    def _advance_line(self) -> None:
        self.current += 1
        self.line += 1
        self.column = 1

    def _skip_comment(self) -> None:
        while not self._at_end() and self._peek() != "\n":
            self._advance()

    def _single_char_token(self, token_type: TokenType) -> Token:
        line = self.line
        column = self.column
        lexeme = self._advance()
        return Token(token_type, lexeme, line, column)

    def _identifier(self) -> Token:
        line = self.line
        column = self.column
        start = self.current

        while not self._at_end() and (
            self._peek().isalnum() or self._peek() in {"_", "-"}
        ):
            self._advance()

        lexeme = self.source[start:self.current].lower()
        token_type = KEYWORDS.get(lexeme, TokenType.IDENTIFIER)
        return Token(token_type, lexeme, line, column)
