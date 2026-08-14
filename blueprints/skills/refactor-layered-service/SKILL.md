---
name: refactor-layered-service
description: Plan and apply coordinated standards-driven refactors across layered service architecture, Java code, dependencies, distributed capabilities, compensation workflows, persistence, error codes, and tests.
---

# Refactor Layered Service

## Workflow

1. Read the project's `AGENTS.md`, root `README.md`, and every authoritative document routed for the affected area.
2. Inspect Git status and record unrelated pre-existing changes before editing.
3. Use `$develop-java-code` for Java language, validation, exceptions, logging, Lombok, and MapStruct changes.
4. Use `$develop-layered-service` for module boundaries, API, domain, application, infrastructure, interfaces, clients, boot, data carriers, and naming.
5. Use `$manage-maven-dependencies` for Maven dependencies, module relationships, versions, scopes, BOMs, starters, or runtime implementations.
6. Use `$develop-distributed-capabilities` for distributed identifiers, locking, event publication, and message consumption.
7. Use `$develop-compensation-workflows` for compensation, reconciliation, repair, cleanup, batch recovery, or fallback flows.
8. Use `$develop-service-persistence` for repositories, transactions, schemas, mappings, constraints, and queries.
9. Use `$manage-service-error-codes` for error definitions, ranges, names, or documentation.
10. Use `$test-service` for test updates, test design, and verification.
11. Produce a plan before modifying code. For every item, identify the triggering rule or requested objective, impacted modules/files, compatibility considerations, implementation approach, and verification commands.
12. After explicit user confirmation, apply only the approved plan, preserve unrelated changes, run the planned verification, and report results. Commit only when separately authorized or when an invoking workflow explicitly authorizes it.
