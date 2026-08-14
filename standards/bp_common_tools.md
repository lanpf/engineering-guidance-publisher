# 通用工具最佳实践

本文定义基础工具库、Lombok 和 MapStruct 的使用约束。

## 基础工具类

- 通用技术能力优先使用 JDK、工程已有框架或成熟且持续维护的社区库，不得重复实现已有可靠实现的散列、编码、集合、I/O 或基础设施算法。
- module 已依赖 Spring Framework 时，字符串和集合的常见判断优先使用 `StringUtils`、`CollectionUtils` 等 Spring 工具类。
- 引入新库前必须评估维护活跃度、安全性、许可证和依赖成本，并统一版本；已有依赖能满足需求时不得引入功能重叠的库。

## Lombok

- 不得使用 `lombok.experimental` 下的实验性注解，不得使用 `@Builder`；分步或链式构造使用显式构造函数或工厂方法。
- 仅按字段赋值且无校验或转换的构造器可以使用 Lombok 构造器注解；包含不变性校验、转换或初始化逻辑时必须显式编写构造函数。
- 日志使用 `@Slf4j`，不得手写 `Logger` 字段。
- 聚合根和实体仅使用 `@Getter`，通过领域行为改变状态；不得使用 `@Data` 或 Lombok `@EqualsAndHashCode`，基于唯一标识显式实现相等性。
- 值对象优先使用 `record`；不适合时使用 `final` 字段、getter 和适当的全参构造器，并按全部字段定义相等性。
- Spring Bean 使用 `final` 依赖和构造器注入，通常使用 `@RequiredArgsConstructor`。

## MapStruct

- 对象转换使用 MapStruct，不得手写字段搬运或使用 `BeanUtils.copyProperties`。
- 转换契约必须独立定义；MapStruct 只作为实现机制。实现放在契约包的 `mapstruct` 子包，命名为 `*MapStructMapper`，实现契约并在方法上使用 `@Override`。
- 复用转换逻辑时通过 `@Mapper(uses = {...})` 组合已有 mapper，不得复制字段级转换。
- `componentModel = spring` 和 `unmappedTargetPolicy = IGNORE` 在公共 `@MapperConfig` 中声明，具体 mapper 通过 `config` 引用。
- 通用 converter/helper 只能供 mapper 使用，不得作为业务组件公开。
