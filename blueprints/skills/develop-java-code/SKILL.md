---
name: develop-java-code
description: Use when creating, modifying, refactoring, or reviewing Java code, including language features, validation, exceptions, logging, Lombok, and MapStruct.
---

# Develop Java Code

## Workflow

1. Inspect the target module, nearby types, and its existing public contracts.
2. Read `references/java-language.md` for every Java implementation or review.
3. Read `references/validation-exceptions.md` when changing inputs, validation, failures, or logging.
4. Read `references/lombok.md` before adding or changing Lombok annotations.
5. Read `references/logging.md` when adding or changing log statements, log configuration, or code that may touch sensitive data.
6. Read `references/mapstruct.md` before creating or modifying object conversion.
7. Preserve compatibility unless the task explicitly authorizes a breaking change.
8. Compile and run the narrowest relevant tests.

Prefer explicit, readable business logic. Treat every `required` rule as a release-blocking constraint.
