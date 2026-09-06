# 服务分层最佳实践

本文定义服务工程的领域文档、module 分层、层内边界和跨层数据约束；`<工程名>` 表示具体服务。服务还必须遵守自身权威领域文档，项目规约只能补充或收紧共享最佳实践。

## 规约体系

- **强制 · 主题**：修改分层、领域边界或 API 业务语义前，必须按[项目文档最佳实践](bp_docs.md#必备文档)读取项目入口路由的权威文档；项目规则可以补充或收紧共享规则，不得重复、放宽或覆盖。

## 分层结构

### 模块职责

- **强制 · 主题**：`<工程名>-api` 定义稳定的对外 API 契约。
- **强制 · 主题**：`<工程名>-domain` 承载核心领域模型和领域规则。
- **强制 · 主题**：`<工程名>-application` 编排写用例和只读查询。
- **强制 · 主题**：`<工程名>-infrastructure` 提供技术适配、持久化抽象和与具体技术栈无关的通用转换，不得放置具体持久化技术的 DO 及其转换 Mapper。
- **强制 · 主题**：具体持久化、调度和消息实现分别放在 `<工程名>-infrastructure-persistence-<技术>`、`<工程名>-infrastructure-scheduler-<技术>`、`<工程名>-infrastructure-message-<技术>`。
- **强制 · 主题**：持久化实现 module 同时承载该技术栈的 DO、DO 转换 Mapper、repository、SQL/XML 和装配。
- **强制 · 主题**：`<工程名>-interfaces` 提供协议无关 Facade 实现及 REST、RPC、消息订阅等协议入口。
- **强制 · 主题**：`<工程名>-openfeign-client` 提供调用本服务的 OpenFeign 客户端。
- **强制 · 主题**：`<工程名>-boot` 只负责启动、运行时配置和打包。
- **强制 · 主题**：`<工程名>-integration-tests` 是独立测试 module，承载跨 module、完整自动装配以及依赖真实数据库或中间件的集成测试；生产 module 不得依赖它。

### 包结构

- **强制 · 主题**：顶层包必须与所属 module 的职责一致，例如 `api`、`domain`、`application`、`infrastructure`、`interfaces`；不得在 module 根包下直接混放不同层或不同技术适配的生产类。
- **强制 · 主题**：包之间的依赖方向必须与[服务分层最佳实践](bp_layered_service.md#依赖方向)一致；包拆分不得绕过 module 依赖约束，也不得用跨包访问、反射或事件隐藏反向依赖。
- **默认 · 主题**：同一层内按业务能力或技术适配分组（feature-first），再按需要细分 `api`、`service`、`repository`、`mapper` 等角色；不要默认按全局类名分类建立孤立的 `entity`、`service`、`repository` 包。
- **强制 · 主题**：`infrastructure` module 的顶层包必须继续按能力或适配边界分包，例如 `persistence`、`messaging`、`locking`、`external`、`configuration`；不得将所有 adapter、DO、mapper、configuration 和 client 直接放在同一个 `infra` 包中。
- **强制 · 主题**：具体技术 module 先按技术栈分组，再按聚合、资源或外部服务分组；同一能力的 DO、技术 repository、转换 mapper 和装配可以放在同一 feature package 或其角色子包内，但不得跨技术栈共享具体 DO 或技术注解。
- **强制 · 主题**：跨能力复用必须通过稳定的 port、契约或明确的公共组件完成；不得通过访问另一个 feature package 的实现类、数据库 DO 或 mapper 建立隐式耦合。
- **默认 · 主题**：只有在包内类型形成清晰的职责闭包后才继续细分；单个类型不应为了目录整齐单独建立一层包，包过大时应按能力或变化原因拆分，而不是机械按类名拆分。
- **强制 · 主题**：包内实现默认使用 package-private；只有跨包、跨 module 或框架装配需要的类型才声明为 `public`，公开类型必须有明确契约或适配职责。
- **默认 · 主题**：测试包路径镜像生产包路径；测试辅助类只在测试源集或测试支持包中提供，不得进入生产包或被生产代码依赖。

### 依赖方向

- **强制 · 主题**：api 不依赖业务实现；domain 不依赖其他业务层；application 依赖 domain。
- **强制 · 主题**：infrastructure 实现 domain/application 定义的端口，具体技术实现 module 依赖 infrastructure。
- **强制 · 主题**：interfaces 依赖 api/application，openfeign-client 依赖 api，boot 只做最终装配。
- **强制 · 主题**：integration-tests 可以用 test scope 依赖 boot 和被观测的服务 module；该依赖只用于验证，不得形成生产代码依赖方向的一部分。
- **强制 · 主题**：内层 module 不得反向依赖外层协议、持久化实现、持久化对象或 boot。

### 项目级配置目录

- **强制 · 主题**：工程根目录必须设置与各 module 平级的 `config/` 目录，作为可独立更新资源的首选存放位置。
- **默认 · 主题**：项目级 `application.yml`、`application-*.yml` 或对应 properties、MyBatis 共享 SQL 片段与 mapper XML、数据库 schema/迁移脚本、Dubbo XML 等配置优先放在该目录。
- **强制 · 主题**：不得仅因某个 module 负责装配就把可独立更新的配置资源打入其制品。
- **强制 · 主题**：boot 必须通过 `spring.config.location`、`spring.config.additional-location`、`spring.config.import`、框架专属 location 配置或等效启动参数显式加载 `config/` 中的资源；构建、部署和本地启动流程必须保证这些资源可用，并验证缺失或无效配置能够按预期失败。
- **强制 · 主题**：只有框架不支持外部加载、资源与代码在版本和类路径上不可拆分，或制品必须自包含且无法由部署环境提供时，才可以把资源放在对应 module 的 `src/main/resources`。不得为了开发便利牺牲配置的独立发布能力，避免仅修改资源文件就重新打包 module。

### 项目级配置内容

- **强制 · 主题**：`*Properties` 已提供默认值且配置文件未改变该值时，配置文件不得重复写出该配置项；配置文件只承载与代码默认值不同的显式决策与外部差异值。
- **强制 · 主题**：配置项不得默认引入环境变量占位符，不得默认要求部署环境提供对应变量；确需注入时由部署配置或专用 profile 承载，且缺失时必须快速失败。

## 层内约定

### api

- **强制 · 主题**：API 以 Facade 为能力中心，只定义接口和稳定契约，不提供业务实现。
- **强制 · 主题**：契约可包含 command、query、response、event、enum 和 constants；有限取值放 `api.enums`，固定 header、topic、event type 放 `api.constants`。
- **强制 · 主题**：Facade 入参必须实现 `Request`，使用状态完整、不可变且与 HTTP 绑定和 Header 回填无关的 command/query `record`；出参使用 `Result<T>` 或分页 `PageResult<T>`，无 payload 使用 `Result<Void>`，非分页集合使用 `Result<List<T>>`。
- **强制 · 主题**：API 集成事件实现 `IntegrationEvent`；可以由领域事件映射，但不得复用领域事件类型。

### domain

- **强制 · 主题**：以聚合根为一致性边界组织实体、值对象、领域服务、Repository 契约和领域事件；聚合根和实体只能通过领域行为改变状态。
- **强制 · 主题**：领域实体的标识必须继承基类 `EntityId`，工程按实际类型提供 `StringEntityId`、`LongEntityId` 等工程级基类，并统一重写 `validate()`，如需额外约束时才再次重写。
- **强制 · 主题**：值对象不可变。
- **强制 · 主题**：领域服务只承载跨聚合或不适合归属单个聚合的领域规则。
- **强制 · 主题**：领域服务返回的 `*Effect` 必须实现 `DomainEffect`，并通过其 `events()` 返回该次领域行为产生的领域事件；没有领域事件时返回空集合，不得返回 `null`。
- **强制 · 主题**：领域对象和服务不得直接读取系统时钟；application 注入 `Clock`，每个用例取得一次业务时间并传入相关状态变化和事件。
- **强制 · 主题**：Repository 只表达领域对象存取契约，不暴露持久化技术。
- **强制 · 主题**：领域行为决定领域事件是否发生及其业务内容。原始领域事件只携带发生时间、事件类型和业务内容，不携带 EventStore 持久化记录 ID，也不依赖 ID 生成端口；EventStore 在封装 `DomainEventEnvelope` 时生成仅用于持久化、发布、追踪和幂等的全局事件 ID。
- **强制 · 主题**：外部能力属于领域模型的一部分并直接服务于领域规则时，由 domain 定义 port；port 契约使用领域语义类型，不得按外部服务协议设计。
- **强制 · 主题**：domain 不得感知 API payload、application command/output/view、外部服务 Payload、HTTP 或第三方 SDK 类型、持久化 DO、具体技术、`Result<T>` 或 `PageResult<T>`。

### application

- **强制 · 主题**：application 编排用例并协调领域模型和端口，不实现领域规则。
- **强制 · 主题**：command service 是写用例和事务边界，接收 application command，返回 command output 或 `void`。
- **强制 · 主题**：query service 只读，接收领域 ID、值对象或 query condition，返回 view，分页使用 `PagedList<T>`。
- **强制 · 主题**：application 的事件发布遵循[分布式消息最佳实践](bp_messaging.md#事件与发布)。
- **强制 · 主题**：外部能力仅用于用例编排、流程协调或查询，不构成领域模型和领域规则时，由 application 定义 port；port 契约使用 application 或 domain 的本地语义类型，不得使用外部服务 Payload、HTTP 或第三方 SDK 类型。
- **强制 · 主题**：application 可以依赖 domain、API 集成事件契约和 framework 端口，不得依赖 API command/query/response、协议实现、持久化 DO、外部服务 Payload、HTTP 或第三方 SDK 类型。

### infrastructure

- **强制 · 主题**：infrastructure 提供 repository、ID、事件存储、消息和调度等技术适配，并实现 domain/application 定义的端口，不承载领域规则或用例编排。
- **强制 · 主题**：领域事件存储必须通过 framework-domain 定义的端口适配；domain 和 application 不得依赖具体的领域事件存储实现。
- **强制 · 主题**：已由运行框架提供的基础设施 Bean 必须注入复用，不得重复声明同语义 Bean。
- **强制 · 主题**：JavaBean 配置绑定中的集合和嵌套对象字段声明为 `final`，只暴露 getter，并初始化为空绑定容器；必填集合使用 `@NotEmpty` 使缺失配置启动失败。
- **强制 · 主题**：`Duration` 独立最小值同时使用 `@NotNull` 和带明确单位的 `@DurationMin`，module 直接依赖 `hibernate-validator`；`@AssertTrue` 等类型级校验只表达字段间关系。
- **强制 · 主题**：persistence、消息和调度适配分别遵循对应主题最佳实践；本层只约束这些能力属于 infrastructure，不在此重复其实现规则。

### interfaces、client 与 boot

- **强制 · 主题**：interfaces 提供协议无关 Facade 实现和协议入口，不承载领域规则或用例编排；Facade 实现负责对象转换、调用 application 和统一响应包装。
- **强制 · 主题**：controller 只处理路由、绑定和协议上下文，将 HTTP Request 转换为 API command/query 后调用 Facade。
- **强制 · 主题**：Client、Channel、Device 等 Header 上下文只在 interfaces 解析；API、application 和 domain 不得依赖 Header 绑定机制。
- **强制 · 主题**：controller 的业务请求收敛为一个普通可变 `@Valid` HTTP Request，并继承 `ClientRequest`。
- **强制 · 主题**：仅在接口确实需要可信渠道或认证会话上下文时，按需实现可组合的 `ChannelContext`、`AuthenticatedSessionContext`。
- **强制 · 主题**：不得把业务字段拆成 path/query 参数再附加独立客户端上下文参数。
- **强制 · 主题**：没有业务 body 的接口声明与所需上下文匹配的具体 Request 类型，由统一参数解析器从受保护 Header 构造并校验。
- **强制 · 主题**：Header 回填和校验后，必须转换成完整不可变 API command/query；Facade 不得接收 interfaces HTTP Request。
- **强制 · 主题**：RPC 能直接暴露 Facade 时发布同一个 Facade Bean；只有协议模型、语义、元数据或异常不兼容时增加技术专属 adapter。
- **强制 · 主题**：消息 listener 属于 interfaces 协议入口，不强制经过 Facade；消费可靠性和处理流程遵循[分布式消息最佳实践](bp_messaging.md#消费与可靠性)。
- **强制 · 主题**：OpenFeign 客户端签名与 Facade 一致，只复用 API 契约和响应包装，不定义业务模型、用例或转换规则。
- **强制 · 主题**：boot 不承载领域规则、应用编排、协议适配或业务类型；技术实现选择遵循[依赖管理最佳实践](bp_dependencies.md#服务技术基线)。

## 不可变数据载体

- **默认 · 主题**：API command/query 优先使用 `record`。
- **强制 · 主题**：API response 使用 `record`。
- **强制 · 主题**：API event 在序列化、RPC、OpenFeign 和客户端支持构造器绑定时使用 `record`；存在无法支持构造器绑定的既有消费端时使用普通 JavaBean 类。
- **强制 · 主题**：公开 Java API 新增 record component 前必须评估构造器二进制兼容性。
- **强制 · 主题**：interfaces HTTP Request 使用普通可变类以支持绑定和上下文回填，但不得作为 Facade 入参。
- **默认 · 主题**：领域 ID、值对象、`*Effect` 和不可变领域事件在无需继承时优先使用 `record`；聚合根、实体、可变状态或复杂行为使用普通类。
- **默认 · 主题**：application 的不可变 command、output、query condition 和 view 优先使用 `record`；service、repository、gateway、mapper 使用普通类。
- **默认 · 主题**：持久化只读 projection 可以使用 `record`；DO、JPA Entity 和需要无参构造器或 setter 映射的对象使用普通类。
