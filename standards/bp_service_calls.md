# 服务调用最佳实践

本文定义同步服务调用中的契约复用、本地适配和边界隔离约束。

## 内部服务调用

- **强制 · 主题**：内部服务调用应优先依赖被调用方发布的 API module，直接复用其请求与响应契约，不得重复定义等价对象；调用方只能依赖被调用方的公开 API，不得依赖其 application、interfaces 或具体实现 module。

## 内部调用降级契约

- **强制 · 主题**：仅当被调用方的 API module 无法引用，或其公开契约不适用于当前调用边界时，才允许定义本地适配类型；本地请求的命名遵循[服务命名最佳实践](bp_naming.md#命名约定)并实现 `Request`，普通响应使用 `Result<T>`，分页响应使用 `PageResult<T>`。`T` 的类型名称应尽量与被调用方公开契约中的对应类型保持一致，但不代表必须复用同一个 Java 类型；存在防腐层、协议差异或本地语义差异时，应按本地语义命名，不得为了保持同名而形成错误耦合。

## 外部服务调用

- **强制 · 主题**：外部服务调用必须封闭在具体 infrastructure 适配 module 的本地适配边界内，使用调用方拥有的请求与响应类型并按[服务命名最佳实践](bp_naming.md#命名约定)命名；外部 SDK、协议模型及其序列化细节不得越过适配边界进入 application 或 domain，本地类型与外部模型之间必须显式转换。
- **强制 · 主题**：外部服务的固定结构请求和响应必须定义类型化协议模型；使用 `application/json` 传输时分别使用 `*RequestPayload`、`*ResponsePayload`。
- **强制 · 主题**：HTTP method 和参数承载位置不改变 Payload 命名；GET 请求的 query parameter、path parameter、header 以及 POST 请求的 form 或 body 由 client adapter、专用 encoder 或 mapper 从 Payload 完成绑定。
- **强制 · 主题**：`*RequestPayload`、`*ResponsePayload` 只表达外部协议数据，不得提供 `queryParams()`、`headers()`、序列化或 HTTP 参数组装等传输行为，也不得依赖某一种 HTTP client。
- **默认 · 主题**：参数固定、数量很少且不存在复用需求时，client 方法可以显式声明参数。

## Map 使用边界

- **强制 · 主题**：外部协议正式定义 `additionalProperties`、metadata、labels、动态标识 key 等动态键值结构，字段名称或集合只能在运行时确定，或需要透明转发本服务不解释的扩展字段时，允许使用 Map 表达该协议结构。
- **强制 · 主题**：第三方 SDK 或底层 client 只接受 Map，或 form、multipart、签名算法明确要求键值集合且现有 client 无法从类型化 Payload 编码时，允许只在 infrastructure adapter 内使用 Map 完成技术适配。
- **强制 · 主题**：字段集合固定时必须定义类型化 Payload；不得仅为减少类型定义、复用通用请求对象、快速拼装少量固定字段或规避 mapper 而使用 Map。必须使用 Map 时，其构造、转换和固定协议字段名必须封闭在对应 infrastructure adapter 内，固定字段名使用该外部服务专属常量，不得向 port、application 或 domain 泄漏。
