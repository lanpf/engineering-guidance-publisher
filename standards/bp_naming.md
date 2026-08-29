# 服务命名最佳实践

本文定义分层服务中的接口、实现、数据载体、技术适配和运行时资源命名约束。

## 命名约定

- 接口按业务角色、端口或技术契约命名，不使用 `I*`、`*Interface`；抽象类使用 `Abstract*`，`Base*` 仅用于框架或共享基础类型。
- 实现类不得使用笼统的 `*Impl`，必须按默认角色、技术、适配职责或策略命名。
- payload、command output、query view 和 effect 不使用 `*Result`；该名称保留给 `Result<T>`、`PageResult<T>`。
- API 使用 `*ApiCommand`、`*ApiCommandOutput`、`*ApiQuery`、`*ApiQueryView`、可复用的 `*ApiResponse`、`*ApiEnum`、`*ApiConstants`、`*ApiEvent` 和 `*Facade`。
- application 使用 `*Command`、`*Output`、`*CommandService`、`*View`、`*QueryService`；分页返回 `PagedList<*View>`，command/query 共用返回类型时才使用 `*Response`。
- 领域服务返回使用 `*Effect`；Repository 契约使用 `*Repository`；领域事件使用 `*Event`。
- infrastructure 类型使用 `*RepositoryAdapter`、技术化 `*PersistenceRepository`、`*DO` 和 `*PersistenceConfiguration`。
- 协议无关 Facade 默认实现位于 `interfaces.facade` 并命名为 `Default*Facade`；必要的技术专属 RPC 适配器使用 `*RpcAdapter`。
- 只有 API payload 可以使用 `*ApiResponse`，只有 application 返回类型可以使用 `*Response`；REST client 远程返回使用 `*Payload`。
- mapper 契约按层级职责命名；MapStruct 实现放入契约包的 `mapstruct` 子包并命名为 `*MapStructMapper`。
- 持久化查询接口按查询条件、范围和排序命名，不按单一调用场景命名。
- MyBatis 与 MyBatis-Plus 共享 SQL 片段文件使用 `<Aggregate>SqlFragments.xml`，namespace 使用 `<工程包>.persistence.sql.<Aggregate>SqlFragments`。
- 具体 mapper XML 使用 `<Aggregate>Mapper.xml`，并通过完全限定的 `refid` 引用共享 `<sql>` 片段。
- OpenFeign 客户端使用 `*FeignClient`。

## 资源命名与命名空间

- 资源名称（包括但不限于缓存键、分布式锁键）的生效范围由命名空间限定：最终名称由命名空间前缀与业务键组成，命名空间必须能区分应用，防止跨应用串扰；环境间隔离由部署基础设施保证，不属于命名空间职责。
- 命名空间只表达应用身份，不得承载业务语义；业务语义只出现在业务键部分。
- 业务键只在命名空间内要求唯一；同一业务键在不同应用中解析为不同的物理资源。
- 业务代码只面向业务键：运行期通过场景 `KeyResolver` 构造资源键，不得感知、解析或手工拼接最终名称中的命名空间前缀。
- 所有对外部资源名称和资源键的定义必须通过 `ResourceNameResolver` 统一解析并注入命名空间。
- 业务场景需要资源键时，必须实现 `Namespaced` 接口表达该场景的命名空间需求，不得手工拼接或声明命名空间前缀。
- 装配时注入 `NamespacedResourceNameResolver`，由 `Namespaced` 配置与解析器组装出该业务场景的 `KeyResolver`。
- 资源键的业务语义与格式约束由所属主题定义：锁键遵循[分布式锁最佳实践](bp_distributed_lock.md#分布式锁)。
