# 服务命名最佳实践

本文定义分层服务中的接口、实现、数据载体和技术适配命名约束。

## 命名约定

- 接口按业务角色、端口或技术契约命名，不使用 `I*`、`*Interface`；抽象类使用 `Abstract*`，`Base*` 仅用于框架或共享基础类型。
- 实现类不得使用笼统的 `*Impl`，必须按默认角色、技术、适配职责或策略命名。
- payload、command output、query view 和 effect 不使用 `*Result`；该名称保留给 `Result<T>`、`PageResult<T>`。
- 只有 API payload 可以使用 `*ApiResponse`，只有 application 返回类型可以使用 `*Response`；REST client 远程返回使用 `*Payload`。
- mapper 契约按层级职责命名；MapStruct 实现放入契约包的 `mapstruct` 子包并命名为 `*MapStructMapper`。
- API 使用 `*ApiCommand`、`*ApiCommandOutput`、`*ApiQuery`、`*ApiQueryView`、可复用的 `*ApiResponse`、`*ApiEnum`、`*ApiConstants`、`*ApiEvent` 和 `*Facade`。
- 领域服务返回使用 `*Effect`；Repository 契约使用 `*Repository`；领域事件使用 `*Event`。
- application 使用 `*Command`、`*Output`、`*CommandService`、`*View`、`*QueryService`；分页返回 `PagedList<*View>`，command/query 共用返回类型时才使用 `*Response`。
- infrastructure 类型使用 `*RepositoryAdapter`、技术化 `*PersistenceRepository`、`*DO` 和 `*PersistenceConfiguration`。
- MyBatis 与 MyBatis-Plus 共享 SQL 片段文件使用 `<Aggregate>SqlFragments.xml`，namespace 使用 `<工程包>.persistence.sql.<Aggregate>SqlFragments`；具体 mapper XML 使用 `<Aggregate>Mapper.xml`，并通过完全限定的 `refid` 引用共享 `<sql>` 片段。
- 协议无关 Facade 默认实现位于 `interfaces.facade` 并命名为 `Default*Facade`；必要的技术专属 RPC 适配器使用 `*RpcAdapter`。
- OpenFeign 客户端使用 `*FeignClient`。
