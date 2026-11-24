# 数据持久化最佳实践

本文基于 `framework-persistence`、JPA starter 和 MyBatis-Plus starter，定义数据建模、并发写、事务、查询和技术选择约束。

## 持久化边界

- **强制 · 主题**：repository adapter 完成领域 Repository 与数据访问能力之间的适配，persistence repository 只表达数据访问能力。 <!-- INFRA-REPOSITORY-001 -->
- **强制 · 主题**：具体 JPA、MyBatis 或 MyBatis-Plus repository、DO、DO 转换 Mapper，以及 SQL/XML 的加载、装配与验证职责归属独立 persistence 实现 module；资源物理位置遵循[服务分层最佳实践](bp_layered_service.md#项目级配置目录)，领域 Repository 契约遵循[服务分层最佳实践](bp_layered_service.md#domain)。 <!-- INFRA-PERSISTENCE-001 -->
- **强制 · 主题**：每个 persistence 实现 module 内的 DO 转换 Mapper 负责 domain、application read model 与该技术栈 DO 之间的转换，不得把依赖具体 DO 的转换器放在共享 infrastructure module。 <!-- INFRA-MAPPER-001 -->
- **强制 · 主题**：一个 persistence 实现 module 只使用一种持久化技术；JPA、MyBatis 和 MyBatis-Plus 的替代实现可以存在于不同 module，但不得在同一实现 module 内混用。 <!-- PERSISTENCE-MODULE-TECHNOLOGY-001 -->
- **强制 · 主题**：一个运行时制品只装配同一 repository 契约的一种实现，具体选择遵循[依赖管理最佳实践](bp_dependencies.md#服务技术基线)。 <!-- PERSISTENCE-RUNTIME-IMPLEMENTATION-001 -->
- **强制 · 主题**：持久化实现可以选择 JPA、MyBatis 或 MyBatis-Plus；使用 MyBatis-Plus 的工程在许可证策略不允许时可以降级为 MyBatis，降级不得改变数据库 schema、表名、字段名、查询语义和 repository 可观察行为。 <!-- PERSISTENCE-MYBATIS-COMPAT-001 -->
- **强制 · 主题**：共存的 MyBatis 和 MyBatis-Plus 替代实现必须加载同一份共享 SQL XML 片段。存放位置遵循项目级配置目录的版本与回滚规则。 <!-- PERSISTENCE-MYBATIS-SQL-001 -->
- **强制 · 主题**：表名、字段列表和可复用查询条件只在共享片段中声明，具体 mapper statement 通过 `<include>` 引用，不得在两套实现中分别复制。 <!-- PERSISTENCE-MYBATIS-SQL-002 -->
具体加载位置与外部配置要求遵循[服务分层最佳实践](bp_layered_service.md#项目级配置目录)，文件和 namespace 命名遵循[服务命名最佳实践](bp_naming.md#命名约定)。

## 数据模型与命名

- **强制 · 主题**：DO 不在不同持久化技术栈之间共享，必须下沉到对应的 JPA、MyBatis 或 MyBatis-Plus 实现 module，并只声明该技术栈必要的实体、主键、枚举等映射注解；类型名称遵循[服务命名最佳实践](bp_naming.md#命名约定)。 <!-- INFRA-DO-001 -->
- **强制 · 主题**：同一逻辑持久化模型在不同技术栈中的 DO 必须保持业务字段属性的名称和 Java 类型一致。 <!-- PERSISTENCE-DO-PORTABILITY-001 -->
- **强制 · 主题**：各技术栈 DO 均不得声明集合属性及 `@ElementCollection`、`@CollectionTable` 等集合映射注解；多值关系拆分为主从 DO 和关联表。 <!-- PERSISTENCE-DO-COLLECTION-001 -->
- **强制 · 主题**：只有在多值内容始终整体读写且不需要独立查询、索引或外键约束时，才可以由各技术栈的 DO 转换 Mapper 按一致的转换规则序列化为单个字符串列存储。 <!-- PERSISTENCE-DO-COLLECTION-002 -->
- **强制 · 主题**：表名遵循统一 `framework.persistence.naming.table-prefix` 和 `table-suffix` 策略；业务代码不得为规避命名策略在 DO 上重复硬编码表名。 <!-- PERSISTENCE-TABLE-NAMING-001 -->
- **默认 · 主题**：schema.sql 与迁移脚本默认随其对应的应用或版本化迁移制品交付。由运维独立管理的资源按项目级配置约定外置。 <!-- PERSISTENCE-SCHEMA-LOCATION-001 -->
- **强制 · 主题**：`schema.sql` 文件开头必须注释声明其中表名前缀、后缀需要与运行配置保持一致。 <!-- PERSISTENCE-SCHEMA-PREFIX-COMMENT-001 -->
- **强制 · 主题**：修改表名前缀或后缀属于 schema 变更，必须同步修改建表脚本或迁移配置，不得只修改运行配置。 <!-- PERSISTENCE-SCHEMA-NAMING-CHANGE-001 -->
- **强制 · 主题**：主键、业务唯一键以及数据库能够表达的非空、引用完整性、取值范围等持久化不变量必须有数据库约束；应用校验和分布式协调不能替代这些最终约束。跨聚合、跨服务或时序业务规则由 domain/application 保证。 <!-- PERSISTENCE-SCHEMA-001 -->

## 并发写与事务

- **强制 · 主题**：选择并发控制前必须评估业务风险、真实冲突概率、竞争范围和失败后果。 <!-- PERSISTENCE-CONCURRENCY-SCENARIO-001 -->
- **默认 · 主题**：低频运维 API 若已有数据库保护或覆盖写符合契约，默认不再增加锁或版本字段。即使竞争罕见，丢失更新会违反契约时仍须提供保护。 <!-- PERSISTENCE-CONCURRENCY-LOW-001 -->
- **默认 · 主题**：业务对象已有状态机或明确前置状态时，优先使用包含当前状态或业务条件的条件更新。 <!-- PERSISTENCE-CONCURRENCY-STATE-001 -->
- **强制 · 主题**：条件更新的受影响行数不符合预期时必须按状态变化或并发冲突处理，不得静默覆盖。 <!-- PERSISTENCE-CONCURRENCY-AFFECTED-ROWS-001 -->
- **默认 · 主题**：单库写入优先评估原子更新、唯一约束、版本检查或数据库锁。需要跨资源协调或有证据表明需要削减竞争时，再评估分布式锁及其失效成本。 <!-- PERSISTENCE-CONCURRENCY-001 -->
- **默认 · 主题**：需要检测基于过期快照的写入时，优先评估版本检查，并定义冲突后的返回或重试语义。 <!-- PERSISTENCE-CONCURRENCY-VERSION-001 -->
- **强制 · 主题**：不得把 version、数据库悲观锁或分布式锁作为所有写操作的默认模板。 <!-- PERSISTENCE-CONCURRENCY-TEMPLATE-001 -->
- **强制 · 主题**：事务必须短小，只覆盖同一数据库内必要读写，不得在事务中执行可避免的 RPC、消息发送、长计算或等待锁；事务边界的分层归属遵循[服务分层最佳实践](bp_layered_service.md#application)。 <!-- PERSISTENCE-TRANSACTION-001 -->
数据写入涉及集成事件时，原子提交与发布遵循[分布式消息最佳实践](bp_messaging.md#事件与发布)。
- **强制 · 主题**：重试写操作必须幂等。 <!-- PERSISTENCE-RETRY-IDEMPOTENT-001 -->
- **强制 · 主题**：写操作重试必须显式分类处理唯一约束冲突、乐观锁冲突、死锁和瞬时连接故障，并限制重试次数，不得无界重试。 <!-- PERSISTENCE-RETRY-POLICY-001 -->

## 唯一约束异常

- **强制 · 主题**：已知业务唯一约束冲突必须在 persistence adapter 边界转换为明确的领域/应用异常，或在确认请求语义与既有数据一致后按幂等成功处理；不得把数据库异常直接泄漏到 application、interfaces 或 API。 <!-- PERSISTENCE-DUPLICATE-001 -->
- **建议 · 主题**：MyBatis 经 Spring 异常转换抛出的 `DuplicateKeyException` 是 `DataIntegrityViolationException` 的子类，因此 JPA 和 MyBatis 可以在同一转换边界捕获 `DataIntegrityViolationException`；这是一项实现说明，不替代下述分类要求。 <!-- PERSISTENCE-DATA-INTEGRITY-001 -->
- **强制 · 主题**：先用 SQLState 或厂商错误码识别冲突类别，再通过约束名或能区分目标约束的业务证据确定归属。存在多个唯一约束时，仅有唯一冲突类别不足以映射到具体业务结果。 <!-- PERSISTENCE-DATA-INTEGRITY-002 -->
- **强制 · 主题**：JPA 若要在 adapter 内捕获唯一约束异常，必须在该捕获边界内执行 `flush`；否则异常可能推迟到事务提交时才抛出，应改由覆盖提交边界的统一转换器处理。 <!-- PERSISTENCE-JPA-FLUSH-001 -->
- **强制 · 主题**：唯一约束异常后，若事务已失败、标记回滚或持久化上下文不再可靠，不得继续用该事务或上下文回查并返回幂等成功；尤其在 JPA/Hibernate 持久化异常后，应先结束失败事务，再通过有效的新事务或独立查询边界核验既有结果。不得仅在失败事务内部开启嵌套调用便宣称恢复成功；核验失败仍须传播失败。 <!-- PERSISTENCE-IDEMPOTENT-RECOVERY-001 -->
- **强制 · 主题**：无论转换为业务异常还是按幂等成功处理，都必须在唯一的转换边界记录日志，包含约束或场景、脱敏后的业务键和处理结果；级别、重复事件聚合与审计例外统一遵循[日志与敏感数据最佳实践](bp_logging.md#日志与敏感数据)。 <!-- PERSISTENCE-CONFLICT-LOG-001 -->
- **强制 · 主题**：未知或无法分类的完整性错误必须继续抛出，不得转为业务唯一冲突或幂等成功。 <!-- PERSISTENCE-UNKNOWN-INTEGRITY-001 -->

## 查询与性能

- **强制 · 主题**：分页必须使用稳定且唯一的排序，不得依赖数据库未指定顺序。 <!-- PERSISTENCE-PAGE-001 -->
- **默认 · 主题**：深分页或持续扫描优先使用游标。 <!-- PERSISTENCE-CURSOR-001 -->
- **强制 · 主题**：查询索引须依据访问模式、数据规模和执行计划设计；新增高频或大表查询前必须验证执行计划和性能满足场景要求，不得机械要求每个查询条件独立建索引。 <!-- PERSISTENCE-QUERY-PLAN-001 -->
持久化查询接口命名遵循[服务命名最佳实践](bp_naming.md#命名约定)。
- **强制 · 主题**：禁止 N+1 查询。 <!-- PERSISTENCE-NPLUSONE-001 -->
- **强制 · 主题**：查询必须限定结果集范围，禁止无界结果集。 <!-- PERSISTENCE-RESULT-BOUND-001 -->
- **强制 · 主题**：批量读写必须限制批次大小，避免一次性加载全部数据。 <!-- PERSISTENCE-BATCH-SIZE-001 -->
- **强制 · 主题**：MyBatis-Plus 的数据库类型必须显式正确配置，不支持的类型必须启动失败。 <!-- PERSISTENCE-MYBATIS-DATABASE-TYPE-001 -->
- **强制 · 主题**：自定义 interceptor 必须保持确定顺序，并验证不会绕过分页或命名策略。 <!-- PERSISTENCE-INTERCEPTOR-ORDER-001 -->
- **强制 · 主题**：JPA 不得在接口层依赖 Open Session in View 补偿懒加载；聚合加载边界和只读 projection 必须显式设计。 <!-- PERSISTENCE-JPA-001 -->

## 验证

- **强制 · 主题**：冒烟阶段的持久化集成测试使用真实数据库/Testcontainers，覆盖 schema 约束、命名策略、事务回滚、并发冲突、分页稳定性和关键查询计划。 <!-- TEST-PERSISTENCE-INTEGRATION-001 -->
- **强制 · 主题**：同一组 repository 契约如有多种替代实现，冒烟阶段必须使用共享契约测试验证可观察行为一致。 <!-- TEST-PERSISTENCE-CONTRACT-001 -->
