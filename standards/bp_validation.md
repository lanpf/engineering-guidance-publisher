# 校验与异常最佳实践

本文定义校验方式选择、Jakarta Bean Validation、Spring 校验启用、显式检查和异常体系约束。

## Bean Validation

- **默认 · 基础**：在依赖与运行时校验机制均已具备的前提下，可绑定 Bean 属性以及方法参数和返回值的非空、格式与范围约束优先使用 Jakarta Bean Validation。
- **强制 · 基础**：采用 Jakarta Bean Validation 时，必须在对应的字段、属性、record component、方法参数或返回值位置声明约束，并保证调用路径实际触发校验。
- **强制 · 基础**：`@Valid` 只标记嵌套对象的级联校验，本身不构成约束。
- **强制 · 基础**：按约束的 null 语义声明必填要求；`@Valid`、`@Size`、`@Pattern` 不拒绝 null，不得代替非空约束。仅当所选约束未拒绝 null 且契约要求非 null 时，组合 `@NotNull`。
- **强制 · 基础**：容器约束、元素约束与元素级联必须分别按契约声明，不得相互替代；例如 `@NotEmpty List<@NotNull @Valid ItemRequest>` 分别约束容器非空、元素非 null 和元素内部有效性。
- **默认 · 主题**：公开 API 的方法参数和返回值约束优先声明在 API 接口或 API 数据类型上。
- **强制 · 主题**：继承或实现方法的参数约束及参数级联标记必须在上层契约声明；子类型不得新增、重复声明或强化。此限制不适用于返回值约束。
- **强制 · 主题**：Spring MVC 请求对象采用参数级绑定校验时，默认组使用参数上的 `@Valid`，指定组使用 `@Validated(Groups.class)`；不得无差别叠加两者，此选择不适用于普通 Bean 方法校验。
- **强制 · 主题**：Spring MVC 方法直接声明参数或返回值约束时，使用 MVC 内置方法校验，对象内部约束通过 `@Valid` 级联；使用该机制的 Controller 不添加类级 `@Validated`。
- **强制 · 主题**：Facade、application service 等普通 Spring Bean 需要校验方法参数或返回值时，在具体 Bean 实现类上添加 `@Validated`，并确保调用经过 Spring 代理；接口负责声明契约约束，实现类负责启用运行时方法校验。
- **强制 · 主题**：方法校验需要指定组时，普通 Bean 在实现类或方法声明 `@Validated(Groups.class)`，方法声明覆盖类声明；MVC 内置方法校验在 handler 方法上声明。需要级联的对象参数或返回值仍使用 `@Valid`，不得以参数上的 `@Validated` 替代级联标记。

## 显式检查

防御性复制的责任归属与保存边界遵循[Java 最佳实践](bp_java.md#集合所有权与防御性复制)；本节定义校验语义及工具选择。

**失败语义与工具**

- **强制 · 基础**：当 Jakarta Bean Validation 无法表达约束、调用路径不能保证触发校验，或必须返回明确的业务错误语义时，使用显式检查；包括不经过框架绑定链路、需要快速失败的构造函数和工厂方法。
- **强制 · 基础**：按失败语义分类：违反业务契约为业务失败，程序错误或内部技术不变量被破坏为技术失败；不得按代码位置、变量数量、工具或是否继承 `BaseException` 分类。
- **强制 · 基础**：技术失败不得使用业务异常或业务错误码。非法技术参数使用 `IllegalArgumentException`，非法执行状态使用 `IllegalStateException`，其他情况使用匹配语义的技术异常；技术契约明确要求框架错误码时，才使用对应 `FrameworkException`。
- **强制 · 主题**：业务契约失败必须抛出携带稳定业务错误码的对应业务异常，不得用通用 `FrameworkException` 加业务文案替代；业务异常基类遵循[异常与消息](#异常与消息)。
- **强制 · 基础**：业务检查按约束与可读性选择 `Require` 的业务异常供应器重载或显式业务守卫；不得使用默认或字符串重载替代约定的业务异常。
- **强制 · 基础**：普通技术防御按已有依赖选择 Spring `org.springframework.util.Assert` 或统一管理的 `org.apache.commons.lang3.Validate`，且方法必须符合异常语义及 NPE 禁令；已有 Spring 时优先 Assert，Spring 解耦 module 使用 Validate。可用工具不能满足时，才编写显式技术守卫。`Require` 默认或字符串重载抛出 `FrameworkException.illegalArgument`，仅用于技术契约明确要求该框架错误码的参数检查。
- **强制 · 基础**：检查工具的依赖准入遵循[依赖管理最佳实践](bp_dependencies.md#scope-与版本)；不得仅为校验引入 Spring、其他 framework module 或任意新工具库。不得手写已有工具能够满足的等价通用技术检查；此限制不适用于显式业务守卫。

**诊断消息与 null 防御**

- **默认 · 基础**：技术检查优先提供显式诊断消息；使用默认消息须有具体理由，例如统一封装已提供等价上下文。消息偏好不改变异常语义。
- **强制 · 基础**：显式技术诊断消息必须非空白，说明检查对象及违反的约束，不得仅写 `invalid`、`required` 等泛化文案；敏感值保护遵循[日志与敏感数据最佳实践](bp_logging.md#日志与敏感数据)。
- **强制 · 基础**：不得主动抛 NPE 或依赖隐式 NPE 完成校验，禁止用 `Objects.requireNonNull`、`Validate.notNull` 校验。可预见的 null 必须在解引用或调用拒绝 null 的 API 前按契约拒绝或归一化；`Validate.notBlank`、`notEmpty` 等可能对 null 抛 NPE 的方法，只能在已保证非 null 后使用。

**Require 与集合检查**

- **强制 · 主题**：`Require.notNull` 用于业务非空守卫时，必须提供业务异常供应器；不得用于普通技术防御性检查。业务守卫的适用范围不取决于检查的是参数、返回值、局部变量还是字段。
- **强制 · 主题**：`Require.satisfies` 的谓词必须无副作用，只依赖当前 `value`、不可变的 `static final` 常量、类字面量及仅由当前值派生的不可变值；不得捕获其他变量、方法参数、`this` 字段或外部可变状态。null 值直接判定失败。
- **强制 · 主题**：跨变量或依赖外部状态的判断使用显式守卫，不得包装成 `Require.satisfies` 调用；异常分类遵循本节失败语义规则。
- **强制 · 主题**：选择集合检查方法必须区分容器非 null、非空、元素非 null 与唯一性，遵循下表；不得以其中一项代替其他约束。

| 方法 | 检查范围 | 空容器及返回结果 |
| --- | --- | --- |
| `Require.notEmpty` | 容器非 null 且至少有一个元素，不检查元素非 null | 拒绝空容器；返回原容器 |
| `Require.noNulls` | 容器和元素非 null；Map 同时检查 key/value | 允许空容器；返回原容器 |
| `Require.noDuplicates` | 容器、元素非 null，元素不重复 | 允许空容器；返回可变 Set |
| 带 `keyMapper` 的 `noDuplicates` | 容器、元素和映射结果非 null，映射键不重复 | 允许空容器；返回可变 Map |

以上方法的异常供应器覆盖各自的结构校验失败；返回结果不等于已完成不可变防御性复制。

- **强制 · 主题**：技术性元素非空检查必须同时覆盖 Map 的 key/value，失败使用匹配语义的技术异常；不得以技术完整性检查代替业务有效性检查。
- **默认 · 主题**：已依赖 framework-core，且元素或 Map key/value 非空确为业务契约时，优先使用 `Require.noNulls` 的业务异常供应器重载；额外业务约束另行保证。
- **强制 · 主题**：业务要求拒绝重复项时，必须检查唯一性，不得以 Set 转换的静默去重代替。
- **强制 · 主题**：不得假定异常供应器会转换回调异常；`Require` 的谓词、`keyMapper` 及 `NullSafe` 的 consumer 自身抛出的异常原样传播。

**NullSafe 与容器契约**

- **强制 · 主题**：仅当输入允许 null、允许空容器且两者语义等价时，才使用 `NullSafe.visit` 或 `copyTo*`。输入已保证非 null 时直接遍历或复制；不得先校验非 null 再使用 `NullSafe`。
- **强制 · 主题**：`NullSafe` 的异常供应器只处理 null 元素或 Map 的 null key/value，不负责拒绝 null 容器。业务性元素检查必须提供业务异常供应器；默认技术异常仅适用于契约接受框架错误码的场景。
- **默认 · 主题**：已依赖 framework-core，满足本节 NullSafe 适用条件且异常语义匹配时，需要不可变浅拷贝优先使用 `NullSafe.copyTo*`；保留输入迭代顺序时使用 `copyToOrdered*`。方法已检查元素非 null，无需重复调用 `Require.noNulls`；Set 复制会去重。

- **强制 · 主题**：`NullSafe.visit` 必须提供非 null consumer，即使容器为 null 也会先检查 consumer；复制方法允许不提供 consumer。null 容器在 `visit` 中跳过，在复制方法中归一为空容器，不触发元素异常供应器。

- **强制 · 主题**：构造器的集合或 Map 参数默认不允许为 null；允许空容器不代表允许 null。允许 null 的参数必须在构造器 Javadoc 的 `@param` 中明确说明 null 的处理语义；存在条件限制时，必须同时说明适用条件。不得因使用 `NullSafe` 而隐式扩大参数对 null 的接受范围。

**检查责任边界**

- **默认 · 主题**：API 请求的字段形态约束优先使用 Jakarta Bean Validation；只有 API 契约明确承诺业务错误语义时，对应检查才返回该业务错误；检查的执行位置由检查内容决定，不因错误由 API 对外承诺而前移到协议绑定层。
- **强制 · 主题**：依赖领域状态、持久化数据或用例上下文的规则由 application 或 domain 校验，不得前移到协议绑定层。

## 异常与消息

异常分类遵循[显式检查](#显式检查)的失败语义规则。
业务错误的中文模板及稳定性遵循[服务错误码最佳实践](bp_error_codes.md#错误码)。

- **强制 · 基础**：意外出现的 NPE 视为程序缺陷，必须定位并修复，不得统一捕获后伪装成调用方可预期的业务拒绝；统一异常边界可以记录诊断并返回通用系统失败，但不因此改变其缺陷性质。
- **强制 · 基础**：`FrameworkError` 等框架通用技术错误的默认消息、工程自行声明的技术诊断消息和 Bean Validation 提示使用英文；第三方原始异常消息不受此语言约束。
- **强制 · 基础**：调用方以稳定业务错误码判断业务结果，任何异常 message 都不得作为稳定业务协议解析。
- **强制 · 主题**：校验失败在统一边界按来源转换：外部入参违反公开约束，返回约定的参数校验错误；返回值违反服务契约、约束声明错误或校验器配置错误，按服务端缺陷处理，不得包装为调用方参数错误或预期业务拒绝。统一错误契约不要求先捕获并重抛框架异常再生成响应。
- **强制 · 主题**：服务自定义业务异常继承 framework-core 的 `BaseException`，不得直接继承 `RuntimeException` 或其他 JDK 异常类。
- **强制 · 主题**：表达领域规则或领域有效性的守卫抛出对应领域的 `DomainException`，不得使用 `IllegalArgumentException`、`IllegalStateException` 等通用异常替代；领域内部的程序错误或技术性前置条件仍按技术异常处理。
- **强制 · 主题**：每个领域的 `DomainException` 必须提供 `invalidEntityId()` 静态工厂方法，用于领域实体 ID 有效性校验失败；对应 `DOMAIN_ENTITY_ID_INVALID` 的码位仅由[服务错误码最佳实践](bp_error_codes.md#错误码)定义。
- **强制 · 基础**：异常按契约处理、转换或继续传播，不得静默吞掉；日志要求遵循[日志与敏感数据最佳实践](bp_logging.md#日志与敏感数据)。
