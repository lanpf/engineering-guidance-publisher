# 依赖管理最佳实践

本文定义 Maven 依赖、module 边界、版本管理和服务技术装配约束。

## Module 依赖

- 每个 module 只声明当前编译和运行语义必需的最小依赖，不为潜在场景提前引入依赖。
- module 之间禁止循环依赖；必须通过调整职责边界或抽取公共 module 消除循环，不得用反射或事件隐藏编译期循环。
- 服务父 POM 必须在 `<dependencyManagement><dependencies>` 中以 `${project.version}` 管理除测试专用 module 和 boot module 外的全部服务 module；不得将它们声明为父 POM 的直接依赖。
- 只有具体技术实现、运行时适配和最终打包装配 module 可以引入聚合 starter；技术中立的 domain、application 等 module 只依赖最小 framework 契约。

## Scope 与版本

- scope 必须匹配实际用途：编译期必需使用 `compile`，仅测试使用 `test`；只有运行环境确实提供或能力确实可选时才使用 `provided` 或 `optional`。
- SNAPSHOT 依赖不得进入发布分支和生产构建，只允许在本地或未发布迭代分支临时使用。
- 三方依赖版本必须通过统一 dependency management 管理，业务和功能 module 不得单独覆盖版本。

## 服务技术基线

- 服务使用 Spring Boot `3.5.16` 和 Spring Cloud `2025.0.3`；版本随 `framework-dependencies` 升级统一调整，升级发布时同步修订本条。
- 使用 `framework-dependencies`、`framework-starter-dependencies` 统一版本，并按需选择 `framework-*` 契约和 `framework-starter-*` 实现。
- 持久化、消息和调度等可替换技术由 boot 的打包依赖选择运行时实现；不得在同一制品内通过运行时属性切换多套实现。实现 module 的位置和职责遵循[服务分层最佳实践](bp_layered_service.md#模块职责)。

| 框架契约 | 典型实现 starter | 最佳实践文档 |
| --- | --- | --- |
| `framework-core` | — | [Java 最佳实践](bp_java.md#参数校验) |
| `framework-domain` | — | [服务分层最佳实践](bp_layered_service.md#层内约定) |
| `framework-id` | `framework-starter-id-cosid` | [分布式 ID 最佳实践](bp_distributed_id.md#分布式 ID) |
| `framework-lock` | `framework-starter-lock-redis` | [分布式锁最佳实践](bp_distributed_lock.md#分布式锁) |
| `framework-message` | RabbitMQ starter | [分布式消息最佳实践](bp_distributed_messaging.md#事件与发布) |
| `framework-persistence` | JPA、MyBatis、MyBatis-Plus starter | [数据持久化最佳实践](bp_persistence.md#持久化边界) |
