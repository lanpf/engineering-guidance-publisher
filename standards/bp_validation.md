# 校验与异常最佳实践

本文定义校验方式选择、Jakarta Bean Validation、Spring 校验启用、显式检查和异常体系约束。

## Bean Validation

- **默认 · 基础**：在依赖与运行时校验机制均已具备的前提下，可绑定 Bean 属性以及方法参数和返回值的非空、格式与范围约束优先使用 Jakarta Bean Validation，并声明在对应的字段、属性、record component、方法参数或返回值位置；不能仅添加注解而不保证调用路径实际触发校验。
- **强制 · 基础**：`@Valid` 只标记嵌套对象的级联校验，本身不构成约束。
- **强制 · 主题**：请求对象入口使用默认校验组时使用 `@Valid`，需要指定校验组时使用 `@Validated`，不得在同一入口无差别叠加两者。
- **默认 · 主题**：公开 API 的方法参数和返回值约束优先声明在 API 接口或 API 数据类型上。
- **强制 · 主题**：具体实现不得重复声明或强化 API 接口参数约束。
- **强制 · 主题**：Spring MVC 请求对象通过入口参数上的 `@Valid` 触发对象校验，需要分组时使用 `@Validated`；方法参数直接声明 `@NotBlank`、`@Min` 等约束时由 Spring MVC 方法校验处理，不得仅为启用方法校验统一给 Controller 添加类级 `@Validated`。
- **强制 · 主题**：Facade、application service 等普通 Spring Bean 需要校验方法参数或返回值时，在具体 Bean 实现类上添加 `@Validated`，并确保调用经过 Spring 代理；接口负责声明契约约束，实现类负责启用运行时方法校验。

## 显式检查

- **强制 · 基础**：当 Jakarta Bean Validation 无法表达约束、调用路径不能保证触发校验，或必须返回明确的业务错误语义时，使用显式检查；包括不经过框架绑定链路、需要快速失败的构造函数和工厂方法。
- **强制 · 基础**：技术性前置条件用于发现程序错误或保护内部技术不变量，不得使用服务业务错误码；可以抛出通用技术异常或携带框架通用错误码的 `FrameworkException`。
- **强制 · 主题**：业务条件检查表达调用方可预期的业务拒绝，必须抛出携带稳定业务错误码、继承自 framework-core `BaseException` 的异常；使用 `Require` 的异常供应器重载或显式抛出对应业务异常，不得因工具降级而丢失业务错误语义。普通技术性前置条件不得使用业务异常供应器。
- **强制 · 基础**：显式检查工具必须先满足失败语义，再按已有依赖及能力依次选择 framework-core `Require`、Spring `org.springframework.util.Assert`、工程统一管理的 `org.apache.commons.lang3.Validate`，再使用 JDK（如 `Objects.requireNonNull`）；前一工具不可用或不能满足约束及异常语义时才选择下一项。仅当已有工具和 JDK 均不能满足需求时才允许手写检查。
- **强制 · 基础**：不得仅为显式检查引入新依赖，也不得手写已有可用工具已提供且满足失败语义的等价逻辑；工具依赖选择遵循[通用工具最佳实践](bp_common_tools.md#基础工具类)。
- **默认 · 主题**：依赖 framework-core 的 module，技术性前置条件判断集合元素为 null 或非法时，优先抛出 `FrameworkException` 的 `missingCollectionElement` 或 `invalidCollectionElement`。
- **默认 · 主题**：API 请求的字段形态约束优先使用 Jakarta Bean Validation；只有失败语义属于 API 明确承诺的业务错误时，API 层才进行业务条件检查。
- **强制 · 主题**：依赖领域状态、持久化数据或用例上下文的规则由 application 或 domain 校验，不得前移到协议绑定层。

## 异常与消息

- **强制 · 基础**：异常分类按失败语义判定，不得仅凭是否继承 `BaseException` 判断其为业务异常。服务业务错误使用错误码绑定的中文模板，遵循[服务错误码最佳实践](bp_error_codes.md#错误码)；工程自行声明的技术诊断消息和 Bean Validation 提示使用英文，第三方原始异常消息不受此语言约束。调用方以业务错误码判断业务结果，任何异常 message 都不得作为稳定业务协议解析。
- **强制 · 主题**：Jakarta Bean Validation 校验失败时使用框架异常体系；服务自定义业务异常继承 framework-core 的 `BaseException`，不得直接继承 `RuntimeException` 或其他 JDK 异常类。
- **强制 · 主题**：表达领域规则或领域有效性的守卫抛出继承自 `BaseException` 的 `DomainException`，不得使用 `IllegalArgumentException`、`IllegalStateException` 等通用异常替代；领域内部的程序错误或技术性前置条件按技术异常处理，不得仅因位于 domain 就包装为业务异常。
- **强制 · 主题**：每个领域的 `DomainException` 必须提供 `invalidEntityId()` 静态工厂方法，用于领域实体 ID 有效性校验失败；对应 `DOMAIN_ENTITY_ID_INVALID` 的码位仅由[服务错误码最佳实践](bp_error_codes.md#错误码)定义。
- **强制 · 基础**：业务异常必须处理或继续抛出；不得静默忽略异常。非业务异常的日志要求遵循[日志与敏感数据最佳实践](bp_logging.md#日志与敏感数据)。
