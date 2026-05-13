"""Tests for the CJ Secure policy compiler."""

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from apps.compiler.cli import compile_policy
from apps.compiler.errors import LexError, ParseError, SemanticError
from apps.compiler.lexer import PolicyLexer
from apps.compiler.parser import PolicyParser
from apps.compiler.semantic import PolicySemanticAnalyzer
from apps.services.accessControlSvc import AccessControlService


def parse_source(source: str):
    tokens = PolicyLexer(source).tokenize()
    return PolicyParser(tokens).parse()


def test_lexer_recognizes_keywords_and_identifiers():
    tokens = PolicyLexer("role admin can review_logs;").tokenize()
    assert [token.lexeme for token in tokens[:-1]] == [
        "role",
        "admin",
        "can",
        "review_logs",
        ";",
    ]


def test_parser_builds_role_rule_ast():
    program = parse_source("role admin can review_logs, manage_users;")
    assert len(program.statements) == 1
    statement = program.statements[0]
    assert statement.role_name == "admin"
    assert statement.permissions == ["review_logs", "manage_users"]


def test_semantic_analysis_generates_checked_roles():
    program = parse_source(
        """
        role provider can view_masked_record;
        role patient can view_own_record;
        mask ssn for provider;
        """
    )
    compiled = PolicySemanticAnalyzer().analyze(program)
    assert compiled["roles"]["provider"] == ["view_masked_record"]
    assert compiled["masks"]["provider"] == ["ssn"]


def test_semantic_analysis_rejects_unsafe_patient_permission():
    program = parse_source("role patient can review_logs;")
    with pytest.raises(SemanticError):
        PolicySemanticAnalyzer().analyze(program)


def test_lexer_rejects_invalid_character():
    with pytest.raises(LexError):
        PolicyLexer("role admin can review_logs @;").tokenize()


def test_parser_requires_semicolon():
    tokens = PolicyLexer("role admin can review_logs").tokenize()
    with pytest.raises(ParseError):
        PolicyParser(tokens).parse()


def test_compile_policy_writes_json(tmp_path: Path):
    source_file = tmp_path / "policy.cjsp"
    output_file = tmp_path / "compiled_policy.json"
    source_file.write_text("role admin can review_logs;", encoding="utf-8")

    compile_policy(str(source_file), str(output_file))

    compiled = json.loads(output_file.read_text(encoding="utf-8"))
    assert compiled["roles"] == {"admin": ["review_logs"]}
    assert compiled["metadata"]["language"] == "CJ Secure Policy Language"


def test_access_control_service_uses_compiled_policy(tmp_path: Path):
    policy_file = tmp_path / "compiled_policy.json"
    policy_file.write_text(
        json.dumps({"roles": {"admin": ["review_logs", "manage_users"]}}),
        encoding="utf-8",
    )
    service = AccessControlService(str(policy_file))
    admin = SimpleNamespace(role="admin")

    assert service.is_authorized(admin, "review_logs") is True
    assert service.is_authorized(admin, "view_own_record") is False
