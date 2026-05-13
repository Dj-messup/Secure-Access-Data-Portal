"""Role-based access control service."""

import json
from pathlib import Path


class AccessControlService:
    """Service responsible for enforcing role-based access control.

    If data/compiled_policy.json exists, this service loads permissions from the
    policy compiler output. Otherwise, it falls back to the built-in demo roles.
    """

    DEFAULT_PERMISSIONS: dict[str, set[str]] = {
        "provider": {"view_masked_record"},
        "patient": {"view_own_record"},
        "admin": {"review_logs"},
    }

    def __init__(self, policy_path: str = "data/compiled_policy.json") -> None:
        self.policy_path = Path(policy_path)
        self.role_permissions = self._load_role_permissions()

    def _load_role_permissions(self) -> dict[str, set[str]]:
        if not self.policy_path.exists():
            return self.DEFAULT_PERMISSIONS.copy()

        try:
            data = json.loads(self.policy_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return self.DEFAULT_PERMISSIONS.copy()

        raw_roles = data.get("roles", {})
        if not isinstance(raw_roles, dict):
            return self.DEFAULT_PERMISSIONS.copy()

        compiled_permissions: dict[str, set[str]] = {}
        for role_name, permissions in raw_roles.items():
            if isinstance(role_name, str) and isinstance(permissions, list):
                compiled_permissions[role_name] = {
                    str(permission) for permission in permissions
                }

        return compiled_permissions or self.DEFAULT_PERMISSIONS.copy()

    def is_authorized(self, user, action: str) -> bool:
        """Return True if the user's role is allowed to perform the action."""
        allowed_actions = self.role_permissions.get(user.role, set())
        return action in allowed_actions
