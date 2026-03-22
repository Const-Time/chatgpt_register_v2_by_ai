返回
API 文档
10 个内容
最后更新：2026-03-22
复制 Markdown

YYDS Mail 提供面向外部集成的 RESTful API，支持临时邮箱、域名管理、API Key 与 Webhook 等能力。这里只展示建议给用户和开发者使用的公开接口，所有接口以 /v1 为前缀。

目录
快速开始
临时邮箱
消息管理
域名管理
API Keys
Webhooks
账号与邮箱
配额与公开信息
AI / LLM
错误处理
1
API 文档

YYDS Mail 提供面向外部集成的 RESTful API，支持临时邮箱、域名管理、API Key 与 Webhook 等能力。这里只展示建议给用户和开发者使用的公开接口，所有接口以 /v1 为前缀。

快速开始
通过 GitHub 或 LinuxDo OAuth 在 /login 登录
前往 API Key 管理 创建密钥
在请求头中使用 X-API-Key 进行 API 调用
bash
curl https://maliapi.215.im/v1/accounts \
  -X POST \
  -H "X-API-Key: AC-your_api_key"
基础 URL
text
https://maliapi.215.im
认证方式
Bearer Token (JWT)

通过 OAuth 登录获取的 JWT 访问令牌。

Authorization: Bearer <access_token>
API Key

以 AC- 前缀开头的 API Key，支持域名范围限制（全部/公共/自有/指定）。

X-API-Key: AC-...
临时 Token

创建临时邮箱时返回的短期有效令牌。

Authorization: Bearer <temp_token>
GET
/v1/plans

获取所有启用套餐及其配额与价格信息。

响应
json
{
  "success": true,
  "data": [
    {
      "id": "free",
      "name": "Free",
      "priceMonthly": 0,
      "maxInboxes": 10,
      "maxApiKeys": 2,
      "maxDomains": 5,
      "maxRps": 10,
      "retentionDays": 1
    }
  ]
}
示例
bash
curl https://maliapi.215.im/v1/plans
2
临时邮箱 API

创建一次性邮箱，无需注册。邮件在 24 小时后自动删除。

POST
/v1/accounts

创建临时邮箱。可选传入自定义前缀与已验证域名。

请求体
json
{
  "address": "my-prefix",
  "domain": "public.example.com"
}
响应
json
{
  "success": true,
  "data": {
    "id": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4",
    "address": "k7xm2pa9bf@public.example.com",
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "inboxType": "temp",
    "source": "api",
    "expiresAt": "2026-03-15T12: 00: 00Z",
    "isActive": true,
    "createdAt": "2026-03-14T12: 00: 00Z"
  }
}
示例
bash
curl https://maliapi.215.im/v1/accounts \
  -X POST
POST
/v1/token

通过邮箱地址获取已有临时邮箱的访问令牌。

请求体
json
{
  "address": "k7xm2pa9bf@public.example.com"
}
响应
json
{
  "success": true,
  "data": {
    "id": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4",
    "address": "k7xm2pa9bf@public.example.com",
    "token": "eyJhbGciOiJIUzI1NiIs..."
  }
}
示例
bash
curl https://maliapi.215.im/v1/token \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"address":"k7xm2pa9bf@public.example.com"}'
GET
/v1/accounts/me

获取当前临时账号信息。

认证: Temp token

响应
json
{
  "success": true,
  "data": {
    "id": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4",
    "address": "k7xm2pa9bf@public.example.com",
    "inboxType": "temp",
    "source": "web",
    "expiresAt": "2026-03-15T12: 00: 00Z",
    "isActive": true,
    "messageCount": 3,
    "createdAt": "2026-03-14T12: 00: 00Z"
  }
}
示例
bash
curl https://maliapi.215.im/v1/accounts/me \
  -H "Authorization: Bearer <temp_token>"
GET
/v1/accounts/{id}

根据 ID 获取临时账号详情。

认证: Temp token / API key / Bearer JWT

请求参数
参数	类型	必填	说明
id	string	是	Account ID
响应
json
{
  "success": true,
  "data": {
    "id": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4",
    "address": "k7xm2pa9bf@public.example.com",
    "inboxType": "temp",
    "source": "api",
    "expiresAt": "2026-03-15T12: 00: 00Z",
    "isActive": true,
    "messageCount": 0,
    "createdAt": "2026-03-14T12: 00: 00Z"
  }
}
示例
bash
curl https://maliapi.215.im/v1/accounts/a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4 \
  -H "Authorization: Bearer <temp_token>"
DELETE
/v1/accounts/{id}

停用临时邮箱。持久邮箱删除请使用 `/v1/me/inboxes/{id}`。

认证: Temp token

请求参数
参数	类型	必填	说明
id	string	是	Account ID
响应
json
204 No Content
示例
bash
curl https://maliapi.215.im/v1/accounts/a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4 \
  -X DELETE \
  -H "Authorization: Bearer <temp_token>"
GET
/v1/domains

列出所有可用于创建临时邮箱的域名。

响应
json
{
  "success": true,
  "data": [
    { "id": "a1b2c3d4...", "domain": "mail.example.com", "isVerified": true, "isPublic": true },
    { "id": "b2c3d4e5...", "domain": "inbox.example.net", "isVerified": true, "isPublic": true }
  ]
}
示例
bash
curl https://maliapi.215.im/v1/domains
4
消息管理

读取、管理和删除邮件消息。支持临时 Token、API Key 或 JWT 认证。

GET
/v1/messages

列出认证邮箱的消息。JWT/API Key 用户需要通过 `?address=xxx` 指定邮箱。

认证: Temp token / API key / Bearer JWT

请求参数
参数	类型	必填	说明
address	string	否	Inbox address (query param, required for JWT/API key users)
limit	number	否	Maximum number of messages to return (default: 50)
响应
json
{
  "success": true,
  "data": {
    "messages": [
      {
        "id": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4",
        "inbox_id": "f6e5d4c3b2a1f6e5d4c3b2a1f6e5d4c3",
        "inboxId": "f6e5d4c3b2a1f6e5d4c3b2a1f6e5d4c3",
        "from": { "name": "Sender", "address": "sender@example.com" },
        "to": [{ "name": "", "address": "k7xm2pa9bf@public.example.com" }],
        "subject": "Welcome!",
        "seen": false,
        "hasAttachments": false,
        "size": 1234,
        "createdAt": "2026-03-14T12: 30: 00Z"
      }
    ],
    "total": 1
  }
}
示例
bash
curl "https://maliapi.215.im/v1/messages?address=k7xm2pa9bf@public.example.com" \
  -H "Authorization: Bearer <token>"
GET
/v1/messages/{id}

获取完整邮件详情，包括正文、HTML 和附件信息。

认证: Temp token / API key / Bearer JWT

请求参数
参数	类型	必填	说明
id	string	是	Message ID
响应
json
{
  "success": true,
  "data": {
    "id": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4",
    "from": { "name": "Sender", "address": "sender@example.com" },
    "to": [{ "name": "", "address": "k7xm2pa9bf@public.example.com" }],
    "subject": "Welcome!",
    "text": "Hello, this is a test email.",
    "html": ["<p>Hello, this is a test email.</p>"],
    "seen": true,
    "hasAttachments": true,
    "size": 1234,
    "createdAt": "2026-03-14T12: 30: 00Z",
    "attachments": [
      {
        "id": "0",
        "filename": "welcome.pdf",
        "contentType": "application/pdf",
        "size": 2048,
        "downloadUrl": "/serve/mailbox/demo/message/attach/0/welcome.pdf"
      }
    ]
  }
}
示例
bash
curl https://maliapi.215.im/v1/messages/a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4 \
  -H "Authorization: Bearer <token>"
PATCH
/v1/messages/{id}

将邮件标记为已读。

认证: Temp token / API key(write) / Bearer JWT

请求参数
参数	类型	必填	说明
id	string	是	Message ID
请求体
json
{
  "seen": true
}
响应
json
{
  "success": true,
  "data": {
    "id": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4",
    "seen": true
  }
}
示例
bash
curl https://maliapi.215.im/v1/messages/a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4 \
  -X PATCH \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"seen":true}'
DELETE
/v1/messages/{id}

删除邮件。

认证: Temp token / API key(write) / Bearer JWT

请求参数
参数	类型	必填	说明
id	string	是	Message ID
响应
json
204 No Content
示例
bash
curl https://maliapi.215.im/v1/messages/a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4 \
  -X DELETE \
  -H "Authorization: Bearer <token>"
GET
/v1/sources/{id}

获取邮件原始源码（RFC 822）。

认证: Temp token / API key / Bearer JWT

请求参数
参数	类型	必填	说明
id	string	是	Message ID
响应
json
{
  "success": true,
  "data": {
    "id": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4",
    "data": "Return-Path: <sender@example.com>\r\nFrom: Sender <sender@example.com>\r\nTo: k7xm2pa9bf@public.example.com\r\nSubject: Welcome!\r\n..."
  }
}
示例
bash
curl https://maliapi.215.im/v1/sources/a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4 \
  -H "Authorization: Bearer <token>"
5
域名管理 API

添加和管理自定义域名。写操作需要身份认证。

GET
/v1/me/domains

列出当前用户拥有的自定义域名。

认证: Bearer JWT / API key

响应
json
{
  "success": true,
  "data": [
    {
      "id": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4",
      "domain": "example.com",
      "isVerified": true,
      "isPublic": false,
      "createdAt": "2026-01-15T10: 00: 00Z"
    }
  ]
}
示例
bash
curl https://maliapi.215.im/v1/me/domains \
  -H "Authorization: Bearer <token>"
POST
/v1/me/domains

添加新的自定义域名。添加后需配置 DNS 记录并完成验证。

认证: Bearer JWT / API key

请求体
json
{
  "domain": "example.com"
}
响应
json
{
  "success": true,
  "data": {
    "id": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4",
    "domain": "example.com",
    "isVerified": false,
    "isPublic": false,
    "verificationToken": "yyds-verify-abc123",
    "createdAt": "2026-03-14T12: 00: 00Z"
  }
}
示例
bash
curl https://maliapi.215.im/v1/me/domains \
  -X POST \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"domain":"example.com"}'
DELETE
/v1/me/domains/{id}

删除域名。删除后将停止接收该域名的邮件。

认证: Bearer JWT / API key

请求参数
参数	类型	必填	说明
id	string	是	Domain ID
响应
json
204 No Content
示例
bash
curl https://maliapi.215.im/v1/me/domains/a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4 \
  -X DELETE \
  -H "Authorization: Bearer <token>"
PATCH
/v1/me/domains/{id}

切换域名的公开/私有可见性。

认证: Bearer JWT / API key

请求参数
参数	类型	必填	说明
id	string	是	Domain ID
请求体
json
{
  "isPublic": true
}
响应
json
{
  "success": true,
  "data": {
    "id": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4",
    "domain": "example.com",
    "isVerified": true,
    "isPublic": true
  }
}
示例
bash
curl https://maliapi.215.im/v1/me/domains/a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4 \
  -X PATCH \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"isPublic":true}'
GET
/v1/me/domains/{id}/dns-guide

获取域名配置说明（TXT 验证记录与 MX 记录）。

认证: Bearer JWT / API key

请求参数
参数	类型	必填	说明
id	string	是	Domain ID
响应
json
{
  "success": true,
  "data": {
    "records": [
      { "type": "CNAME", "name": "mail.example.com", "value": "<mx-host>" },
      { "type": "MX", "name": "example.com", "value": "<mx-host>", "priority": 10 },
      { "type": "TXT", "name": "_yydsmail-verify.example.com", "value": "yyds-verify-abc123" }
    ],
    "instructions": "Please add the above records at your DNS provider, then click verify."
  }
}
示例
bash
curl https://maliapi.215.im/v1/me/domains/a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4/dns-guide \
  -H "Authorization: Bearer <token>"
GET
/v1/me/domains/{id}/dns-status

检查域名当前 DNS 验证状态。

认证: Bearer JWT / API key

请求参数
参数	类型	必填	说明
id	string	是	Domain ID
响应
json
{
  "success": true,
  "data": {
    "records": [
      { "type": "TXT", "name": "_yydsmail-verify.example.com", "status": "ok" },
      { "type": "MX", "name": "example.com", "status": "ok" },
      { "type": "CNAME", "name": "mail.example.com", "status": "fail" }
    ]
  }
}
示例
bash
curl https://maliapi.215.im/v1/me/domains/a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4/dns-status \
  -H "Authorization: Bearer <token>"
POST
/v1/me/domains/{id}/verify

触发域名 DNS 验证（检查 TXT 与 MX）。

认证: Bearer JWT / API key

请求参数
参数	类型	必填	说明
id	string	是	Domain ID
响应
json
{
  "success": true,
  "data": {
    "verified": true,
    "records": [
      { "type": "TXT", "name": "_yydsmail-verify.example.com", "status": "ok" },
      { "type": "MX", "name": "example.com", "status": "ok" },
      { "type": "CNAME", "name": "mail.example.com", "status": "ok" }
    ]
  }
}
示例
bash
curl https://maliapi.215.im/v1/me/domains/a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4/verify \
  -X POST \
  -H "Authorization: Bearer <token>"
6
API Key 管理

创建和管理 API Key，用于程序化访问。密钥支持权限控制。

GET
/v1/me/api-keys

列出当前用户的所有 API Key。

认证: Bearer JWT / API key

响应
json
{
  "success": true,
  "data": {
    "apiKeys": [
      {
        "id": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4",
        "userId": "u_123",
        "name": "My API Key",
        "keyPrefix": "AC-a1b2...",
        "permissions": ["read", "write"],
        "domainScope": "all",
        "allowedDomainIds": [],
        "isActive": true,
        "lastUsedAt": "2026-03-14T12: 00: 00Z",
        "createdAt": "2026-03-01T10: 00: 00Z",
        "updatedAt": "2026-03-14T12: 00: 00Z"
      }
    ],
    "total": 1
  }
}
示例
bash
curl https://maliapi.215.im/v1/me/api-keys \
  -H "Authorization: Bearer <token>"
POST
/v1/me/api-keys

创建新的 API Key。完整密钥仅在创建响应中返回一次。`permissions` 支持 read | write | all；`domainScope` 支持 all | public | own | specific（specific 时需提供 allowedDomainIds）。

认证: Bearer JWT only

请求体
json
{
  "name": "My Production Key",
  "permissions": ["read", "write"],
  "domainScope": "all",
  "allowedDomainIds": []
}
响应
json
{
  "success": true,
  "data": {
    "apiKey": {
      "id": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4",
      "userId": "u_123",
      "name": "My Production Key",
      "keyPrefix": "AC-a1b2...",
      "permissions": ["read", "write"],
      "domainScope": "all",
      "allowedDomainIds": [],
      "isActive": true,
      "createdAt": "2026-03-14T12: 00: 00Z",
      "updatedAt": "2026-03-14T12: 00: 00Z"
    },
    "plainKey": "AC-a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4",
    "warning": "Save this API Key now, it will not be shown again."
  }
}
示例
bash
curl https://maliapi.215.im/v1/me/api-keys \
  -X POST \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name":"My Production Key","permissions":["read","write"],"domainScope":"all"}'
DELETE
/v1/me/api-keys/{id}

撤销 API Key，此操作不可恢复。

认证: Bearer JWT only

请求参数
参数	类型	必填	说明
id	string	是	API key ID
响应
json
204 No Content
示例
bash
curl https://maliapi.215.im/v1/me/api-keys/a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4 \
  -X DELETE \
  -H "Authorization: Bearer <token>"
GET
/v1/me/api-keys/{id}/usage

获取指定 API Key 的使用统计。

认证: Bearer JWT / API key

请求参数
参数	类型	必填	说明
id	string	是	API key ID
响应
json
{
  "success": true,
  "data": {
    "keyId": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4",
    "usage": [
      {
        "endpoint": "GET /v1/messages",
        "usageDate": "2026-03-14T00: 00: 00Z",
        "callCount": 45,
        "errorCount": 1,
        "createdAt": "2026-03-14T00: 00: 10Z",
        "updatedAt": "2026-03-14T12: 30: 00Z"
      }
    ]
  }
}
示例
bash
curl https://maliapi.215.im/v1/me/api-keys/a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4/usage \
  -H "Authorization: Bearer <token>"
7
Webhook 管理

设置 Webhook 以在事件发生时接收实时 HTTP 通知。

GET
/v1/me/webhooks

列出当前用户的所有 Webhook。

认证: Bearer JWT / API key

响应
json
{
  "success": true,
  "data": {
    "webhooks": [
      {
        "id": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4",
        "userId": "u_123",
        "url": "https://example.com/hook",
        "events": ["message.received", "message.deleted"],
        "isActive": true,
        "createdAt": "2026-03-14T12: 00: 00Z",
        "updatedAt": "2026-03-14T12: 00: 00Z"
      }
    ],
    "total": 1
  }
}
示例
bash
curl https://maliapi.215.im/v1/me/webhooks \
  -H "Authorization: Bearer <token>"
POST
/v1/me/webhooks

创建新的 Webhook 订阅。

认证: Bearer JWT only

请求体
json
{
  "url": "https://example.com/hook",
  "events": ["message.received", "message.deleted"],
  "secret": "signing-secret"
}
响应
json
{
  "success": true,
  "data": {
    "id": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4",
    "userId": "u_123",
    "url": "https://example.com/hook",
    "events": ["message.received", "message.deleted"],
    "secret": "signing-secret",
    "isActive": true,
    "createdAt": "2026-03-14T12: 00: 00Z",
    "updatedAt": "2026-03-14T12: 00: 00Z"
  }
}
示例
bash
curl https://maliapi.215.im/v1/me/webhooks \
  -X POST \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com/hook class="code-string">","events":["message.received","message.deleted"],"secret":"signing-secret"}'
DELETE
/v1/me/webhooks/{id}

删除 Webhook。删除后将停止接收通知。

认证: Bearer JWT only

请求参数
参数	类型	必填	说明
id	string	是	Webhook ID
响应
json
204 No Content
示例
bash
curl https://maliapi.215.im/v1/me/webhooks/a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4 \
  -X DELETE \
  -H "Authorization: Bearer <token>"
PATCH
/v1/me/webhooks/{id}

更新 Webhook 的 URL、事件类型或启用状态。需要 JWT 登录（API Key 无法修改 Webhook）。

认证: Bearer JWT only

请求参数
参数	类型	必填	说明
id	string	是	Webhook ID
请求体
json
{
  "url": "https://new-endpoint.example.com/hook",
  "events": ["message.received", "message.deleted"],
  "isActive": false
}
响应
json
{
  "success": true,
  "data": {
    "id": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4",
    "userId": "u_123",
    "url": "https://new-endpoint.example.com/hook",
    "events": ["message.received", "message.deleted"],
    "isActive": false,
    "createdAt": "2026-03-14T12: 00: 00Z",
    "updatedAt": "2026-03-21T08: 00: 00Z"
  }
}
示例
bash
curl https://maliapi.215.im/v1/me/webhooks/a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4 \
  -X PATCH \
  -H "Authorization: Bearer <jwt>" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://new-endpoint.example.com/hook class="code-string">","isActive":false}'
POST
/v1/me/webhooks/{id}/test

向 Webhook URL 发送测试事件并检查连通性。返回状态码和延迟。需要 JWT 登录。

认证: Bearer JWT only

请求参数
参数	类型	必填	说明
id	string	是	Webhook ID
响应
json
{
  "success": true,
  "data": {
    "success": true,
    "statusCode": 200,
    "latencyMs": 156
  }
}
示例
bash
curl https://maliapi.215.im/v1/me/webhooks/a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4/test \
  -X POST \
  -H "Authorization: Bearer <jwt>"
POST
/v1/me/webhooks/{id}/regenerate-secret

重新生成 Webhook 签名密钥。新密钥仅显示一次，旧密钥立即失效。需要 JWT 登录。

认证: Bearer JWT only

请求参数
参数	类型	必填	说明
id	string	是	Webhook ID
响应
json
{
  "success": true,
  "data": {
    "webhookId": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4",
    "secret": "e3b0c44298fc1c149afbf4c8996fb924..."
  }
}
示例
bash
curl https://maliapi.215.im/v1/me/webhooks/a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4/regenerate-secret \
  -X POST \
  -H "Authorization: Bearer <jwt>"
8
账号与邮箱

这里保留开发者在接入过程中真正需要的账号资料、持久邮箱与实时收件接口。

GET
/v1/me

获取当前用户资料及生效配额快照。

认证: Bearer JWT / API key

响应
json
{
  "success": true,
  "data": {
    "id": "u_123",
    "uid": 1024,
    "authType": "github",
    "username": "demo_user",
    "displayName": "Demo",
    "githubId": 123456,
    "role": "user",
    "isActive": true,
    "createdAt": "2026-03-01T10: 00: 00Z",
    "updatedAt": "2026-03-14T12: 00: 00Z",
    "isAdmin": false,
    "quota": {
      "planId": "free",
      "planName": "Free",
      "maxDomains": 5,
      "maxInboxes": 10,
      "maxApiKeys": 2,
      "maxMessagesPerDay": 100,
      "maxApiCallsDaily": 1000,
      "maxApiCallsWeekly": 5000,
      "maxApiCallsMonthly": 20000,
      "maxWebhooks": 3,
      "retentionDays": 1,
      "maxAttachmentBytes": 10485760,
      "storageBytes": 52428800,
      "maxRps": 10,
      "bonusDaily": 0,
      "totalPool": 0
    }
  }
}
PATCH
/v1/me

更新用户资料字段（当前主要是显示名称）。

认证: Bearer JWT / API key

请求体
json
{
  "displayName": "New Name"
}
响应
json
{
  "success": true,
  "data": {
    "id": "u_123",
    "uid": 1024,
    "authType": "github",
    "username": "demo_user",
    "displayName": "New Name",
    "githubId": 123456,
    "role": "user",
    "isActive": true,
    "createdAt": "2026-03-01T10: 00: 00Z",
    "updatedAt": "2026-03-14T12: 05: 00Z",
    "isAdmin": false,
    "quota": {
      "planId": "free",
      "planName": "Free"
    }
  }
}
POST
/v1/me/deactivate

永久注销账号。需要输入确认文字。有 30 天冷静期，期间可恢复。仅限 JWT 调用，API Key 不可用。

认证: Bearer JWT only

响应
json
{
  "success": true,
  "data": {
    "deactivatedAt": "2026-03-21T12: 00: 00Z",
    "cooldownEndsAt": "2026-04-20T12: 00: 00Z",
    "pendingOrders": 0
  }
}
示例
bash
curl https://maliapi.215.im/v1/me/deactivate \
  -X POST \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"confirmation":"DELETE MY ACCOUNT"}'
GET
/v1/me/inboxes

列出当前用户拥有的持久邮箱。

认证: Bearer JWT / API key

响应
json
{
  "success": true,
  "data": [
    {
      "id": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4",
      "userId": "u_123",
      "address": "team@example.com",
      "inboxType": "persistent",
      "source": "web",
      "isActive": true,
      "messageCount": 12,
      "createdAt": "2026-03-01T10: 00: 00Z",
      "updatedAt": "2026-03-14T12: 00: 00Z"
    }
  ]
}
示例
bash
curl https://maliapi.215.im/v1/me/inboxes \
  -H "Authorization: Bearer <token>"
POST
/v1/me/inboxes

创建持久邮箱；`prefix` 和 `domain` 都是可选。

认证: Bearer JWT / API key

请求体
json
{
  "prefix": "team",
  "domain": "example.com"
}
响应
json
{
  "success": true,
  "data": {
    "id": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4",
    "userId": "u_123",
    "address": "team@example.com",
    "inboxType": "persistent",
    "source": "web",
    "isActive": true,
    "messageCount": 0,
    "createdAt": "2026-03-14T12: 00: 00Z",
    "updatedAt": "2026-03-14T12: 00: 00Z"
  }
}
示例
bash
curl https://maliapi.215.im/v1/me/inboxes \
  -X POST \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"prefix":"team","domain":"example.com"}'
DELETE
/v1/me/inboxes/{id}

按 ID 删除持久邮箱。

认证: Bearer JWT / API key

请求参数
参数	类型	必填	说明
id	string	是	Inbox ID
响应
json
204 No Content
示例
bash
curl https://maliapi.215.im/v1/me/inboxes/a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4 \
  -X DELETE \
  -H "Authorization: Bearer <token>"
POST
/v1/me/inboxes/{id}/claim

将临时邮箱认领为你的持久邮箱。

认证: Bearer JWT / API key

请求参数
参数	类型	必填	说明
id	string	是	Temp inbox ID
响应
json
{
  "success": true,
  "data": {
    "id": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4",
    "userId": "u_123",
    "address": "claimed@example.com",
    "inboxType": "persistent",
    "source": "web",
    "isActive": true,
    "messageCount": 3,
    "createdAt": "2026-03-10T08: 00: 00Z",
    "updatedAt": "2026-03-14T12: 00: 00Z"
  }
}
示例
bash
curl https://maliapi.215.im/v1/me/inboxes/a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4/claim \
  -X POST \
  -H "Authorization: Bearer <token>"
GET
/v1/auth/ws-ticket

获取短期有效的 WebSocket ticket，用于实时消息流鉴权。

认证: Bearer JWT / API key

响应
json
{
  "success": true,
  "data": { "ticket": "eyJ..." }
}
示例
bash
curl https://maliapi.215.im/v1/auth/ws-ticket \
  -H "Authorization: Bearer <token>"
WS
/v1/ws

通过 WebSocket 接收实时收件事件。`token` 参数来自 `/v1/auth/ws-ticket`。

认证: WebSocket ticket

9
配额与公开信息

查询您的 API 配额使用情况，并查看对外公开的套餐与平台统计信息。

GET
/v1/me/quota

获取当前用户的详细配额使用情况，包括所有维度的限制和剩余量。

认证: Bearer JWT / API key

响应
json
{
  "success": true,
  "data": {
    "planId": "pro",
    "planName": "Pro",
    "dimensions": [
      { "name": "domains", "limit": 20, "used": 3, "remaining": 17 },
      { "name": "inboxes", "limit": 50, "used": 8, "remaining": 42 },
      { "name": "apiKeys", "limit": 10, "used": 2, "remaining": 8 },
      { "name": "apiCallsDaily", "limit": 50500, "used": 120, "remaining": 50380 },
      { "name": "apiCallsWeekly", "limit": 200000, "used": 0, "remaining": 200000 },
      { "name": "apiCallsMonthly", "limit": 1000000, "used": 0, "remaining": 1000000 },
      { "name": "maxRps", "limit": 60, "used": 0, "remaining": 60 },
      { "name": "bonusDaily", "limit": 500, "used": 0, "remaining": 500 },
      { "name": "purchasedPool", "limit": 2000, "used": 0, "remaining": 2000 },
      { "name": "totalPool", "limit": 52500, "used": 120, "remaining": 52380 }
    ]
  }
}
示例
bash
curl https://maliapi.215.im/v1/me/quota \
  -H "X-API-Key: AC-your_key"
余额与支付

通过 LinuxDo 积分支付管理账户余额。所有金额单位为分（1 元 = 100 分）。

GET
/v1/me/balance

获取当前余额和最近的交易记录。金额单位为分。

认证: Bearer JWT only

响应
json
{
  "success": true,
  "data": {
    "balance": 10000,
    "reward": 5000,
    "purchased": 3000,
    "redemption": 2000,
    "total": 10000
  }
}
示例
bash
curl https://maliapi.215.im/v1/me/balance \
  -H "Authorization: Bearer YOUR_JWT"
POST
/v1/me/balance/topup

通过 LinuxDo 积分支付充值余额。创建待支付订单并返回支付链接。

认证: Bearer JWT only

响应
json
{
  "success": true,
  "data": {
    "orderId": "ord_abc123",
    "payUrl": "https://connect.linux.do/pay/...",
    "amountCents": 1000,
    "status": "pending"
  }
}
示例
bash
curl -X POST https://maliapi.215.im/v1/me/balance/topup \
  -H "Authorization: Bearer YOUR_JWT" \
  -H "Content-Type: application/json" \
  -d '{"amountCents": 1000}'
POST
/v1/me/balance/purchase

使用余额购买 API 调用次数。购买后立即生效，会从余额中扣除对应金额。

认证: Bearer JWT only

响应
json
{
  "success": true,
  "data": {
    "orderId": "ord_def456",
    "quantity": 1000,
    "priceCents": 800,
    "status": "completed"
  }
}
示例
bash
curl -X POST https://maliapi.215.im/v1/me/balance/purchase \
  -H "Authorization: Bearer YOUR_JWT" \
  -H "Content-Type: application/json" \
  -d '{"quantity": 1000}'
GET
/v1/pricing

获取 API 调用次数的购买套餐和货币配置。公开接口，无需认证。

响应
json
{
  "success": true,
  "data": {
    "packages": [
      { "quantity": 100, "priceCents": 100 },
      { "quantity": 1000, "priceCents": 800 },
      { "quantity": 10000, "priceCents": 5000 }
    ],
    "rateLimits": [
      { "tier": "free", "maxDaily": 1000, "rps": 10, "burst": 100 },
      { "tier": "basic", "maxDaily": 5000, "rps": 30, "burst": 300 },
      { "tier": "pro", "maxDaily": 50000, "rps": 60, "burst": 600 },
      { "tier": "enterprise", "maxDaily": -1, "rps": 200, "burst": 2000 }
    ],
    "currency": { "code": "CNY", "symbol": "¥", "suffix": "" }
  }
}
示例
bash
curl https://maliapi.215.im/v1/pricing
GET
/v1/stats

获取平台公开统计数据。`totalCreatedInboxes` 是清晰字段名，`totalMessages` 保留为兼容别名，两者都表示累计创建邮箱数。

响应
json
{
  "success": true,
  "data": {
    "totalUsers": 12345,
    "totalDomains": 120,
    "verifiedDomains": 108,
    "publicDomains": 64,
    "totalInboxes": 56789,
    "anonInboxes": 43210,
    "totalCreatedInboxes": 654321,
    "totalMessages": 654321,
    "todayApiCalls": 9876,
    "topDomains": [
      {
        "domain": "mail.example.com",
        "isVerified": true,
        "usageToday": 180,
        "usageTotal": 24500
      }
    ],
    "hourlyActivity": [
      { "hour": "09", "inboxes": 14, "apiCalls": 0 },
      { "hour": "10", "inboxes": 22, "apiCalls": 0 }
    ],
    "dailyTrend": [
      { "date": "03-14", "inboxes": 120, "apiCalls": 6400, "users": 42 },
      { "date": "03-15", "inboxes": 135, "apiCalls": 7100, "users": 48 }
    ]
  }
}
示例
bash
curl https://maliapi.215.im/v1/stats
10
AI / LLM 集成

提供 llms.txt 端点，让 AI 助手（如 ChatGPT、Claude）快速理解公开集成面与认证方式，帮助您编写接入代码。

GET
/v1/llms.txt

返回一份纯文本格式的公开 API 摘要，供 AI/LLM 快速理解外部可集成端点和认证方式。

响应
json
# yyds Mail API
> Public integration summary for temporary inboxes, domains, API keys, webhooks, and realtime access.
> Base URL: https://api.example.com/v1

## Scope
- Public integration surface only
- Internal admin, payment checkout, and operations endpoints are excluded

## Authentication
- Bearer Token: Authorization: Bearer <jwt>
- API Key: X-API-Key: AC-xxx
- Temp Token: Authorization: Bearer <temp_token>

## Endpoints
POST /v1/accounts — Create temporary inbox
POST /v1/token — Get token for existing inbox
GET  /v1/messages?address=xxx — List messages
GET  /v1/messages/{id} — Get message detail
...
示例
bash
curl https://maliapi.215.im/v1/llms.txt
如何使用

将 llms.txt 的 URL 提供给任意 AI 助手，它就能理解公开集成面并帮助您编写接入代码。

text
# ChatGPT / Claude / other AI assistants
# Just point the AI to:
https://maliapi.215.im/v1/llms.txt

# The AI can then understand the public integration surface
# and help you write integration code.
11
错误处理

所有错误响应遵循统一格式：

json
{
  "success": false,
  "error": "Invalid or expired token"
}
HTTP 状态码
状态码	说明
200	成功
201	创建成功
400	请求错误 — 参数无效
401	未授权 — 令牌缺失或无效
403	禁止访问 — 权限不足
404	未找到
429	请求过多 — 已触发限流
500	服务器内部错误
速率限制

API 请求在三个层级进行限流：基于 IP、基于用户和基于 API Key。触发限流时，API 返回 429 状态码，并在 Retry-After 响应头中指示重试时间。

对 API 有疑问？

访问社区