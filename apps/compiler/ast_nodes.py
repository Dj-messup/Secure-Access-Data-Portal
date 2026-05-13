"""Abstract syntax tree node definitions for the policy compiler."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class RoleRule:
    """A rule granting permissions to one role."""

    role_name: str
    permissions: list[str]


@dataclass(frozen=True)
class DenyRule:
    """A rule explicitly denying one permission from one role."""

    role_name: str
    permission: str


@dataclass(frozen=True)
class MaskRule:
    """A rule saying one sensitive field must be masked for one role."""

    field_name: str
    role_name: str


Statement = RoleRule | DenyRule | MaskRule


@dataclass(frozen=True)
class Program:
    """Root AST node for an entire policy source file."""

    statements: list[Statement] = field(default_factory=list)
