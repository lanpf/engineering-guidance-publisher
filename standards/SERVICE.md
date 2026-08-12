# 服务级工程规约

本文继承本地 [通用工程规约](COMMON.md)，定义所有服务工程共同遵守的技术基线、模块分层、层内边界和命名约定；`<工程名>` 表示具体服务工程。服务还必须遵守自身的 `DOMAIN.md`：服务级规约定义工程结构与协作边界，领域设计定义当前服务的业务模型与语义。

## 规约体系

- 每个服务必须在工程根目录维护 `DOMAIN.md`，定义当前服务的领域边界、领域语言、业务规则、错误定义、领域事件和 API 语义。

## 技术基线

### 服务框架

- 服务基于 Spring Boot `3.5.16` 和 Spring Cloud `2025.0.3`。
- 服务通过 `framework-dependencies`、`framework-bom` 和 `framework-starter-bom` 统一依赖版本，并按需使用 `framework-*` 契约与 `framework-starter-*` 实现。

### 依赖管理

- 每个 module 只声明当前职责所需的最小依赖；domain、application 等技术中立 module 只依赖最小 framework 契约。
- 只有具体技术实现、运行时适配和最终打包装配 module 可以引入对应的聚合型 starter。

### 技术装配

- 持久化、消息、调度等可替换技术使用独立 module，由 boot 的打包依赖决定运行时实现；不通过服务运行时属性在同一制品内切换多套技术实现。
- 分布式定时任务默认使用 XXL-JOB，只承载兜底、补偿和批处理等辅助能力，不作为核心业务实时链路的前置依赖。

## 分层结构

### 模块职责

`<工程名>` 使用以下分层 module，顺序同时表示本文约定各层时采用的固定顺序：

- `<工程名>-api`：对外契约层，定义稳定 API 契约。
- `<工程名>-domain`：领域层，承载核心领域模型和领域规则。
- `<工程名>-application`：应用层，编排写用例和只读查询。
- `<工程名>-infrastructure`：基础设施层，提供技术适配、持久化抽象、通用转换和持久化对象。
- `<工程名>-infrastructure-persistence-<技术>`：持久化实现 module，承载具体 repository 实现、SQL XML 和技术装配。
- `<工程名>-infrastructure-scheduler-<技术>`：可选调度实现 module，承载具体调度框架适配和任务入口。
- `<工程名>-infrastructure-message-<技术>`：可选消息实现 module，承载具体消息中间件的出站适配。
- `<工程名>-interfaces`：接口适配层，提供 Facade API 的协议无关实现，并承接 REST、RPC 和消息订阅等外部协议。
- `<工程名>-openfeign-client`：客户端适配层，提供调用本服务的 OpenFeign 客户端。
- `<工程名>-boot`：启动 module，负责应用启动、运行时配置和打包依赖装配。

### 依赖方向

- `api` 不依赖业务实现，`domain` 不依赖其他业务层，`application` 依赖 `domain`。
- `infrastructure` 实现 domain/application 定义的端口；具体 persistence、scheduler 和 message module 依赖 `infrastructure`。
- `interfaces` 依赖 api/application，`openfeign-client` 依赖 api，`boot` 只负责最终装配。
- 任何内层 module 都不得反向依赖外层协议、持久化对象或启动 module。

## 层内约定

### api

- **职责**：定义对外稳定契约，以 Facade 为能力中心，只声明接口及其契约，不提供业务实现。
- **契约组成**：包含 command、query、response、event、enum 和 constants；`api.enums` 表达有限取值集合，`api.constants` 表达 header、topic、event type 等固定值。
- **Facade 方法**：入参必须实现 `Request`，并使用状态完整、不可变、与 HTTP 绑定及 Header 回填机制无关的 API command/query `record`；出参必须由 `BaseResult` 实现类包装，分页集合使用 `PageResult<T>`，其他结果使用 `Result<T>`。`T` 为 API response `record`，无 payload 使用 `Result<Void>`，非分页集合使用 `Result<List<T>>`。
- **集成事件**：`api.event` 定义服务间集成事件并实现 `IntegrationEvent`；可以由领域事件映射生成，但不得直接复用领域事件类型。

### domain

- **职责**：以聚合根为一致性边界，定义聚合根、实体、值对象、领域服务、Repository 契约和领域事件。
- **模型约束**：聚合根与实体只能通过领域行为改变状态；值对象表达不可变业务概念；领域服务只承载跨聚合或不适合归属单个聚合的领域规则。
- **时间来源**：领域对象和领域服务不得直接调用 `Instant.now()`、`LocalDateTime.now()` 等系统时钟。Application 层的用例服务统一注入 `Clock`，在一次用例中取得业务时间并显式传入领域行为；同一业务事实的状态变化和领域事件应复用同一个时间值。
- **Repository**：只表达领域对象存取契约，不暴露具体持久化技术。
- **领域事件**：表示领域内已发生的事实，创建时必须传入趋势递增的 Long 事件 ID；领域事件不等同于 API 集成事件。
- **边界**：不得感知 API payload、application command/output/view、持久化 DO 或具体技术实现，也不得使用 `Result<T>`、`PageResult<T>` 等对外响应包装。

### application

- **职责**：编排业务用例、协调领域模型和端口，不实现领域规则。
- **Command**：command service 是写用例入口，入参为 application command，出参为 command output；无 payload 时可以返回 `void`，并由 command service 承担事务边界。
- **Query**：query service 负责只读查询，不承担写事务；入参使用领域 ID、值对象或 query condition，出参为 application view，分页返回 `PagedList<T>`。
- **集成事件**：通过 `IntegrationEventOutbox` 端口提交，不直接绑定消息中间件。
- **边界**：可以依赖 domain、API 集成事件契约和 framework 端口；不得依赖 API command/query/response、REST/RPC 实现、持久化 DO 或对外响应包装。

### infrastructure

- **职责**：提供 repository adapter、persistence repository、gateway adapter、ID generator、事件存储、消息发送和调度辅助等技术适配；不承载领域规则或应用编排。
- **配置文件绑定**：
  - 采用 Spring Boot 常见的 JavaBean 绑定模式：集合字段和内嵌配置对象字段声明为 `final`，只暴露 getter、不提供 setter；`final` 仅约束字段不被重新赋值，集合本身或内嵌对象各自的属性仍由 Binder 向已有实例填充。
  - 集合字段的初始值只能是空集合，仅作为绑定容器，不得在 Java 代码中预置业务配置项；必填集合使用 `@NotEmpty`，确保配置缺失时启动失败，避免以空集合静默运行。
- **配置文件属性**： 
  - `Duration` 类型的独立最小值必须同时使用 `@NotNull` 和 Hibernate Validator 的 `@DurationMin`，按业务语义明确填写 `days`、`minutes`、`seconds` 等最小单位；使用该扩展注解的 module 必须直接声明 `hibernate-validator` 依赖。
  - `@AssertTrue` 等类型级校验只用于字段间关系约束。
- **Repository adapter**：实现 domain Repository 或 application 端口，负责领域对象与持久化能力之间的适配；persistence repository 只表达数据访问能力。
- **持久化实现**：具体技术拆入 `infrastructure-persistence-<技术>`，其 repository 实现、SQL XML 和技术装配保持内聚。打包时依赖哪个 persistence module，运行时就使用哪个实现。
- **持久化模型**：通用 `persistence.model` 位于 infrastructure；DO 不显式声明表名和列名，只保留实体、主键、枚举映射等必要注解，字段约束和索引由建表 SQL 管理；同一 DO 可以供多种持久化实现复用。
- **对象转换**：mapper 负责 domain、application read model 与 persistence object 之间的转换；通用 helper/converter 不绑定具体持久化技术，只能作为 mapper helper 被引用，不向业务组件开放。
- **查询契约**：持久化查询接口的方法名优先表达查询条件、范围和排序，不绑定具体调用场景。
- **异步辅助**：领域事件存储、integration event outbox 和分区消息遵循 framework 端口与编排；服务只提供所选技术的适配实现。调度 module 只提供任务入口，实际补偿逻辑保留在 infrastructure 通用服务中。

### interfaces

- **职责**：提供 Facade API 的协议无关实现，并承载 REST controller、RPC service 和消息 listener 等协议入口；不承载领域规则或用例编排。
- **Facade 实现**：负责 API/application 对象转换、调用 application，并使用 `Result<T>`、`PageResult<T>` 统一包装响应。
- **REST**：controller 只负责 HTTP 路由、参数绑定和必要的协议上下文提取，通过 Facade API 调用能力。Client、Channel、Device 等来自 HTTP Header 的上下文只允许在 interfaces 层注入或解析，不得将 Header 绑定机制传入 API、application 或 domain。网关统一写入客户端上下文后，controller 的业务请求参数必须收敛为一个普通可变 HTTP Request 类，可按需继承 `ClientRequest`（需要渠道时继承 `ClientChannelRequest`），并统一标注 `@Valid`；不得将业务字段拆成 path/query 参数后再额外声明一个客户端上下文参数。继承 `ClientRequest` 表示 `clientAppId` 必填，继承 `ClientChannelRequest` 表示接口需要渠道且 `channelCode` 必填；无需渠道的接口不得继承 `ClientChannelRequest`。无业务请求体的接口直接声明具体请求上下文类型，由统一参数解析器从受保护 Header 构造并执行 Bean Validation。controller 在完成 Header 回填和校验后，必须将 HTTP Request 转换为状态完整、不可变且与 HTTP 无关的 API command/query `record`，Facade 不接收 interfaces HTTP Request。
- **RPC**：具体技术能够直接暴露 Facade 契约时，通过配置或框架代理发布同一个 Facade Bean；仅当协议模型、调用语义、元数据或异常处理与 Facade 契约不兼容时，才增加技术专属 RPC adapter。
- **消息入口**：listener 按消息契约完成入站转换并调用 application，不强制经过 Facade。
- **边界**：interfaces HTTP Request 与 API command/query 分离，前者服务于 HTTP 绑定和上下文回填，后者服务于稳定 Facade 契约；interfaces 可以依赖 api/application，application/domain 不得反向依赖 interfaces 或协议对象。

### openfeign-client

- **职责**：供其他服务调用本服务 API，方法签名必须与 API Facade 契约一致。
- **复用边界**：复用 API command/query/payload 及 `Result<T>`、`PageResult<T>`，只依赖 api 和必要的 OpenFeign/Spring Cloud 客户端能力。
- **禁止事项**：不定义业务模型、应用用例或对象转换规则。

### boot

- **职责**：只负责应用启动、运行时配置、具体技术实现选择和打包依赖装配。
- **装配边界**：未引入相应持久化、消息或调度实现 module 时，运行时不具备该项技术能力。
- **禁止事项**：不承载领域规则、应用编排、协议适配或业务类型。

## 跨层约定

### 不可变数据载体

- 遵循 `COMMON.md` 的 record 通用约定：能够在构造时完整确定状态、构造后不再变化，且不依赖继承、代理或 JavaBean setter 绑定的数据载体优先使用 `record`；集合组件必须进行防御性复制。
- API command 和 query 优先使用 `record`，API response 统一使用 `record`；它们表达状态完整、不可变、与 HTTP 绑定及 Header 注入无关的 Facade 契约。API event 在序列化、RPC、OpenFeign 及客户端兼容性支持不可变构造器绑定时使用 `record`。公开 Java API 还必须评估新增 record component 对构造器二进制兼容性的影响。
- interfaces HTTP Request 使用普通可变类，以支持 JSON 参数绑定以及 Client、Channel、Device 等 Header 上下文回填；可按实际上下文需求继承 `ClientRequest`、`ClientChannelRequest` 等 Client 上下文类型，但不得作为 Facade 入参。
- 领域 ID、值对象、`*Outcome` 和不可变领域事件不依赖继承时优先使用 `record`；聚合根、实体、需要继承框架基类、持续改变状态或承载复杂领域行为的类型使用普通类。
- Application command、command output、query condition 和 view 属于不可变数据载体时优先使用 `record`；Service、Repository、Gateway 和 Mapper 使用普通类。
- 持久化只读 projection 可以使用 `record`；DO、JPA Entity 及依赖无参构造器或 setter 映射的对象使用普通类。

### 错误码

错误码固定为 6 位，由 3 位工程前缀和 3 位本地码组成；错误枚举只声明本地码，框架负责生成完整错误码。一个服务工程对应一个限界上下文并使用唯一工程前缀；子域拆分为独立限界上下文或服务工程时，必须分别分配工程前缀。

本地码按层统一分配：

- `000-099`：`ApplicationError`，名称统一使用 `APP_` 前缀。
- `100-799`：`DomainError`。`100-199` 固定为 DOMAIN 公共错误；`200-799` 按连续 100 个码位为领域聚合分段。未分配的完整码段为领域聚合预留，已分配码段内的剩余码位仍归所属聚合，不得挪用。
- `800-899`：`InfrastructureError`，名称统一使用 `INFRA_` 前缀。
- `900-999`：工程预留，暂不分配。

DOMAIN 公共错误统一使用 `DOMAIN_` 前缀，前两个错误固定为 `DOMAIN_ENTITY_ID_INVALID`、`DOMAIN_EVENT_ID_REQUIRED`。聚合错误使用聚合名称作为前缀，每个聚合的前两个错误固定为 `{聚合名称}_NOT_FOUND`、`{聚合名称}_ALREADY_EXISTS`。服务必须在 `DOMAIN.md` 中声明工程前缀、DOMAIN 公共错误码段及各聚合对应的具体码段。

新增错误在所属码段内按本地码顺序追加；已发布的错误码不得修改、复用或分配给其他语义。

## 命名约定

### 通用命名

- 接口直接按业务角色、端口或技术契约命名，不使用 `I*`、`*Interface`；抽象类使用 `Abstract*`，`Base*` 仅用于框架基础类型或通用父类型。
- 实现类不使用笼统的 `*Impl`，使用默认实现、技术、适配角色或实现策略命名。
- 各层 payload、command output、view 和 outcome 不使用 `*Result` 后缀，避免与 framework 响应 `Result<T>`、`PageResult<T>` 混淆。
- 转换器契约按层级职责命名，例如 `ApplicationMapper`、`ApiMapper`；MapStruct 实现放在契约包的 `mapstruct` 子包，统一使用 `*MapStructMapper`。

### api

- `api.command` 入参使用 `*ApiCommand`，返回 payload 使用 `*ApiCommandResponse`。
- `api.query` 入参使用 `*ApiQuery`，返回 payload 使用 `*ApiQueryResponse`。
- `api.enums` 使用 `*ApiEnum`，`api.constants` 使用 `*ApiConstants`，`api.event` 使用 `*ApiEvent`。
- Facade API 接口使用 `*Facade`。

### domain

- 领域服务返回使用 `*Outcome`。
- Repository 契约使用 `*Repository`，领域事件使用 `*Event`。

### application

- `application.command` 入参使用 `*Command`，返回使用 `*CommandOutput`，服务使用 `*CommandService`。
- `application.query` 使用领域 ID、值对象或 query condition 作为入参，返回 `*View`，分页返回 `PagedList<*View>`，服务使用 `*QueryService`。

### infrastructure

- `repository.adapter` 中领域 Repository 适配器使用 `*RepositoryAdapter`。
- `persistence.repository` 放持久化仓储契约；具体实现使用 `*JpaPersistenceRepository`、`*MybatisPersistenceRepository`、`*MybatisPlusPersistenceRepository` 等技术化名称。
- `persistence.mapper` 放持久化转换契约；通用 converter/helper 与 MapStruct 实现放在 mapper 契约所在包，并保持 module 内最小可见性。
- `persistence.model` 中的数据对象使用 `*DO`，持久化装配使用 `*PersistenceConfiguration`，具体实现 module 使用 `<工程名>-infrastructure-persistence-<技术>`。

### interfaces

- Facade 的协议无关默认实现放在 `interfaces.facade`，使用 `Default*Facade`。
- 仅在 Facade 契约不能直接适配具体 RPC 技术时，协议专属实现放在 `interfaces.rpc.<技术>` 并使用 `*RpcAdapter`。

### openfeign-client

- OpenFeign 客户端使用 `*FeignClient`。

### boot

- Boot module 不定义业务类型。
