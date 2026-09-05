# 校验与异常最佳实践

本文定义 Jakarta Bean Validation、Spring 校验启用、显式前置条件、业务守卫和异常体系约束。

## Bean Validation

- **默认 · 基础**：可绑定 Bean 属性以及方法参数和返回值的非空、格式与范围约束优先使用 Jakarta Bean Validation，并声明在所属字段、属性或 record component 上。
- **强制 · 基础**：`@Valid` 只标记嵌套对象的级联校验，本身不构成约束。
- **强制 · 主题**：请求对象入口使用默认校验组时使用 `@Valid`，需要指定校验组时使用 `@Validated`，不得在同一入口无差别叠加两者。
- **默认 · 主题**：公开 API 的方法参数和返回值约束优先声明在 API 接口或 API 数据类型上。
- **强制 · 主题**：具体实现不得重复声明或强化 API 接口参数约束。
- **强制 · 主题**：Spring MVC 请求对象通过入口参数上的 `@Valid` 触发对象校验，需要分组时使用 `@Validated`；方法参数直接声明 `@NotBlank`、`@Min` 等约束时由 Spring MVC 方法校验处理，不得仅为启用方法校验统一给 Controller 添加类级 `@Validated`。
- **强制 · 主题**：Facade、application service 等普通 Spring Bean 需要校验方法参数或返回值时，在具体 Bean 实现类上添加 `@Validated`，并确保调用经过 Spring 代理；接口负责声明契约约束，实现类负责启用运行时方法校验。

## 显式检查

- **强制 · 基础**：仅在 Bean Validation 无法表达约束，或领域对象构造函数、工厂方法等不经过框架绑定链路的内部 API 需要快速失败时，才使用显式检查。
- **强制 · 基础**：技术性前置条件用于发现程序错误或保护内部不变量，不构成稳定业务协议；其异常 message 只用于诊断，调用方不得依赖 message 文本判断业务结果。
- **默认 · 基础**：技术性前置条件只检查非空时优先使用 JDK `Objects.requireNonNull`。
- **强制 · 基础**：技术性前置条件需要检查非空白、范围、集合或任意条件时，已因自身职责依赖 Spring Framework 的 module 使用 `org.springframework.util.Assert`，与 Spring 解耦的 module 使用工程统一管理的 `org.apache.commons.lang3.Validate`。
- **强制 · 主题**：业务规则守卫用于表达调用方可预期且需要稳定错误码的业务拒绝，统一使用 framework-core 的 `Require`，并显式提供继承自 `BaseException` 的异常；不得使用 `Objects.requireNonNull`、`Validate` 或 `Assert` 代替业务异常，也不得为了普通技术性前置条件滥用 `Require`。
- **默认 · 主题**：API 请求的字段形态约束优先使用 Jakarta Bean Validation；只有失败语义属于 API 明确承诺的业务错误时，API 层才使用 `Require`。
- **强制 · 主题**：依赖领域状态、持久化数据或用例上下文的规则由 application 或 domain 校验，不得前移到协议绑定层。
- **强制 · 基础**：不得仅为显式检查引入 Spring Framework，也不得手写上述工具已提供的等价逻辑；工具依赖选择遵循[通用工具最佳实践](bp_common_tools.md#基础工具类)。

## 异常与消息

- **强制 · 基础**：Jakarta Bean Validation 和技术前置条件的诊断 message 使用英文，不得作为稳定业务协议。
具有稳定错误码的业务异常使用[服务错误码最佳实践](bp_error_codes.md#错误码)定义的中文模板；调用方不得解析异常 message 判断业务结果的约束由上文技术前置条件和错误码契约共同保证。
- **强制 · 主题**：Jakarta Bean Validation 校验失败时使用框架异常体系；服务自定义业务异常继承 framework-core 的 `BaseException`，不得直接继承 `RuntimeException` 或其他 JDK 异常类。
- **强制 · 主题**：领域层守卫逻辑抛出继承自 `BaseException` 的 `DomainException`，不得使用 `IllegalArgumentException`、`IllegalStateException` 等通用异常替代。
- **强制 · 主题**：`DomainException` 提供 `invalidEntityId()` 和 `missingField()` 静态工厂方法。
- **强制 · 基础**：业务异常必须处理或继续抛出；不得静默忽略异常。非业务异常的日志要求遵循[日志与敏感数据最佳实践](bp_logging.md#日志与敏感数据)。
