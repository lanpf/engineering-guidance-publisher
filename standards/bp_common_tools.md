# 通用工具最佳实践

本文定义基础工具库、Lombok 和 MapStruct 的使用约束。

## 基础工具类

- **默认 · 基础**：通用技术能力优先使用 JDK、工程已有框架或成熟且持续维护的社区库。
- **强制 · 基础**：字符串与集合判定必须先区分纯 null、非空（不为 null 且长度非零）、非空白（至少含一个非空白字符），不得为统一工具改变判断语义；只有允许将 null 与空集合等同处理时才使用统一的集合空判定。
- **强制 · 基础**：module 已因自身职责依赖 Spring Framework 时，复用语义匹配的 Spring 工具；字符串与集合判定按下表选择。

| 判定语义 | 方法 |
| --- | --- |
| 纯 null | `== null` / `!= null` 或 JDK 对应方法 |
| 字符串非空 | `org.springframework.util.StringUtils.hasLength` |
| 字符串非空白 | `org.springframework.util.StringUtils.hasText` |
| 集合 null 或 empty | `org.springframework.util.CollectionUtils.isEmpty` |
- **强制 · 基础**：与 Spring 解耦的 module 不得仅为工具方法引入 Spring Framework。
- **强制 · 基础**：与 Spring 解耦的 module 在 JDK 不足以满足需求时，使用工程统一管理的 Apache Commons，并按既定判定语义选择对应方法。

| 判定语义 | 方法 |
| --- | --- |
| 字符串 empty / 非空 | `org.apache.commons.lang3.StringUtils.isEmpty` / `isNotEmpty` |
| 字符串 blank / 非空白 | `org.apache.commons.lang3.StringUtils.isBlank` / `isNotBlank` |
| 集合 null 或 empty / 非空 | `org.apache.commons.collections4.CollectionUtils.isEmpty` / `isNotEmpty` |
- **强制 · 基础**：不得手写上述工具已提供的等价逻辑。
工具依赖的引入与版本治理遵循[依赖管理最佳实践](bp_dependencies.md#scope-与版本)。

## Lombok

- **强制 · 基础**：不得使用 `lombok.experimental` 下的实验性注解。
- **强制 · 基础**：不得使用 `@Builder`；分步或链式构造使用显式构造函数或工厂方法。
- **强制 · 基础**：仅逐字段赋值且无校验、转换或初始化逻辑的构造器必须使用 Lombok 构造器注解生成，不得手写；包含这些逻辑时必须显式编写构造函数。
- **强制 · 基础**：仅返回或赋值字段且无校验、转换或其他行为的 getter、setter 必须使用 Lombok `@Getter`、`@Setter` 生成，不得手写；包含行为的方法必须显式编写。
- **强制 · 基础**：日志使用 `@Slf4j`，不得手写 `Logger` 字段。
- **强制 · 基础**：聚合根和实体的字段访问仅使用 `@Getter`；不得使用 `@Data` 或对外暴露无领域行为的 setter。
- **强制 · 基础**：聚合根和实体基于唯一标识显式实现相等性，不得使用 Lombok `@EqualsAndHashCode`。
- **强制 · 基础**：值对象按 [Java 最佳实践](bp_java.md#java-语言) 选择普通类时，使用 `final` 字段、getter 和适当的全参构造器，并按全部字段定义相等性。
- **强制 · 基础**：Spring Bean 使用 `final` 依赖和构造器注入，通常使用 `@RequiredArgsConstructor`。

## MapStruct

- **强制 · 基础**：数据载体之间存在对应字段的结构化映射时使用 MapStruct，不得手写逐字段搬运或使用 `BeanUtils.copyProperties`。
- **强制 · 基础**：领域对象构造、业务校验、状态转换和协议编码必须使用显式语义方法；这些行为可以由 MapStruct mapper 调用，但不得隐藏在自动字段映射中。
- **强制 · 基础**：转换契约必须独立定义；手写的 `@Mapper` 接口继承契约，或 `@Mapper` 抽象类实现契约，重新声明契约方法时使用 `@Override`。手写 mapper 类型的包和名称遵循[服务命名最佳实践](bp_naming.md#命名约定)。
- **强制 · 基础**：MapStruct 的具体实现由编译期生成，不得手写或修改生成类。
- **强制 · 基础**：复用转换逻辑时通过 `@Mapper(uses = {...})` 组合已有 mapper，不得复制字段级转换。
- **强制 · 基础**：`componentModel = spring` 和 `unmappedTargetPolicy = ERROR` 在公共 `@MapperConfig` 中声明，具体 mapper 通过 `config` 引用，不得改变公共默认配置。
- **强制 · 基础**：普通映射中确实不参与映射的目标字段必须显式声明 `ignore = true`。
- **强制 · 基础**：部分更新、投影等白名单映射必须在对应方法使用 `@BeanMapping(ignoreByDefault = true)` 并显式声明允许映射的字段；不得以局部 `unmappedTargetPolicy = IGNORE` 替代白名单或关闭漏映射检查。
- **强制 · 基础**：通用 converter/helper 只能供 mapper 使用，不得作为业务组件公开。
