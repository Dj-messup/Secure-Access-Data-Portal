# CSCI450 Compiler Extension: CJ Secure Policy Compiler

## Purpose

This extension turns the CJ Secure Access Portal into a Compiler Structures project by adding a small domain-specific language for role-based access-control policies.

The original application remains the runtime/demo environment. The new compiler is the CSCI450 portion because it includes lexical analysis, parsing, an AST, semantic analysis, and code/config generation.

## Language Name

CJ Secure Policy Language (`.cjsp`)

## Example Source Program

```txt
role provider can view_masked_record;
role patient can view_own_record;
role admin can review_logs, manage_users, view_full_record;

deny patient review_logs;
mask ssn for provider;
mask diagnosis for patient;
```

## BNF Grammar

```txt
<program>          ::= <statement>* EOF
<statement>        ::= <role_rule> | <deny_rule> | <mask_rule>
<role_rule>        ::= "role" <identifier> "can" <permission_list> ";"
<deny_rule>        ::= "deny" <identifier> <identifier> ";"
<mask_rule>        ::= "mask" <identifier> "for" <identifier> ";"
<permission_list>  ::= <identifier> ("," <identifier>)*
<identifier>       ::= <letter> (<letter> | <digit> | "_" | "-")*
```

## Compiler Phases Implemented

1. **Lexer**: `apps/compiler/lexer.py`
   - Converts raw policy text into tokens.
   - Recognizes keywords, identifiers, commas, semicolons, comments, and EOF.

2. **Parser**: `apps/compiler/parser.py`
   - Recursive-descent parser.
   - Builds an AST from the token stream.

3. **AST**: `apps/compiler/ast_nodes.py`
   - Represents `RoleRule`, `DenyRule`, `MaskRule`, and `Program`.

4. **Semantic Analysis**: `apps/compiler/semantic.py`
   - Rejects duplicate roles.
   - Rejects unknown permissions.
   - Rejects masks for undefined roles.
   - Rejects unsafe patient permissions like `review_logs` or `manage_users`.

5. **Code Generation**: `apps/compiler/codegen.py`
   - Generates `data/compiled_policy.json`.
   - The existing `AccessControlService` can load this compiled JSON for RBAC decisions.

6. **CLI Driver**: `apps/compiler/cli.py`
   - Allows compiling a `.cjsp` file from the terminal.

## How to Run the Compiler

```bash
python -m apps.compiler.cli data/policies/cj_hospital_policy.cjsp -o data/compiled_policy.json
```

Expected output:

```txt
Policy compiled successfully: data/compiled_policy.json
```

## How to Run Tests

```bash
pytest tests/test_policy_compiler.py
```

Or run the whole test suite:

```bash
pytest
```

## How This Connects to the Existing Portal

The existing portal already uses role-based access control through `AccessControlService`.

This compiler generates the role-permission configuration instead of hardcoding it. That makes the compiler output part of the application runtime.

If `data/compiled_policy.json` exists, `AccessControlService` loads permissions from that file. If the compiled file is missing or invalid, the service falls back to the original built-in demo permissions.
