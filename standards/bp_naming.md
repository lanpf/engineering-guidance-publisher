# 服务命名最佳实践

本文定义分层服务中的接口、实现、数据载体、技术适配和运行时资源命名约束。

## 命名约定

- **默认 · 主题**：接口按业务角色、端口或技术契约命名，不使用 `I*`、`*Interface`。 <!-- NAME-INTERFACE-ROLE-001 -->
- **默认 · 主题**：抽象类使用 `Abstract*`，`Base*` 仅用于框架或共享基础类型。 <!-- NAME-ABSTRACT-BASE-001 -->
- **默认 · 主题**：实现类不得使用笼统的 `*Impl`，必须按默认角色、技术、适配职责或策略命名。 <!-- NAME-IMPLEMENTATION-001 -->
- **默认 · 主题**：Spring Boot 自动配置入口类必须统一命名为 `*AutoConfiguration`。除组件扫描的 wiring 类外，其他类型不得以 `Configuration` 结尾，应按实际职责命名。 <!-- NAME-AUTO-CONFIGURATION-001 -->
- **默认 · 主题**：组件扫描的 wiring 类使用 `*Configuration` 命名。 <!-- NAME-CONFIGURATION-001 -->
- **默认 · 主题**：配置属性绑定类使用 `*Properties` 命名。 <!-- NAME-PROPERTIES-001 -->
- **默认 · 主题**：payload、command output、query view 和 effect 不使用 `*Result`；该名称保留给 `Result<T>`、`PageResult<T>`。 <!-- NAME-RESULT-001 -->
- **默认 · 主题**：API 类型按下表中的角色使用对应名称。 <!-- NAME-API-001 -->

| API 角色 | 名称 |
| --- | --- |
| 写入请求 / 输出 | `*ApiCommand` / `*ApiOutput` |
| 查询请求 / 视图 | `*ApiQuery` / `*ApiView` |
| 枚举 / 常量 / 集成事件 | `*ApiEnum` / `*ApiConstants` / `*ApiEvent` |
| 写能力 / 查询能力契约 | `*CommandFacade` / `*QueryFacade` |
- **默认 · 主题**：application 类型按下表中的角色使用对应名称；分页返回契约遵循[服务分层最佳实践](bp_layered_service.md#application)。 <!-- NAME-APPLICATION-001 -->

| application 角色 | 名称 |
| --- | --- |
| 写用例服务 / 请求 / 输出 | `*CommandService` / `*Command` / `*Output` |
| 查询服务 / 条件 / 视图 | `*QueryService` / `*Query` / `*View` |
- **默认 · 主题**：领域类型按下表中的角色使用对应名称。 <!-- NAME-DOMAIN-001 -->

| domain 角色 | 名称 |
| --- | --- |
| 领域服务返回 | `*Effect` |
| Repository 契约 | `*Repository` |
| 领域事件 | `*Event` |
- **默认 · 主题**：infrastructure 类型按下表中的角色使用对应名称。 <!-- NAME-INFRA-001 -->

| infrastructure 角色 | 名称 |
| --- | --- |
| Repository 适配器 | `*RepositoryAdapter` |
| 技术化持久化 Repository | `*PersistenceRepository` |
| 数据对象 | `*DO` |
| 持久化自动配置入口 | `*PersistenceAutoConfiguration` |
- **默认 · 主题**：协议无关 Facade 默认实现位于 `interfaces.facade` 并命名为 `Default*Facade`；必要的技术专属 RPC 适配器使用 `*RpcAdapter`。 <!-- NAME-INTERFACES-001 -->
- **默认 · 主题**：只有 API payload 在共用返回类型时可以使用 `*ApiResponse`。 <!-- NAME-API-SHARED-RESPONSE-001 -->
- **默认 · 主题**：只有 application 在共用返回类型时可以使用 `*Response`。 <!-- NAME-APPLICATION-RESPONSE-001 -->
- **默认 · 主题**：外部服务调用的本地协议模型使用“外部服务名 + 动作或资源 + `RequestPayload`/`ResponsePayload`”命名，例如 `GithubSearchRepositoriesRequestPayload`；不得使用缺少外部服务身份或调用语义的 `RequestPayload`、`CreateRequestPayload` 等名称。 <!-- NAME-REMOTE-PAYLOAD-001 -->
- **默认 · 主题**：内部服务调用无法复用被调用方 API 而定义的本地请求类型使用 `*InternalRequest`。 <!-- NAME-INTERNAL-REQUEST-001 -->
- **默认 · 主题**：mapper 契约按层级职责命名，手写 MapStruct mapper 类型命名为 `*MapStructMapper`。 <!-- NAME-MAPPER-TYPE-001 -->
- **默认 · 主题**：存在独立转换契约时，手写 MapStruct mapper 默认放在契约包的 mapstruct 子包。单一 mapper 可与所属功能放在同一包。 <!-- NAME-MAPPER-PACKAGE-001 -->
- **强制 · 主题**：持久化查询接口按查询条件、范围和排序命名，不按单一调用场景命名。 <!-- INFRA-QUERY-001 -->
- **强制 · 主题**：MyBatis 与 MyBatis-Plus 共享 SQL 片段文件使用 `<Aggregate>SqlFragments.xml`，namespace 使用 `<工程包>.persistence.sql.<Aggregate>SqlFragments`。 <!-- NAME-MYBATIS-SQL-001 -->
- **强制 · 主题**：具体 mapper XML 使用 `<Aggregate>Mapper.xml`。 <!-- NAME-MYBATIS-MAPPER-FILE-001 -->
- **强制 · 主题**：共享片段的复用遵循[数据持久化最佳实践](bp_persistence.md#持久化边界)，引用时 `refid` 必须使用完全限定名称。 <!-- NAME-MYBATIS-REFID-001 -->
- **默认 · 主题**：OpenFeign 客户端使用 `*FeignClient`。 <!-- NAME-CLIENT-001 -->
- **默认 · 主题**：具体业务场景的资源键处理器以 `*KeyResolver` 结尾。 <!-- NAME-KEY-RESOLVER-SUFFIX-001 -->
- **强制 · 主题**：具体业务场景的 `*KeyResolver` 必须继承 `AbstractKeyResolver`；运行时职责遵循[资源命名最佳实践](bp_resource_naming.md#资源键与命名空间)。 <!-- NAME-KEY-RESOLVER-BASE-001 -->
- **默认 · 主题**：包名必须使用小写并表达稳定职责或变化边界；禁止使用 `misc`、`temp`、`other` 等无语义包，也不得把业务类型放入笼统的 `util` 或 `common` 包。包的层级和分组遵循[服务分层最佳实践](bp_layered_service.md#包结构)。 <!-- NAME-PACKAGE-001 -->
