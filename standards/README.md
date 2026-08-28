# Standards 索引

本目录存放人工维护的最佳实践政策源文档（`bp_*.md`）。结构化发布表示见仓库根目录 `catalog.json`，它定义版本、持久规则 ID、Skill 路由和生成的详细规则文本；本 README 只做索引与约定，不复制具体规则。

## 约定

- 所有 `bp_*.md` 的约束默认适用于全部服务工程；项目规约可以补充或收紧，但不得放宽或覆盖。
- 规则编号、标题和规则语义在发布后保持稳定；发布后不得重用规则 ID 表达不同语义，标题是 `catalog.json` 引用身份的一部分，不得随手改名。
- `## 验证` 章节只写在具有可运行验证行为的主题文档中；语言、命名等静态约束由代码评审与静态检查保障。

## 文档索引

| 文档 | 范围 |
| --- | --- |
| [bp_java.md](bp_java.md) | Java 语言、常量与字面量、参数校验、异常 |
| [bp_common_tools.md](bp_common_tools.md) | 基础工具类、Lombok、MapStruct |
| [bp_naming.md](bp_naming.md) | 接口、实现、数据载体、技术适配与 MyBatis XML 命名 |
| [bp_layered_service.md](bp_layered_service.md) | 规约体系、module 分层、依赖方向、项目级配置、层内约定、不可变数据载体 |
| [bp_dependencies.md](bp_dependencies.md) | Maven 依赖、module 边界、版本管理、服务技术基线 |
| [bp_persistence.md](bp_persistence.md) | 持久化边界、数据模型、并发写与事务、唯一约束异常、查询与性能 |
| [bp_logging.md](bp_logging.md) | 日志级别、日志内容、链路上下文、敏感数据定义与脱敏 |
| [bp_error_codes.md](bp_error_codes.md) | 错误码结构、码段分配、枚举与模板、发布稳定性 |
| [bp_distributed_id.md](bp_distributed_id.md) | 分布式 Long ID 生成与使用 |
| [bp_distributed_lock.md](bp_distributed_lock.md) | 分布式锁互斥、锁键、超时与数据一致性 |
| [bp_distributed_messaging.md](bp_distributed_messaging.md) | 集成事件发布、分区顺序、消费可靠性、延迟消息 |
| [bp_business_compensation.md](bp_business_compensation.md) | 业务补偿、对账、修复、清理和兜底流程 |

## 依赖方向

主题文档之间的约束引用自底向上：`bp_java` / `bp_common_tools` / `bp_naming` 是基础；`bp_layered_service` 和 `bp_dependencies` 定义结构与装配；`bp_persistence`、`bp_logging`、`bp_error_codes`、`bp_distributed_*`、`bp_business_compensation` 在其上定义领域与技术主题，并回引基础文档。
