"""Command-line entry point for the CJ Secure policy compiler."""

import argparse
from pathlib import Path

from apps.compiler.codegen import PolicyCodeGenerator
from apps.compiler.errors import PolicyCompilerError
from apps.compiler.lexer import PolicyLexer
from apps.compiler.parser import PolicyParser


DEFAULT_OUTPUT = "data/compiled_policy.json"


def compile_policy(source_path: str, output_path: str = DEFAULT_OUTPUT) -> None:
    """Compile a policy source file into JSON configuration."""
    source = Path(source_path).read_text(encoding="utf-8")
    tokens = PolicyLexer(source).tokenize()
    program = PolicyParser(tokens).parse()
    PolicyCodeGenerator().write_json(program, output_path, source_path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Compile CJ Secure policy files.")
    parser.add_argument("source", help="Path to .cjsp policy source file")
    parser.add_argument(
        "-o",
        "--output",
        default=DEFAULT_OUTPUT,
        help=f"Compiled JSON output path. Default: {DEFAULT_OUTPUT}",
    )
    args = parser.parse_args()

    try:
        compile_policy(args.source, args.output)
    except (OSError, PolicyCompilerError) as exc:
        print(f"Policy compile failed: {exc}")
        return 1

    print(f"Policy compiled successfully: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
