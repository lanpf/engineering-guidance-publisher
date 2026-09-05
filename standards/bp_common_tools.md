# 通用工具最佳实践

本文定义基础工具库、Lombok 和 MapStruct 的使用约束。

## 基础工具类

- **默认 · 基础**：通用技术能力优先使用 JDK、工程已有框架或成熟且持续维护的社区库。
- **强制 · 基础**：module 已因自身职责依赖 Spring Framework 时，字符串 null、empty、blank 判断统一使用 `org.springframework.util.StringUtils.hasText`，集合 null、empty 判断统一使用 `org.springframework.util.CollectionUtils.isEmpty`，其他基础判断优先复用 `org.springframework.util` 中的对应工具。
- **强制 · 基础**：与 Spring 解耦的 module 不得仅为工具方法引入 Spring Framework。
- **强制 · 基础**：与 Spring 解耦的 module 在 JDK 不足以满足需求时，使用工程统一管理的 Apache Commons：字符串使用 `org.apache.commons.lang3.StringUtils.isBlank`/`isNotBlank`，集合使用 `org.apache.commons.collections4.CollectionUtils.isEmpty`/`isNotEmpty`。
- **强制 · 基础**：不得手写上述工具已提供的等价逻辑。
工具依赖的引入与版本治理遵循[依赖管理最佳实践](bp_dependencies.md#scope-与版本)。

## Lombok

- **强制 · 基础**：不得使用 `lombok.experimental` 下的实验性注解，不得使用 `@Builder`；分步或链式构造使用显式构造函数或工厂方法。
- **强制 · 基础**：仅逐字段赋值且无校验、转换或初始化逻辑的构造器必须使用 Lombok 构造器注解生成，不得手写；包含这些逻辑时必须显式编写构造函数。
- **强制 · 基础**：仅返回或赋值字段且无校验、转换或其他行为的 getter、setter 必须使用 Lombok `@Getter`、`@Setter` 生成，不得手写；包含行为的方法必须显式编写。
- **强制 · 基础**：日志使用 `@Slf4j`，不得手写 `Logger` 字段。
- **强制 · 基础**：聚合根和实体仅使用 `@Getter`；不得使用 `@Data` 或 Lombok `@EqualsAndHashCode`，基于唯一标识显式实现相等性。
- **强制 · 基础**：值对象按 [Java 最佳实践](bp_java.md#java-语言) 选择普通类时，使用 `final` 字段、getter 和适当的全参构造器，并按全部字段定义相等性。
- **强制 · 基础**：Spring Bean 使用 `final` 依赖和构造器注入，通常使用 `@RequiredArgsConstructor`。

## MapStruct

- **强制 · 基础**：数据载体之间存在对应字段的结构化映射时使用 MapStruct，不得手写逐字段搬运或使用 `BeanUtils.copyProperties`。
- **强制 · 基础**：领域对象构造、业务校验、状态转换和协议编码必须使用显式语义方法；这些行为可以由 MapStruct mapper 调用，但不得隐藏在自动字段映射中。
- **强制 · 基础**：转换契约必须独立定义；MapStruct 只作为实现机制，实现类必须实现契约并在方法上使用 `@Override`。实现类的包和名称遵循[服务命名最佳实践](bp_naming.md#命名约定)。
- **强制 · 基础**：复用转换逻辑时通过 `@Mapper(uses = {...})` 组合已有 mapper，不得复制字段级转换。
- **强制 · 基础**：`componentModel = spring` 和 `unmappedTargetPolicy = ERROR` 在公共 `@MapperConfig` 中声明，具体 mapper 通过 `config` 引用；确实不参与映射的字段必须显式声明 `ignore = true`。
- **强制 · 基础**：通用 converter/helper 只能供 mapper 使用，不得作为业务组件公开。
