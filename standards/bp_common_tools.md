# 通用工具最佳实践

本文定义基础工具库、Lombok 和 MapStruct 的使用约束。

## 基础工具类

- 通用技术能力优先使用 JDK、工程已有框架或成熟且持续维护的社区库，不得重复实现已有可靠实现的散列、编码、集合、I/O 或基础设施算法。
- module 已因自身职责依赖 Spring Framework 时，字符串 null、empty、blank 判断统一使用 `org.springframework.util.StringUtils.hasText`，集合 null、empty 判断统一使用 `org.springframework.util.CollectionUtils.isEmpty`，其他基础判断优先复用 `org.springframework.util` 中的对应工具。
- 与 Spring 解耦的 module 不得仅为工具方法引入 Spring Framework。
- 与 Spring 解耦的 module 在 JDK 不足以满足需求时，使用工程统一管理的 Apache Commons：字符串使用 `org.apache.commons.lang3.StringUtils.isBlank`/`isNotBlank`，集合使用 `org.apache.commons.collections4.CollectionUtils.isEmpty`/`isNotEmpty`。
- 不得手写上述工具已提供的等价逻辑。
- 引入新库前必须评估维护活跃度、安全性、许可证和依赖成本；已有依赖能满足需求时不得引入功能重叠的库。版本管理遵循[依赖管理最佳实践](bp_dependencies.md#scope-与版本)。

## Lombok

- 不得使用 `lombok.experimental` 下的实验性注解，不得使用 `@Builder`；分步或链式构造使用显式构造函数或工厂方法。
- 仅逐字段赋值且无校验、转换或初始化逻辑的构造器必须使用 Lombok 构造器注解生成，不得手写；包含这些逻辑时必须显式编写构造函数。
- 仅返回或赋值字段且无校验、转换或其他行为的 getter、setter 必须使用 Lombok `@Getter`、`@Setter` 生成，不得手写；包含行为的方法必须显式编写。
- 日志使用 `@Slf4j`，不得手写 `Logger` 字段。
- 聚合根和实体仅使用 `@Getter`；不得使用 `@Data` 或 Lombok `@EqualsAndHashCode`，基于唯一标识显式实现相等性。
- 值对象按 [Java 最佳实践](bp_java.md#java-语言) 选择普通类时，使用 `final` 字段、getter 和适当的全参构造器，并按全部字段定义相等性。
- Spring Bean 使用 `final` 依赖和构造器注入，通常使用 `@RequiredArgsConstructor`。

## MapStruct

- 对象转换使用 MapStruct，不得手写字段搬运或使用 `BeanUtils.copyProperties`。
- 转换契约必须独立定义；MapStruct 只作为实现机制，实现类必须实现契约并在方法上使用 `@Override`。实现类的包和名称遵循[服务命名最佳实践](bp_naming.md#命名约定)。
- 复用转换逻辑时通过 `@Mapper(uses = {...})` 组合已有 mapper，不得复制字段级转换。
- `componentModel = spring` 和 `unmappedTargetPolicy = IGNORE` 在公共 `@MapperConfig` 中声明，具体 mapper 通过 `config` 引用。
- 通用 converter/helper 只能供 mapper 使用，不得作为业务组件公开。
