# 通用工具最佳实践

本文定义基础工具库、Lombok 和 MapStruct 的使用约束。

## 基础工具类

- **默认 · 基础**：通用技术能力优先使用 JDK 和 module 已依赖的框架工具；两者不足以满足需求时，再按依赖准入规则评估成熟且持续维护的社区库。 <!-- JAVA-UTILITY-001 -->
- **强制 · 基础**：Guava 只因哈希等明确选定的能力按需引入，不作为 framework 工程隐含的通用工具基线；不得仅因它已在依赖中，就用 Preconditions 替代语义匹配的优先检查工具。 <!-- JAVA-UTILITY-GUAVA-SCOPE-001 -->
- **强制 · 基础**：字符串与集合判定必须先区分纯 null、非空（不为 null 且长度非零）、非空白（至少含一个非空白字符），不得为统一工具改变判断语义；只有允许将 null 与空集合等同处理时才使用统一的集合空判定。 <!-- JAVA-PREDICATE-SEMANTICS-001 -->
- **强制 · 基础**：module 已因自身职责依赖 Spring Framework 时，复用语义匹配的 Spring 工具；字符串与集合判定按下表选择。 <!-- JAVA-UTILITY-SPRING-001 -->

| 判定语义 | 方法 |
| --- | --- |
| 纯 null | `== null` / `!= null` 或 `Objects.isNull` / `Objects.nonNull` 布尔判定 |
| 字符串非空 | `org.springframework.util.StringUtils.hasLength` |
| 字符串非空白 | `org.springframework.util.StringUtils.hasText` |
| 集合 null 或 empty | `org.springframework.util.CollectionUtils.isEmpty` |
- **强制 · 基础**：与 Spring 解耦的 module 不得仅为工具方法引入 Spring Framework。 <!-- JAVA-UTILITY-004 -->
- **强制 · 基础**：已有依赖提供语义匹配的工具时应复用，不重复实现。 <!-- JAVA-UTILITY-006 -->
- **强制 · 基础**：仅需简单字符串或集合判定时，不得为避免直接使用 JDK API 而新增依赖或通用封装。 <!-- JAVA-SIMPLE-PREDICATE-DEPENDENCY-001 -->

工具依赖的引入与版本治理遵循[依赖管理最佳实践](bp_dependencies.md#scope-与版本)。上表仅适用于布尔判定；抛出异常的检查、工具优先级及禁用项统一遵循[显式检查](bp_validation.md#显式检查)。

## Lombok

- **强制 · 主题**：不得使用 `lombok.experimental` 下的实验性注解。 <!-- LOMBOK-EXPERIMENTAL-001 -->
- **默认 · 主题**：使用 Lombok 的工程默认以构造器或工厂表达创建语义。有明确收益时可采用 @Builder。 <!-- LOMBOK-BUILDER-001 -->
- **默认 · 主题**：已采用 Lombok 时，纯字段赋值构造器优先用构造器注解。含校验、转换或初始化逻辑的构造器显式编写。 <!-- LOMBOK-CONSTRUCTOR-001 -->
- **默认 · 主题**：已采用 Lombok 时，纯字段访问优先用 @Getter 或 @Setter。有校验、转换或其他行为的方法显式编写。 <!-- LOMBOK-ACCESSOR-001 -->
- **默认 · 主题**：已采用 Lombok 时优先用 @Slf4j 声明 Logger。 <!-- LOMBOK-LOG-001 -->
- **强制 · 主题**：聚合根和实体的字段访问仅使用 `@Getter`；不得使用 `@Data` 或对外暴露无领域行为的 setter。 <!-- LOMBOK-ENTITY-ACCESS-001 -->
- **强制 · 主题**：聚合根和实体基于唯一标识显式实现相等性，不得使用 Lombok `@EqualsAndHashCode`。 <!-- LOMBOK-ENTITY-EQUALITY-001 -->
- **强制 · 主题**：值对象按 [Java 最佳实践](bp_java.md#java-语言) 选择普通类时，使用 `final` 字段、getter 和适当的全参构造器，并按全部字段定义相等性。 <!-- LOMBOK-VALUE-001 -->
- **强制 · 主题**：Spring Bean 使用 `final` 依赖和构造器注入，通常使用 `@RequiredArgsConstructor`。 <!-- LOMBOK-SPRING-001 -->

## MapStruct

- **默认 · 主题**：已采用 MapStruct 时，成组结构化字段映射默认交给 MapStruct。局部、简单且清晰的映射可用构造器或工厂方法。 <!-- MAPSTRUCT-CONVERSION-001 -->
- **强制 · 主题**：领域对象构造、业务校验、状态转换和协议编码必须使用显式语义方法；这些行为可以由 MapStruct mapper 调用，但不得隐藏在自动字段映射中。 <!-- MAPSTRUCT-SEMANTIC-001 -->
- **默认 · 主题**：多实现替换、跨 module 共用契约等场景单独定义转换接口，mapper 实现该契约。单一局部映射可直接声明 mapper。 <!-- MAPSTRUCT-CONTRACT-BINDING-001 -->
- **强制 · 主题**：MapStruct 的具体实现由编译期生成，不得手写或修改生成类。 <!-- MAPSTRUCT-GENERATED-001 -->
- **强制 · 主题**：复用转换逻辑时通过 `@Mapper(uses = {...})` 组合已有 mapper，不得复制字段级转换。 <!-- MAPSTRUCT-REUSE-001 -->
- **强制 · 主题**：`componentModel = spring` 和 `unmappedTargetPolicy = ERROR` 在公共 `@MapperConfig` 中声明，具体 mapper 通过 `config` 引用，不得改变公共默认配置。 <!-- MAPSTRUCT-SHARED-CONFIG-001 -->
- **强制 · 主题**：普通映射中确实不参与映射的目标字段必须显式声明 `ignore = true`。 <!-- MAPSTRUCT-EXPLICIT-IGNORE-001 -->
- **强制 · 主题**：部分更新、投影等白名单映射必须在对应方法使用 `@BeanMapping(ignoreByDefault = true)` 并显式声明允许映射的字段；不得以局部 `unmappedTargetPolicy = IGNORE` 替代白名单或关闭漏映射检查。 <!-- MAPSTRUCT-WHITELIST-001 -->
- **强制 · 主题**：通用 converter/helper 只能供 mapper 使用，不得作为业务组件公开。 <!-- MAPSTRUCT-HELPER-001 -->
