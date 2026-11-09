# 依赖管理最佳实践

本文定义 Maven 依赖、module 边界、版本管理和服务技术装配约束。

## Module 依赖

- **强制 · 基础**：每个 module 只声明当前编译和运行语义必需的最小依赖，不为潜在场景提前引入依赖。
- **强制 · 基础**：module 之间禁止循环依赖；必须通过调整职责边界或抽取公共 module 消除循环，不得用反射或事件隐藏编译期循环。
- **强制 · 基础**：服务父 POM 必须在 `<dependencyManagement><dependencies>` 中以 `${project.version}` 管理除测试专用 module 和 boot module 外的全部服务 module；不得将它们声明为父 POM 的直接依赖。
- **强制 · 基础**：只有具体技术实现、运行时适配和最终打包装配 module 可以引入聚合 starter；技术中立的 domain、application 等 module 只依赖最小 framework 契约。
- **强制 · 基础**：`framework-kernel` 的生产代码只依赖 JDK，不反向依赖 `framework-core`、其它 framework module、Spring 或 starter。
- **强制 · 基础**：`framework-core` 和其它 module 按实际用途依赖 `framework-kernel`；只需要错误码、异常或 `Require` 时直接依赖 kernel，不为此引入 core 或 starter。

## Scope 与版本

- **强制 · 基础**：引入新依赖前必须评估维护活跃度、安全性、许可证和依赖成本。
- **默认 · 基础**：使用 framework 的工程优先将统一管理的 commons-lang3 作为通用基础工具依赖；实际使用其 API 的 module 按交付契约选择 scope 并直接声明，dependency management 只管理版本，不代表已经引入依赖。JDK 或已有优先框架工具足以满足需要的 module 无需声明，不要求每个 module 无条件依赖。
- **强制 · 基础**：已有依赖能满足需求时，不得引入功能重叠的库。 按实际使用的能力判断重叠：仅因哈希算法引入的 Guava 不替代统一的 Commons Lang 基础工具。
- **强制 · 基础**：scope 必须匹配实际用途：编译期必需使用 `compile`，仅测试使用 `test`；只有运行环境确实提供时才使用 `provided`。
- **强制 · 基础**：只有能力确实可选时才声明依赖为 `optional`；不得将其作为 scope 选择的替代。
- **强制 · 基础**：SNAPSHOT 依赖不得进入发布分支和生产构建，只允许在本地或未发布迭代分支临时使用。
- **强制 · 基础**：三方依赖版本必须通过统一 dependency management 管理，业务和功能 module 不得单独覆盖版本。

## 服务技术基线

- **强制 · 基础**：服务技术版本必须采用下表中的统一组合。

| Spring Boot | Spring Cloud |
| --- | --- |
| `3.5.16` | `2025.0.3` |

- **强制 · 基础**：服务技术版本随 `framework-dependencies` 升级统一调整，升级发布时必须同步修订版本组合。
- **强制 · 基础**：使用 `framework-dependencies`、`framework-starter-dependencies` 统一版本，并按需选择 `framework-*` 契约和 `framework-starter-*` 实现。
- **强制 · 基础**：持久化、消息和调度等可替换技术由 boot 的打包依赖选择运行时实现；不得在同一制品内通过运行时属性切换多套实现。实现 module 的位置和职责遵循[服务分层最佳实践](bp_layered_service.md#模块职责)。

| 框架契约 | 典型实现 starter | 最佳实践文档 |
| --- | --- | --- |
| `framework-kernel` | — | [显式检查](bp_validation.md#显式检查)、[错误码](bp_error_codes.md#错误码) |
| `framework-core` | — | [请求与响应契约](bp_layered_service.md#api)、[集合处理](bp_validation.md#显式检查) |
| `framework-domain` | — | [服务分层最佳实践](bp_layered_service.md#层内约定) |
| `framework-id` | `framework-starter-id-cosid` | [分布式 ID 最佳实践](bp_ids.md#分布式 ID) |
| `framework-lock` | `framework-starter-lock-redis` | [分布式锁最佳实践](bp_lock.md#分布式锁) |
| `framework-message` | `framework-starter-message-rabbitmq` | [分布式消息最佳实践](bp_messaging.md#事件与发布) |
| `framework-persistence` | JPA、MyBatis、MyBatis-Plus starter | [数据持久化最佳实践](bp_persistence.md#持久化边界) |
