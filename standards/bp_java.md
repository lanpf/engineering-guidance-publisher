# Java 最佳实践

本文定义所有 Java 工程共同遵守的语言、数据设计、校验和异常处理约束。项目内部规约可以补充或收紧这些约束，但不得放宽或覆盖。

## Java 语言

- 使用 Java 17 编译和运行。
- 局部变量的初始化表达式本身已清晰呈现具体类型时可以使用 `var`；如果必须查看被调用方法的声明或依赖泛型推断才能确定变量类型，则不得使用 `var`。
- 能够在构造时完整确定状态、构造后不再变化，且不依赖继承、代理或 JavaBean setter 绑定的数据载体优先使用 `record`；集合组件必须通过 `List.copyOf`、`Set.copyOf` 等方式防御性复制。
- 需要继承、可变状态、框架代理、JavaBean 形态或复杂领域行为时使用普通类。
- 优先使用 `Integer`、`Long`、`Boolean` 等包装类型；仅在明确需要基本类型默认值、性能特性或语义上不允许为空时使用基本类型。
- 简单集合遍历优先使用 `forEach`，简单转换、过滤和映射优先使用 `Stream`，简单回调优先使用 lambda 或方法引用；复杂业务规则、嵌套条件和异常流程以可读性为先。
- 可能缺失的返回值及其链式处理优先使用 `Optional`；不得将 `Optional` 用作 Bean 属性或方法参数。

## 常量与字面量

### 常量

- 取值集合固定且封闭（有限状态、类型枚举）：使用 `enum`。
- 单一常量值需跨类复用：使用 `public static final` 常量或专门的常量类。
- 取值可能因部署环境变化：使用配置项（配置文件/配置中心），允许有默认值。

### 字面量

- 禁止将具有业务语义、可能被多处引用、或用于分支判断/状态标识的字符串字面量直接硬编码在业务代码中，配置文件中的默认值除外。
- 日志文本、非业务诊断的异常提示、单元测试桩数据、正则表达式和格式化模板只有在不承载业务语义、不参与分支或状态判断且无需跨类复用时，才允许保留为字面量。

## 参数校验

- 优先使用 Jakarta Bean Validation 表达可绑定 Bean 属性和方法参数约束。
- 仅在框架校验无法表达约束，或领域对象构造函数、工厂方法等不经过框架绑定链路的内部 API 需要快速失败时，才使用显式检查。
- 显式检查需要抛出 `BaseException` 时，尤其是领域层守卫逻辑，统一使用 framework-core 的 `Require`。
- 不需要抛出业务异常的技术性或编程前置条件检查，module 已因自身职责依赖 Spring Framework 时使用 `org.springframework.util.Assert`；与 Spring 解耦的 module 使用工程统一管理的 `org.apache.commons.lang3.Validate`。不得仅为显式检查引入 Spring Framework，也不得手写这些工具已提供的等价逻辑。工具依赖选择遵循[通用工具最佳实践](bp_common_tools.md#基础工具类)。
- 校验失败的异常 message 必须使用英文，不得包含中文文本。

## 异常

- Jakarta Bean Validation 校验失败时使用框架异常体系。
- 服务自定义的业务异常必须继承 framework-core 提供的 `BaseException`，不得直接继承 `RuntimeException` 或其他 JDK 异常类。
- 领域层的非空检查、前置条件校验等守卫逻辑，必须抛出 `DomainException`（继承自 `BaseException`），禁止使用 `IllegalArgumentException`、`IllegalStateException` 等通用异常替代。
- `DomainException` 必须提供 `invalidEntityId()` 和 `missingField()` 静态工厂方法。
- 业务异常必须携带明确的错误码，错误码遵循[服务错误码最佳实践](bp_error_codes.md#错误码)。
- 业务异常必须处理或继续抛出；非业务异常必须记录足够的定位上下文；不得静默忽略异常。
