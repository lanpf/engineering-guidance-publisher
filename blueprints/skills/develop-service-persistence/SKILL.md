---
name: develop-service-persistence
description: Use when designing, implementing, migrating, or reviewing repositories, transactions, schemas, constraints, queries, JPA, MyBatis, MyBatis-Plus, persistence mappings, or database-backed concurrency behavior.
---

# Develop Service Persistence

## Workflow

1. Inspect the project guidance, schema or migrations, repository contracts, transaction boundaries, persistence modules, mappings, and affected queries.
2. Read `references/persistence.md` completely before changing persistence behavior.
3. Read `references/persistence-naming.md` when creating or changing shared MyBatis or MyBatis-Plus SQL XML fragments.
4. Keep domain repository contracts technology-neutral and place concrete persistence implementations in dedicated technical modules.
5. Preserve schema, table, field, query, and observable repository semantics when switching between MyBatis-Plus and MyBatis.
6. Design database constraints as the final integrity boundary and explicitly translate expected conflicts at the persistence adapter boundary.
7. Run repository contract tests and real-database integration tests for transactions, constraints, concurrency, and critical query behavior.
