# 服务命名最佳实践

本文定义分层服务中的接口、实现、数据载体、技术适配和运行时资源命名约束。

## 命名约定

- **强制 · 基础**：接口按业务角色、端口或技术契约命名，不使用 `I*`、`*Interface`；抽象类使用 `Abstract*`，`Base*` 仅用于框架或共享基础类型。
- **强制 · 基础**：实现类不得使用笼统的 `*Impl`，必须按默认角色、技术、适配职责或策略命名。
- **强制 · 基础**：payload、command output、query view 和 effect 不使用 `*Result`；该名称保留给 `Result<T>`、`PageResult<T>`。
- **强制 · 基础**：API 使用 `*ApiCommand`、`*ApiCommandOutput`、`*ApiQuery`、`*ApiQueryView`、可复用的 `*ApiResponse`、`*ApiEnum`、`*ApiConstants`、`*ApiEvent` 和 `*Facade`。
- **强制 · 基础**：application 使用 `*Command`、`*Output`、`*CommandService`、`*View`、`*QueryService`；分页返回 `PagedList<*View>`，command/query 共用返回类型时才使用 `*Response`。
- **强制 · 基础**：领域服务返回使用 `*Effect`；Repository 契约使用 `*Repository`；领域事件使用 `*Event`。
- **强制 · 基础**：infrastructure 类型使用 `*RepositoryAdapter`、技术化 `*PersistenceRepository`、`*DO` 和 `*PersistenceConfiguration`。
- **强制 · 基础**：协议无关 Facade 默认实现位于 `interfaces.facade` 并命名为 `Default*Facade`；必要的技术专属 RPC 适配器使用 `*RpcAdapter`。
- **强制 · 基础**：只有 API payload 可以使用 `*ApiResponse`，只有 application 返回类型可以使用 `*Response`；外部服务调用的本地协议模型使用“外部服务名 + 动作或资源 + `RequestPayload`/`ResponsePayload`”命名，例如 `GithubSearchRepositoriesRequestPayload`、`GithubSearchRepositoriesResponsePayload`，不得使用缺少外部服务身份或调用语义的 `RequestPayload`、`CreateRequestPayload` 等名称；内部服务调用无法复用被调用方 API 而定义的本地请求类型使用 `*InternalRequest`。
- **强制 · 基础**：mapper 契约按层级职责命名；MapStruct 实现放入契约包的 `mapstruct` 子包并命名为 `*MapStructMapper`。
- **强制 · 基础**：持久化查询接口按查询条件、范围和排序命名，不按单一调用场景命名。
- **强制 · 基础**：MyBatis 与 MyBatis-Plus 共享 SQL 片段文件使用 `<Aggregate>SqlFragments.xml`，namespace 使用 `<工程包>.persistence.sql.<Aggregate>SqlFragments`。
- **强制 · 基础**：具体 mapper XML 使用 `<Aggregate>Mapper.xml`，并通过完全限定的 `refid` 引用共享 `<sql>` 片段。
- **强制 · 基础**：OpenFeign 客户端使用 `*FeignClient`。
- **强制 · 基础**：具体业务场景的资源键处理器以 `*KeyResolver` 结尾并继承 `AbstractKeyResolver`；其运行时职责遵循[资源命名最佳实践](bp_resource_naming.md#资源键与命名空间)。
- **强制 · 基础**：包名必须使用小写并表达稳定职责或变化边界；禁止使用 `misc`、`temp`、`other` 等无语义包，也不得把业务类型放入笼统的 `util` 或 `common` 包。包的层级和分组遵循[服务分层最佳实践](bp_layered_service.md#包结构)。
