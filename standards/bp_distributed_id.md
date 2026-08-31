# 分布式 ID 最佳实践

本文基于 `framework-id` 契约和 `framework-starter-id-cosid` 实现，定义服务内分布式 Long ID 的生成和使用约束。

## 分布式 ID

- 跨实例创建的聚合、领域事件持久化 Envelope、集成事件和需要全局唯一标识的数据，必须通过注入 `LongIdGenerator` 生成趋势递增的 Long ID，不得依赖数据库自增主键、随机数、时间戳拼接或各业务自行实现生成算法。
- 调用 `nextId(name)` 时必须使用稳定、可配置且能明确区分 ID 空间的生成器名称；不得把用户输入、请求 ID 或每条数据的业务键动态拼成生成器名称。
- 生成器名称和对应 CosId 配置必须在部署前完成注册与校验；缺失的生成器必须启动失败或用例快速失败，不得静默降级到本地算法或数据库自增。
- 聚合等业务标识由 application/infrastructure 通过框架端口生成后传入 domain；领域事件持久化 ID 则由 EventStore 在 infrastructure 边界构造 Envelope 时生成。domain 不得依赖 `LongIdGenerator`、CosId 或 starter 类型。
- ID 只用于唯一标识和必要的趋势排序；业务不得假设 ID 连续、无空洞、严格按时间排序，也不得从 ID 位段解析业务语义。
- 非 Long 的字符串标识（如 UUID、外部系统标识）不在 `LongIdGenerator` 范围内；业务不得自行设计新的生成算法，来源由项目领域文档约定，类型定义遵循[服务分层最佳实践](bp_layered_service.md#domain)的 `EntityId` 工程级基类。
- 任何节点/机器标识和时钟回拨策略必须由统一基础设施配置保证安全；不得在业务 module 覆盖或硬编码节点标识。
- ID 的数据库约束遵循[数据持久化最佳实践](bp_persistence.md#数据模型与命名)。

## 验证

- 集成测试必须覆盖同一生成器连续生成、多个生成器名称隔离以及缺失名称快速失败。
- 涉及多实例部署时，必须验证不同实例不会使用冲突的节点身份，并验证时钟回拨处置符合配置预期。
