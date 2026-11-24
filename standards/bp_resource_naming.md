# 资源命名最佳实践

本文定义业务资源键、命名空间、Resolver 职责和命名空间注入边界；资源相关类型的名称遵循[服务命名最佳实践](bp_naming.md#命名约定)。

## 资源键与命名空间

- **强制 · 主题**：本规则只限制业务服务，不限制 `framework-*` 等框架工程内部 module；框架内部资源键由框架工程文档约定。 <!-- NAME-RESOURCE-SCOPE-001 -->
- **强制 · 主题**：资源名称由命名空间前缀与业务键组成；命名空间必须区分应用以防止跨应用串扰，环境隔离由部署基础设施保证。 <!-- NAME-NAMESPACE-001 -->
- **强制 · 主题**：命名空间只表达应用身份，不得承载业务语义；业务语义只出现在业务键部分。 <!-- NAME-NAMESPACE-003 -->
- **强制 · 主题**：业务键只需在命名空间内唯一；同一业务键在不同应用中必须解析为不同物理资源。 <!-- NAME-NAMESPACE-002 -->
- **强制 · 主题**：业务代码只面向业务键，具体场景的 `*KeyResolver` 只负责业务前缀和业务键段，并通过注入的 `ResourceNameResolver` 解析资源键，不得处理、解析或手工拼接命名空间。 <!-- NAME-BUSINESS-KEY-BOUNDARY-001 -->
- **强制 · 主题**：同一资源的命名空间必须且只能注入一次，可以由场景装配的 `ResourceNameResolver` 或最终资源适配边界注入；禁止同时使用 `NamespacedResourceNameResolver` 与再次注入命名空间的最终适配器。 <!-- NAME-RESOURCE-NAMESPACE-ONCE-001 -->
- **强制 · 主题**：选择场景装配注入时，场景配置实现 `Namespaced`，并向 `*KeyResolver` 注入由该配置和 `NamespaceResolver` 组装的 `NamespacedResourceNameResolver`。 <!-- NAME-RESOURCE-003 -->
- **强制 · 主题**：选择最终资源适配边界注入时，`*KeyResolver` 使用不注入命名空间的 `ResourceNameResolver`，由最终适配器统一完成命名空间隔离。 <!-- NAME-RESOURCE-004 -->

- **强制 · 主题**：应用命名空间身份由统一基础设施配置提供。 <!-- NAME-NAMESPACE-CONFIG-001 -->
- **强制 · 主题**：业务代码、业务配置和适配器不得为单个资源重复声明或手工拼接应用、环境等命名空间前缀；注入次数遵循本节单次注入规则。 <!-- NAME-NAMESPACE-MANUAL-PREFIX-001 -->
- **强制 · 主题**：框架入口已完成资源解析时，业务代码不得再次解析或注入命名空间；分布式锁的具体锁键行为遵循[分布式锁最佳实践](bp_lock.md#分布式锁)。 <!-- NAME-RESOURCE-005 -->
