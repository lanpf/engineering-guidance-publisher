---
name: develop-java-code
description: Use when creating, modifying, refactoring, or reviewing Java code, including language and tools, distributed IDs and locks, jobs, persistence, and messaging.
---

# Develop Java Code

## Workflow

1. Inspect the target module, nearby types, and its existing public contracts.
2. Read `references/java-language.md` for every Java implementation or review.
3. Read `references/validation-exceptions.md` when changing inputs, validation, failures, or logging.
4. Read `references/lombok.md` before adding or changing Lombok annotations.
5. Read `references/mapstruct.md` before creating or modifying object conversion.
6. Read `references/distributed-id.md` when generating or assigning distributed identifiers.
7. Read `references/distributed-lock.md` before implementing cross-instance mutual exclusion or concurrent writes.
8. Read `references/distributed-job.md` when creating or changing scheduled, compensation, reconciliation, or batch jobs.
9. Read `references/persistence.md` when changing repositories, transactions, schemas, queries, JPA, or MyBatis-Plus.
10. Read `references/messaging.md` when publishing or consuming events, using outbox, partitioning, dead letters, or delayed messages.
11. Preserve compatibility unless the task explicitly authorizes a breaking change.
12. Compile and run the narrowest relevant tests.

Prefer explicit, readable business logic. Treat every `required` rule as a release-blocking constraint.
