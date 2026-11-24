# 服务分层最佳实践

本文定义服务工程的领域文档、module 分层、层内边界和跨层数据约束；`<工程名>` 表示具体服务。服务还必须遵守自身权威领域文档，项目规约只能补充或收紧共享最佳实践。

## 规约体系

- **强制 · 主题**：修改分层、领域边界或 API 业务语义前，必须按[项目文档最佳实践](bp_docs.md#必备文档)读取项目入口路由的权威文档；项目规则可以补充或收紧共享规则，不得重复、放宽或覆盖。 <!-- SERVICE-DOMAIN-DOC-002 -->

## 分层结构

### 模块职责

- **强制 · 主题**：`<工程名>-api` 定义稳定的对外 API 契约。 <!-- ARCH-MODULE-API-001 -->
- **强制 · 主题**：`<工程名>-domain` 承载核心领域模型和领域规则。 <!-- ARCH-MODULE-DOMAIN-001 -->
- **强制 · 主题**：`<工程名>-application` 编排写用例和只读查询。 <!-- ARCH-MODULE-APPLICATION-001 -->
- **强制 · 主题**：`<工程名>-infrastructure` 提供技术适配、持久化抽象和与具体技术栈无关的通用转换，不得放置具体持久化技术的 DO 及其转换 Mapper。 <!-- ARCH-MODULE-INFRA-001 -->
- **强制 · 主题**：具体持久化、调度和消息实现分别放在 `<工程名>-infrastructure-persistence-<技术>`、`<工程名>-infrastructure-scheduler-<技术>`、`<工程名>-infrastructure-message-<技术>`。 <!-- ARCH-MODULE-TECH-001 -->
- **强制 · 主题**：持久化实现 module 承载该技术栈的 DO、DO 转换 Mapper、repository，以及 SQL/XML 的加载、装配与验证职责；SQL/XML 文件的物理存放位置遵循本文“项目级配置目录”。 <!-- ARCH-MODULE-TECH-002 -->
- **强制 · 主题**：`<工程名>-interfaces` 提供协议无关 Facade 实现及 REST、RPC、消息订阅等协议入口。 <!-- ARCH-MODULE-INTERFACES-001 -->
- **强制 · 主题**：`<工程名>-openfeign-client` 提供调用本服务的 OpenFeign 客户端。 <!-- ARCH-MODULE-CLIENT-001 -->
- **强制 · 主题**：`<工程名>-boot` 只负责启动、运行时配置和打包。 <!-- ARCH-MODULE-BOOT-001 -->
- **强制 · 主题**：`<工程名>-integration-tests` 是独立测试 module，承载多个 module 的真实实现协作、完整自动装配以及依赖真实数据库或中间件的集成测试；仅引用其他 module 的接口或 DTO 不因此构成集成测试；生产 module 不得依赖它。 <!-- ARCH-MODULE-INTEGRATION-TESTS-001 -->

### 包结构

- **强制 · 主题**：顶层包必须与所属 module 的职责一致，例如 `api`、`domain`、`application`、`infrastructure`、`interfaces`；不得在 module 根包下直接混放不同层或不同技术适配的生产类。 <!-- PACKAGE-LAYER-001 -->
- **强制 · 主题**：包之间的依赖方向必须与[服务分层最佳实践](bp_layered_service.md#依赖方向)一致；包拆分不得绕过 module 依赖约束，也不得用跨包访问、反射或事件隐藏反向依赖。 <!-- PACKAGE-DIRECTION-001 -->
- **默认 · 主题**：同一层内按业务能力或技术适配分组（feature-first），再按需要细分 `api`、`service`、`repository`、`mapper` 等角色；不要默认按全局类名分类建立孤立的 `entity`、`service`、`repository` 包。 <!-- PACKAGE-FEATURE-001 -->
- **强制 · 主题**：`infrastructure` module 的顶层包必须继续按能力或适配边界分包，例如 `persistence`、`messaging`、`locking`、`external`、`configuration`；不得将所有 adapter、DO、mapper、configuration 和 client 直接放在同一个 `infra` 包中。 <!-- PACKAGE-INFRA-001 -->
- **强制 · 主题**：具体技术 module 先按技术栈分组，再按聚合、资源或外部服务分组；同一能力的 DO、技术 repository、转换 mapper 和装配可以放在同一 feature package 或其角色子包内，但不得跨技术栈共享具体 DO 或技术注解。 <!-- PACKAGE-TECH-001 -->
- **强制 · 主题**：跨能力复用必须通过稳定的 port、契约或明确的公共组件完成；不得通过访问另一个 feature package 的实现类、数据库 DO 或 mapper 建立隐式耦合。 <!-- PACKAGE-CROSS-CAPABILITY-001 -->
- **默认 · 主题**：只有在包内类型形成清晰的职责闭包后才继续细分；单个类型不应为了目录整齐单独建立一层包，包过大时应按能力或变化原因拆分，而不是机械按类名拆分。 <!-- PACKAGE-GRANULARITY-001 -->
- **强制 · 主题**：包内实现默认使用 package-private；只有跨包、跨 module 或框架装配需要的类型才声明为 `public`，公开类型必须有明确契约或适配职责。 <!-- PACKAGE-VISIBILITY-001 -->
- **默认 · 主题**：测试包路径默认镜像生产包路径。 <!-- PACKAGE-TEST-MIRROR-001 -->
- **强制 · 主题**：测试辅助类只在测试源集或测试支持包中提供，不得进入生产包或被生产代码依赖。 <!-- PACKAGE-TEST-ISOLATION-001 -->

### 依赖方向

- **强制 · 主题**：api 不依赖业务实现。 <!-- ARCH-DEP-API-CONTRACT-001 -->
- **强制 · 主题**：domain 不依赖其他业务层。 <!-- ARCH-DEP-DOMAIN-001 -->
- **强制 · 主题**：application 依赖 domain；允许的额外契约依赖遵循本文 application 约定。 <!-- ARCH-DEP-APPLICATION-001 -->
- **强制 · 主题**：infrastructure 实现 domain/application 定义的端口，具体技术实现 module 依赖 infrastructure。 <!-- ARCH-DEP-INFRA-001 -->
- **强制 · 主题**：interfaces 依赖 api/application。 <!-- ARCH-DEP-INTERFACES-001 -->
- **强制 · 主题**：openfeign-client 依赖 api。 <!-- ARCH-DEP-CLIENT-001 -->
- **强制 · 主题**：boot 依赖运行时装配所需的 module，只负责最终装配。 <!-- ARCH-DEP-BOOT-001 -->
- **强制 · 主题**：integration-tests 可以用 test scope 依赖 boot 和被观测的服务 module；该依赖只用于验证，不得形成生产代码依赖方向的一部分。 <!-- ARCH-DEP-INTEGRATION-TESTS-001 -->
- **强制 · 主题**：内层 module 不得反向依赖外层协议、持久化实现、持久化对象或 boot。 <!-- ARCH-DEP-INWARD-001 -->

### 项目级配置目录

- **默认 · 主题**：存在独立部署的外置配置时，默认在工程根目录使用 config/ 集中维护。 <!-- ARCH-PROJECT-CONFIG-001 -->
- **默认 · 主题**：按修改责任、生效时间与回滚单元决定资源位置。环境地址和运维参数优先外置，凭据通过部署环境的秘密管理机制注入。 <!-- ARCH-PROJECT-CONFIG-003 -->
- **强制 · 主题**：不得仅因某个 module 负责装配就把可独立更新的配置资源打入其制品。 <!-- ARCH-PROJECT-CONFIG-PACKAGING-001 -->
- **强制 · 主题**：外置 SQL、映射文件、schema 和其他配置资源仍须与应用版本建立对应关系，并在部署前验证兼容性；可独立更新不意味着可脱离代码版本管理。 <!-- ARCH-PROJECT-CONFIG-COMPAT-001 -->
- **强制 · 主题**：使用外置 config/ 时，boot 必须通过 Spring 配置位置、框架专属配置或等效启动参数显式加载所需资源。 <!-- ARCH-CONFIG-LOAD-001 -->
- **强制 · 主题**：构建、部署和本地启动流程必须提供所需外置资源，并验证缺失或无效配置能够按预期失败。 <!-- ARCH-CONFIG-VERIFY-001 -->
- **强制 · 主题**：与代码一同演进和回滚的 mapper XML、schema 或迁移脚本可随 module 资源或版本化迁移制品交付。框架要求类路径加载或部署要求自包含时也可随制品交付。 <!-- ARCH-CONFIG-CLASSPATH-EXCEPTION-001 -->

### 项目级配置内容

- **强制 · 主题**：`*Properties` 已提供默认值且配置文件未改变该值时，配置文件不得重复写出该配置项；配置文件只承载与代码默认值不同的显式决策与外部差异值。 <!-- CONFIG-DEFAULT-001 -->
- **强制 · 主题**：配置项不得默认引入环境变量占位符，不得默认要求部署环境提供对应变量；确需注入时由部署配置或专用 profile 承载，且缺失时必须快速失败。 <!-- CONFIG-PLACEHOLDER-001 -->

## 职责内聚与边界检查

- **强制 · 主题**：必须依据项目权威职责与领域文档、逻辑所表达的业务语义判定归属，不得仅按类名、包名、注解或条件分支数量判定分层。协议解析、序列化、连接管理及不改变业务语义的技术重试属于适配行为；Gateway 的协议认证和路由执行也须按实际语义区分技术执行与业务决策，不得一概迁入 domain/application。 <!-- ARCH-SEMANTIC-OWNERSHIP-001 -->
- **强制 · 主题**：检查领域职责时必须定位资格判定、业务不变量、状态转换及业务决策的实际执行位置；同一规则应内聚于负责该语义的领域模型或领域服务，由各入口复用，不得在 controller、filter、listener、adapter 或 application 中各自维护业务判定。协议格式校验与领域有效性校验必须区分，具体校验边界遵循[校验与异常最佳实践](bp_validation.md)。 <!-- ARCH-DOMAIN-COHESION-001 -->
- **强制 · 主题**：检查应用职责时必须沿用例调用链定位业务步骤顺序、多个领域能力或端口的协调、业务结果分支及业务补偿决策；这些编排必须归属 application。适配器内部为完成一次技术操作而进行的 SDK 调用、分页拉取或技术重试不因包含多个步骤就视为应用编排；独立的基础设施恢复流程遵循[业务补偿最佳实践](bp_compensation.md)。 <!-- ARCH-ORCHESTRATION-COHESION-001 -->
- **强制 · 主题**：不得以已存在 domain/application module 或已通过中间 service 转发作为职责内聚的证据；必须追踪到实际作出业务决策及编排的实现。迁移职责时必须迁移相应决策和行为验证，不能仅移动类、改包名或增加转发层而保留外层原有业务逻辑。 <!-- ARCH-SUBSTANTIVE-LAYERING-001 -->
- **强制 · 主题**：依赖方向检查必须同时覆盖 POM 中实际声明或继承的依赖与源码中的 import、全限定类型引用、方法签名、继承/实现关系及注入类型；沿相关调用链检查隐式反向依赖。必须按本文“依赖方向”和“层内约定”的允许范围判定，不能仅凭编译成功、没有循环依赖或接口抽象就认定分层正确。 <!-- ARCH-DEPENDENCY-AUDIT-001 -->

## 层内约定

### api

- **强制 · 主题**：API 以 Facade 为能力中心，只定义接口和稳定契约，不提供业务实现。 <!-- API-RESPONSIBILITY-001 -->
- **强制 · 主题**：契约可包含 command、query、response、event、enum 和 constants；有限取值放 `api.enums`，固定 header、topic、event type 放 `api.constants`。 <!-- API-CONTENTS-001 -->
- **强制 · 主题**：Facade 入参必须实现 `Request`，使用状态完整、不可变且与 HTTP 绑定和 Header 回填无关的 API command/query `record`。 <!-- API-FACADE-INPUT-001 -->
- **强制 · 主题**：Facade 出参使用 `Result<T>` 或分页 `PageResult<T>`；无 payload 使用 `Result<Void>`，非分页集合使用 `Result<List<T>>`。 <!-- API-FACADE-OUTPUT-001 -->
- **强制 · 主题**：API 集成事件实现 `IntegrationEvent`；可以由领域事件映射，但不得复用领域事件类型。 <!-- API-EVENT-001 -->

### domain

- **强制 · 主题**：以聚合根为一致性边界组织实体、值对象、领域服务、Repository 契约和领域事件。 <!-- DOMAIN-MODEL-001 -->
- **强制 · 主题**：聚合根和实体只能通过领域行为改变状态。 <!-- DOMAIN-STATE-CHANGE-001 -->
- **强制 · 主题**：领域实体的标识必须继承基类 `EntityId`，工程按实际类型提供 `StringEntityId`、`LongEntityId` 等工程级基类，并统一重写 `validate()`，如需额外约束时才再次重写。 <!-- DOMAIN-ENTITY-ID-001 -->
- **强制 · 主题**：值对象不可变。 <!-- DOMAIN-VALUE-IMMUTABILITY-001 -->
- **强制 · 主题**：领域服务只承载跨聚合或不适合归属单个聚合的领域规则。 <!-- DOMAIN-SERVICE-SCOPE-001 -->
- **强制 · 主题**：领域服务返回的 `*Effect` 必须实现 `DomainEffect`，并通过其 `events()` 返回该次领域行为产生的领域事件；没有领域事件时返回空集合，不得返回 `null`。 <!-- NAME-DOMAIN-EFFECT-001 -->
- **强制 · 主题**：领域对象和服务不得直接读取系统时钟；application 注入 `Clock`，每个用例取得一次业务时间并传入相关状态变化和事件。 <!-- DOMAIN-CLOCK-001 -->
- **强制 · 主题**：Repository 只表达领域对象存取契约，不暴露持久化技术。 <!-- DOMAIN-REPOSITORY-001 -->
- **强制 · 主题**：领域行为决定领域事件是否发生及其业务内容；原始领域事件只携带发生时间、事件类型和业务内容，不携带 EventStore 持久化记录 ID，也不依赖 ID 生成端口。 <!-- DOMAIN-RAW-EVENT-001 -->
- **强制 · 主题**：EventStore 在封装 `DomainEventEnvelope` 时生成仅用于持久化、发布、追踪和幂等的全局事件 ID。 <!-- DOMAIN-EVENT-ENVELOPE-ID-001 -->
- **强制 · 主题**：外部能力属于领域模型的一部分并直接服务于领域规则时，由 domain 定义 port；port 契约使用领域语义类型，不得按外部服务协议设计。 <!-- DOMAIN-PORT-OWNERSHIP-001 -->
- **强制 · 主题**：domain 不得感知 API payload、application command/output/view、外部服务 Payload、HTTP 或第三方 SDK 类型、持久化 DO、具体技术、`Result<T>` 或 `PageResult<T>`。 <!-- DOMAIN-BOUNDARY-001 -->

### application

- **强制 · 主题**：application 编排用例并协调领域模型和端口，不实现领域规则。 <!-- APPLICATION-RESPONSIBILITY-001 -->
- **强制 · 主题**：command service 是写用例和事务边界，接收 application command，返回 command output 或 `void`。 <!-- APPLICATION-COMMAND-001 -->
- **强制 · 主题**：query service 只读，接收领域 ID、值对象或 query condition，返回 view，分页使用 `PagedList<T>`。 <!-- APPLICATION-QUERY-001 -->
application 的事件发布遵循[分布式消息最佳实践](bp_messaging.md#事件与发布)。
- **强制 · 主题**：外部能力仅用于用例编排、流程协调或查询，不构成领域模型和领域规则时，由 application 定义 port；port 契约使用 application 或 domain 的本地语义类型，不得使用外部服务 Payload、HTTP 或第三方 SDK 类型。 <!-- APPLICATION-PORT-OWNERSHIP-001 -->
- **强制 · 主题**：application 可以依赖 domain、API 集成事件契约和 framework 端口，不得依赖 API command/query/response、协议实现、持久化 DO、外部服务 Payload、HTTP 或第三方 SDK 类型。 <!-- APPLICATION-BOUNDARY-001 -->

### infrastructure

- **强制 · 主题**：infrastructure 提供 repository、ID、事件存储、消息和调度等技术适配，并实现 domain/application 定义的端口，不承载领域规则或用例编排。 <!-- INFRA-RESPONSIBILITY-001 -->
- **强制 · 主题**：领域事件存储必须通过 framework-domain 定义的端口适配；domain 和 application 不得依赖具体的领域事件存储实现。 <!-- INFRA-EVENTSTORE-PORT-001 -->
- **强制 · 主题**：已由运行框架提供的基础设施 Bean 必须注入复用，不得重复声明同语义 Bean。 <!-- DEP-BEAN-001 -->
- **强制 · 主题**：JavaBean 配置绑定中的集合和嵌套对象字段声明为 `final`，只暴露 getter，并初始化为空绑定容器。 <!-- INFRA-CONFIG-001 -->
- **强制 · 主题**：必填配置集合使用 `@NotEmpty`，使缺失配置启动失败。 <!-- INFRA-CONFIG-002 -->
- **强制 · 主题**：`Duration` 的独立最小值校验同时使用 `@NotNull` 和带明确单位的 `@DurationMin`。 <!-- INFRA-DURATION-VALIDATION-001 -->
- **强制 · 主题**：使用 `@DurationMin` 的 module 直接依赖 `hibernate-validator`。 <!-- INFRA-DURATION-DEPENDENCY-001 -->
- **强制 · 主题**：`@AssertTrue` 等类型级校验只表达字段间关系，不替代独立字段约束。 <!-- INFRA-CROSS-FIELD-001 -->
persistence、消息和调度适配分别遵循对应主题最佳实践；本层只约束这些能力属于 infrastructure，不在此重复其实现规则。

### interfaces、client 与 boot

- **强制 · 主题**：interfaces 提供协议无关 Facade 实现和协议入口，不承载领域规则或用例编排。 <!-- INTERFACES-RESPONSIBILITY-001 -->
- **强制 · 主题**：Facade 实现负责对象转换、调用 application 和统一响应包装。 <!-- INTERFACES-FACADE-001 -->
- **强制 · 主题**：controller 只处理路由、绑定和协议上下文，将 HTTP Request 转换为 API command/query 后调用 Facade。 <!-- INTERFACES-REST-001 -->
- **强制 · 主题**：Client、Channel、Device 等 Header 上下文只在 interfaces 解析；API、application 和 domain 不得依赖 Header 绑定机制。 <!-- INTERFACES-HEADER-CONTEXT-001 -->
- **强制 · 主题**：controller 的业务请求收敛为一个启用校验的普通可变 HTTP Request，并继承 `ClientRequest`；校验方式遵循[校验与异常最佳实践](bp_validation.md#Bean-Validation)。 <!-- INTERFACES-REST-CONTEXT-001 -->
- **强制 · 主题**：仅在接口确实需要可信渠道或认证会话上下文时，按需实现可组合的 `ChannelContext`、`AuthenticatedSessionContext`。 <!-- INTERFACES-REST-CONTEXT-002 -->
- **强制 · 主题**：不得把业务字段拆成 path/query 参数再附加独立客户端上下文参数。没有业务 body 的接口声明与所需上下文匹配的具体 Request 类型，由统一参数解析器从受保护 Header 构造并校验。 <!-- INTERFACES-REST-CONTEXT-003 -->

- **强制 · 主题**：Header 回填和校验后，必须转换成完整不可变 API command/query；Facade 不得接收 interfaces HTTP Request。 <!-- INTERFACES-FACADE-BOUNDARY-001 -->
- **强制 · 主题**：RPC 能直接暴露 Facade 时发布同一个 Facade Bean；只有协议模型、语义、元数据或异常不兼容时增加技术专属 adapter。 <!-- INTERFACES-RPC-001 -->
- **强制 · 主题**：消息 listener 属于 interfaces 协议入口，不强制经过 Facade；消费可靠性和处理流程遵循[分布式消息最佳实践](bp_messaging.md#消费与可靠性)。 <!-- INTERFACES-MESSAGE-001 -->
- **强制 · 主题**：OpenFeign 客户端签名与 Facade 一致，只复用 API 契约和响应包装，不定义业务模型、用例或转换规则。 <!-- CLIENT-FEIGN-001 -->
- **强制 · 主题**：boot 负责启动、运行配置和打包。技术实现选择遵循[依赖管理最佳实践](bp_dependencies.md#服务技术基线)。 <!-- BOOT-RESPONSIBILITY-001 -->
- **强制 · 主题**：boot 不承载领域规则、应用编排、协议适配或业务类型。 <!-- BOOT-BOUNDARY-001 -->

## 不可变数据载体

集合状态的保存边界、副本可变性及元素隔离遵循[Java 最佳实践](bp_java.md#集合所有权与防御性复制)；本文只规定各层的数据载体选择。

- **强制 · 主题**：API response 使用 `record`。 <!-- API-RESPONSE-001 -->
- **强制 · 主题**：API event 在序列化、RPC、OpenFeign 和客户端支持构造器绑定时使用 `record`；存在无法支持构造器绑定的既有消费端时使用普通 JavaBean 类。 <!-- DATA-API-EVENT-001 -->
- **强制 · 主题**：公开 Java API 新增 record component 前必须评估构造器二进制兼容性。 <!-- DATA-API-COMPAT-001 -->
- **强制 · 主题**：interfaces HTTP Request 使用普通可变类以支持绑定和上下文回填，但不得作为 Facade 入参。 <!-- DATA-INTERFACES-001 -->
- **默认 · 主题**：领域 ID、值对象、`*Effect` 和不可变领域事件在无需继承时优先使用 `record`。 <!-- DATA-DOMAIN-RECORD-001 -->
- **强制 · 主题**：聚合根、实体、可变状态或复杂行为使用普通类，具体条件遵循[Java 最佳实践](bp_java.md#java-语言)。 <!-- DATA-DOMAIN-CLASS-001 -->
- **默认 · 主题**：application 的不可变 command、output、query condition 和 view 优先使用 `record`。 <!-- DATA-APPLICATION-RECORD-001 -->
- **强制 · 主题**：service、repository、gateway、mapper 使用普通类或对应接口，不使用 `record`。 <!-- DATA-APPLICATION-COMPONENT-001 -->
- **默认 · 主题**：持久化只读 projection 可以使用 `record`。 <!-- DATA-PERSISTENCE-PROJECTION-001 -->
- **强制 · 主题**：DO、JPA Entity 和需要无参构造器或 setter 映射的对象使用普通类。 <!-- DATA-PERSISTENCE-DO-001 -->
