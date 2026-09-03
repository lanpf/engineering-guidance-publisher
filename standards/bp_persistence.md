# 数据持久化最佳实践

本文基于 `framework-persistence`、JPA starter 和 MyBatis-Plus starter，定义数据建模、并发写、事务、查询和技术选择约束。

## 持久化边界

- repository adapter 完成领域 Repository 与数据访问能力之间的适配，persistence repository 只表达数据访问能力。
- 具体 JPA、MyBatis 或 MyBatis-Plus repository、DO、DO 转换 Mapper、SQL/XML 和装配放在独立 persistence 实现 module；领域 Repository 契约遵循[服务分层最佳实践](bp_layered_service.md#domain)。
- 每个 persistence 实现 module 内的 DO 转换 Mapper 负责 domain、application read model 与该技术栈 DO 之间的转换，不得把依赖具体 DO 的转换器放在共享 infrastructure module。
- 同一 repository 只使用一种持久化技术，不得混用 JPA、MyBatis 和 MyBatis-Plus；制品级实现选择遵循[依赖管理最佳实践](bp_dependencies.md#服务技术基线)。
- 持久化实现可以选择 JPA、MyBatis 或 MyBatis-Plus；使用 MyBatis-Plus 的工程在许可证策略不允许时可以降级为 MyBatis，降级不得改变数据库 schema、表名、字段名、查询语义和 repository 可观察行为。
- MyBatis 与 MyBatis-Plus 实现必须共同加载工程根目录 `config/` 中的共享 SQL XML 片段。
- 表名、字段列表和可复用查询条件只在共享片段中声明，具体 mapper statement 通过 `<include>` 引用，不得在两套实现中分别复制。
- 具体加载位置与外部配置要求遵循[服务分层最佳实践](bp_layered_service.md#项目级配置目录)，文件和 namespace 命名遵循[服务命名最佳实践](bp_naming.md#命名约定)。

## 数据模型与命名

- DO 不在不同持久化技术栈之间共享，必须下沉到对应的 JPA、MyBatis 或 MyBatis-Plus 实现 module，并只声明该技术栈必要的实体、主键、枚举等映射注解；类型名称仍以 `DO` 结尾，遵循[服务命名最佳实践](bp_naming.md#命名约定)。
- 同一逻辑持久化模型在不同技术栈中的 DO 必须保持业务字段属性的名称和 Java 类型一致。
- 各技术栈 DO 均不得声明集合属性及 `@ElementCollection`、`@CollectionTable` 等集合映射注解；多值关系拆分为主从 DO 和关联表。
- 只有在多值内容始终整体读写且不需要独立查询、索引或外键约束时，才可以由各技术栈的 DO 转换 Mapper 按一致的转换规则序列化为单个字符串列存储。
- 表名遵循统一 `framework.persistence.naming.table-prefix` 和 `table-suffix` 策略；业务代码不得为规避命名策略在 DO 上重复硬编码表名。
- `schema.sql` 和数据库迁移配置优先放在工程根目录 `config/`，路径和加载方式遵循[服务分层最佳实践](bp_layered_service.md#项目级配置目录)。
- `schema.sql` 文件开头必须注释声明其中表名前缀、后缀需要与运行配置保持一致；修改表名前缀或后缀属于 schema 变更，必须同步修改建表脚本或迁移配置，不得只修改运行配置。
- 主键、业务唯一键和所有业务不变量必须有数据库约束；应用校验和分布式协调不能替代最终约束。

## 并发写与事务

- 并发控制必须先评估业务场景和真实冲突概率；低频运维 API 等极低竞争场景不得为假设性并发过度引入 version、分布式锁或数据库悲观锁。
- 业务对象已有状态机或明确前置状态时，优先使用包含当前状态或业务条件的条件更新；受影响行数不符合预期必须按状态变化或并发冲突处理，不得静默覆盖。
- 确有跨实例并发冲突且业务条件不足以收敛时，优先使用分布式锁降低竞争；只有残余冲突风险仍需要检测时才增加 version 乐观并发。不得把 version、数据库悲观锁或分布式锁作为所有写操作的默认模板。
- 事务必须短小，只覆盖同一数据库内必要读写，不得在事务中执行可避免的 RPC、消息发送、长计算或等待锁；事务边界的分层归属遵循[服务分层最佳实践](bp_layered_service.md#application)。
- 数据写入涉及集成事件时，原子提交与发布遵循[分布式消息最佳实践](bp_messaging.md#事件与发布)。
- 重试写操作必须幂等，并显式处理唯一约束冲突、乐观锁冲突、死锁和瞬时连接故障；不得无界重试。

## 唯一约束异常

- 已知业务唯一约束冲突必须在 persistence adapter 边界转换为明确的领域/应用异常，或在确认请求语义与既有数据一致后按幂等成功处理；不得把数据库异常直接泄漏到 application、interfaces 或 API。
- MyBatis 经 Spring 异常转换抛出的 `DuplicateKeyException` 是 `DataIntegrityViolationException` 的子类，因此 JPA 和 MyBatis 可以统一捕获 `DataIntegrityViolationException`。
- 统一捕获后必须依据已知约束名、SQLState/厂商错误码或冲突后的业务键回查确认它确实是目标唯一约束冲突，不得把非空、外键、检查约束等其他完整性错误当成重复键。
- JPA 若要在 adapter 内捕获唯一约束异常，必须在该捕获边界内执行 `flush`；否则异常可能推迟到事务提交时才抛出，应改由覆盖提交边界的统一转换器处理。
- 无论转换为业务异常还是按幂等成功处理，都必须在唯一的转换边界记录日志，包含约束或场景、脱敏后的业务键和处理结果；预期幂等冲突使用 `INFO` 或 `WARN`，未知或无法分类的完整性错误使用 `ERROR` 并继续抛出，脱敏形式遵循[日志与敏感数据最佳实践](bp_logging.md#日志与敏感数据)。

## 查询与性能

- 分页必须有稳定且唯一的排序，深分页或持续扫描优先使用游标；不得依赖数据库未指定顺序。
- 查询条件、排序和关联路径必须由匹配索引支持；新增高频或大表查询前验证执行计划。
- 持久化查询接口命名遵循[服务命名最佳实践](bp_naming.md#命名约定)。
- 禁止 N+1 查询和无界结果集；批量读写必须限制批次大小，避免一次性加载全部数据。
- MyBatis-Plus 的数据库类型必须显式正确配置，不支持的类型必须启动失败；自定义 interceptor 必须保持确定顺序并验证不会绕过分页或命名策略。
- JPA 不得在接口层依赖 Open Session in View 补偿懒加载；聚合加载边界和只读 projection 必须显式设计。

## 验证

- 持久化集成测试使用真实数据库/Testcontainers，覆盖 schema 约束、命名策略、事务回滚、并发冲突、分页稳定性和关键查询计划。
- 同一组 repository 契约如有多种实现，必须使用共享契约测试验证可观察行为一致。
