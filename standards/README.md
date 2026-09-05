# Standards 索引

本目录存放人工维护的最佳实践政策源文档（`bp_*.md`）。结构化发布表示见仓库根目录 `catalog.json`，它定义版本、持久规则 ID、Skill 路由和生成的详细规则文本；本 README 只做索引与约定，不复制具体规则。

## 约定

- 所有 `bp_*.md` 的约束默认适用于全部服务工程；项目规约可以补充或收紧，但不得放宽或覆盖。
- 规则编号、标题和规则语义在发布后保持稳定；发布后不得重用规则 ID 表达不同语义，标题是 `catalog.json` 引用身份的一部分，不得随手改名。
- `## 验证` 章节只写在具有可运行验证行为的主题文档中；语言、命名等静态约束由代码评审与静态检查保障。

每条规则同时声明约束级别和适用优先级：

- **强制（`required`）**：不可豁免，违反时阻断交付。
- **默认（`default`）**：默认必须采用；仅在存在具体、可说明的场景理由时允许偏离，并在交付结果中记录理由。
- **建议（`advisory`）**：用于改善实现质量，可按实际收益采用，不因未采用而单独阻断交付。
- **基础（`baseline`）**：与具体架构或业务主题无关，开发和重构时必须预先加载，并在完成前统一复查。
- **主题（`topic`）**：仅在任务涉及对应技术、架构或业务主题时加载和检查。

`bp_*.md` 使用“**强制/默认/建议 · 基础/主题**”标记规则；`catalog.json` 使用 `enforcement` 和 `priority` 字段提供机器可校验的发布表示。分类是规则语义的一部分，调整分类也必须按规则变更发布。

## 文档索引

| 文档 | 范围 |
| --- | --- |
| [bp_java.md](bp_java.md) | Java 语言、数据设计、常量与字面量 |
| [bp_validation.md](bp_validation.md) | Bean Validation、显式前置条件、业务守卫与异常体系 |
| [bp_common_tools.md](bp_common_tools.md) | 基础工具类、Lombok、MapStruct |
| [bp_naming.md](bp_naming.md) | 接口、实现、数据载体、技术适配与 MyBatis XML 命名 |
| [bp_resource_naming.md](bp_resource_naming.md) | 资源键、命名空间、Resolver 职责与单次注入边界 |
| [bp_layered_service.md](bp_layered_service.md) | 规约体系、module 分层、依赖方向、项目级配置、层内约定、不可变数据载体 |
| [bp_service_calls.md](bp_service_calls.md) | 内部 API 契约复用、内部调用降级契约与外部服务防腐边界 |
| [bp_docs.md](bp_docs.md) | 必备项目文档集合、README/RESPONSIBILITIES/DOMAIN 边界、跨服务契约书写规则 |
| [bp_dependencies.md](bp_dependencies.md) | Maven 依赖、module 边界、版本管理、服务技术基线 |
| [bp_persistence.md](bp_persistence.md) | 持久化边界、数据模型、并发写与事务、唯一约束异常、查询与性能 |
| [bp_logging.md](bp_logging.md) | 日志级别、日志内容、链路上下文、敏感数据定义与脱敏 |
| [bp_error_codes.md](bp_error_codes.md) | 错误码结构、码段分配、枚举与模板、发布稳定性 |
| [bp_unit_testing.md](bp_unit_testing.md) | 单元测试与模块契约测试；开发阶段只允许单元测试 |
| [bp_integration.md](bp_integration.md) | 集成测试；只在测试冒烟阶段编写和执行 |
| [bp_ids.md](bp_ids.md) | 分布式 Long ID 生成与使用 |
| [bp_lock.md](bp_lock.md) | 分布式锁互斥、锁键、超时与数据一致性 |
| [bp_messaging.md](bp_messaging.md) | 集成事件发布、分区顺序、消费可靠性、延迟消息 |
| [bp_compensation.md](bp_compensation.md) | 业务补偿、对账、修复、清理和兜底流程 |

## 依赖方向

主题文档之间的约束引用自底向上：`bp_java` / `bp_common_tools` / `bp_dependencies` / `bp_naming` 是基础，`bp_validation` 同时包含基础校验规则与分层服务校验主题；`bp_layered_service` 定义结构与装配，`bp_resource_naming` 定义资源键运行时边界；`bp_service_calls` 定义同步服务调用的契约与适配边界；`bp_docs` 定义项目文档集合与边界；`bp_persistence`、`bp_logging`、`bp_error_codes`、`bp_ids` / `bp_lock` / `bp_messaging`、`bp_compensation` 在其上定义领域与技术主题，并回引基础文档。`bp_unit_testing` 与 `bp_integration` 按测试阶段拆分：开发阶段只运行单元测试，主题集成验证由 `bp_integration` 在冒烟阶段统一路由。
