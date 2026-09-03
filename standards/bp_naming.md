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
- 只有 API payload 可以使用 `*ApiResponse`，只有 application 返回类型可以使用 `*Response`；外部服务调用的本地请求与响应载荷类型使用 `*Payload`，内部服务调用无法复用被调用方 API 而定义的本地请求类型使用 `*InternalRequest`。
- mapper 契约按层级职责命名；MapStruct 实现放入契约包的 `mapstruct` 子包并命名为 `*MapStructMapper`。
- 持久化查询接口按查询条件、范围和排序命名，不按单一调用场景命名。
- MyBatis 与 MyBatis-Plus 共享 SQL 片段文件使用 `<Aggregate>SqlFragments.xml`，namespace 使用 `<工程包>.persistence.sql.<Aggregate>SqlFragments`。
- 具体 mapper XML 使用 `<Aggregate>Mapper.xml`，并通过完全限定的 `refid` 引用共享 `<sql>` 片段。
- OpenFeign 客户端使用 `*FeignClient`。

## 资源命名与命名空间

- 本节命名空间与资源命名约束只限制业务服务，不限制框架工程内部模块；`framework-*` 等框架模块处理自身资源键的方式由框架工程文档约定。
- 资源名称（包括但不限于缓存键、分布式锁键）的生效范围由命名空间限定：最终名称由命名空间前缀与业务键组成，命名空间必须能区分应用，防止跨应用串扰；环境间隔离由部署基础设施保证，不属于命名空间职责。
- 命名空间只表达应用身份，不得承载业务语义；业务语义只出现在业务键部分。
- 业务键只在命名空间内要求唯一；同一业务键在不同应用中解析为不同的物理资源。
- 业务代码只面向业务键：具体场景处理器统一以 `*KeyResolver` 结尾并继承 `AbstractKeyResolver`，不得感知、解析或手工拼接最终名称中的命名空间前缀。
- `*KeyResolver` 只负责业务前缀和业务键段，并通过注入的 `ResourceNameResolver` 解析资源键，不得处理命名空间。
- 命名空间必须且只能注入一次；可以在场景装配时由 `ResourceNameResolver` 注入，也可以由最终资源适配边界注入。
- 选择场景装配注入时，场景配置实现 `Namespaced`，并向 `*KeyResolver` 注入由该配置和 `NamespaceResolver` 组装的 `NamespacedResourceNameResolver`。
- 选择最终资源适配边界注入时，`*KeyResolver` 使用不注入命名空间的 `ResourceNameResolver` 实现，由最终适配器统一完成命名空间隔离。
- 禁止 `NamespacedResourceNameResolver` 与最终资源适配器对同一资源重复注入命名空间。
- 框架入口内部已基于 `ResourceNameResolver` 完成解析的场景无需重复处理：如分布式锁使用 `LockExecutor` 时，锁键的命名空间注入与键段规范化拼接由其内部完成，业务代码直接向 `LockContext` 传入稳定的业务键段，不建 `*KeyResolver`，也不得额外解析或注入命名空间。
- 业务代码、配置文件和适配器不得手工拼接或声明应用、环境等命名空间前缀。
- 资源键的业务语义与格式约束由所属主题定义：锁键遵循[分布式锁最佳实践](bp_lock.md#分布式锁)。
