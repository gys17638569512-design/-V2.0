# DMMS API 接口契约
# 版本：v1.0 · 湖南智造机械科技有限公司
# 本文件定义前后端接口规范，所有端必须严格遵守

## 基础规范

### Base URL
- 开发环境：http://localhost:8000/api/v1
- 生产环境：通过 VITE_API_BASE_URL 环境变量配置

### 认证方式
所有接口（除登录外）必须携带 Authorization Header：
```
Authorization: Bearer <access_token>
```

### 内容类型
`Content-Type: application/json`

### 统一响应格式
```json
// 成功
{
  "code": 0,
  "msg": "ok",
  "data": {} 或 [...]
}

// 失败
{
  "code": 400,
  "msg": "错误描述",
  "data": null
}
```

### 错误码定义
| 错误码 | 含义 |
|--------|------|
| 400 | 参数错误 |
| 401 | 未授权（Token无效或过期） |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

### 分页规范
所有列表接口统一使用以下参数：
```
GET /api/v1/resource?page=1&page_size=20
```
返回格式：
```json
{
  "code": 0,
  "msg": "ok",
  "data": {
    "items": [...],
    "total": 100,
    "page": 1,
    "page_size": 20
  }
}
```

### 时间格式
所有时间字段使用ISO 8601格式：`2026-04-19T14:30:00+08:00`

## 接口目录（持续更新）

### M03 用户认证
- POST /api/v1/auth/login
- POST /api/v1/auth/refresh
- POST /api/v1/auth/logout
- GET  /api/v1/auth/me

### M04 字段设置
- GET  /api/v1/field-options
- POST /api/v1/field-options
- PUT  /api/v1/field-options/{id}
- DELETE /api/v1/field-options/{id}

### M05 客户管理
- GET  /api/v1/customers
- POST /api/v1/customers
- GET  /api/v1/customers/{id}
- PUT  /api/v1/customers/{id}
- DELETE /api/v1/customers/{id}

### M06 联系人管理
- GET  /api/v1/customers/{id}/contacts
- POST /api/v1/customers/{id}/contacts
- PUT  /api/v1/contacts/{id}
- DELETE /api/v1/contacts/{id}

### M07 厂区管理
- GET  /api/v1/customers/{id}/sites
- POST /api/v1/customers/{id}/sites
- PUT  /api/v1/sites/{id}
- DELETE /api/v1/sites/{id}

### M08 设备档案
- GET  /api/v1/equipment
- POST /api/v1/equipment
- GET  /api/v1/equipment/{id}
- PUT  /api/v1/equipment/{id}
- DELETE /api/v1/equipment/{id}

### M09 设备证书
- GET  /api/v1/equipment-certificates
- POST /api/v1/equipment-certificates
- GET  /api/v1/equipment-certificates/{id}
- PUT  /api/v1/equipment-certificates/{id}
- DELETE /api/v1/equipment-certificates/{id}

### M12 维保工单
- GET  /api/v1/work-orders
- POST /api/v1/work-orders
- GET  /api/v1/work-orders/{id}
- PUT  /api/v1/work-orders/{id}/status
- POST /api/v1/work-orders/{id}/assign

### M14 报告生成
- POST /api/v1/reports/generate
- GET  /api/v1/reports/{id}
- GET  /api/v1/reports/{id}/pdf
- GET  /api/v1/reports/{id}/share-link

## 核心接口定义示例

### 登录
`POST /api/v1/auth/login`
- 请求：`{"username": "string", "password": "string"}`
- 响应 `data`：
```json
{
  "access_token": "string",
  "token_type": "bearer",
  "expires_in": 86400,
  "user": {"id":1,"username":"admin","role":"ADMIN","name":"张三"}
}
```

### 工单列表
`GET /api/v1/work-orders`
- 响应 `data.items[0]`：
```json
{
  "id": 1,
  "order_no": "WO-2026-000001",
  "customer_name": "宝武钢铁",
  "equipment_name": "QD50T桥式起重机A2",
  "engineer_name": "张伟",
  "status": "PENDING",
  "priority": "NORMAL",
  "planned_date": "2026-04-20",
  "is_overdue": false,
  "overdue_days": 0,
  "created_at": "2026-04-19T10:00:00+08:00"
}
```

## 枚举值定义

### 工单状态枚举
`PENDING` / `ASSIGNED` / `ACCEPTED` / `IN_PROGRESS` / `PENDING_SIGN` / `COMPLETED` / `CANCELLED` / `REVIEWED`

### 工单优先级枚举
`NORMAL` / `URGENT`

### 角色枚举
`SUPER_ADMIN` / `ADMIN` / `MANAGER` / `TECH` / `CLIENT` / `DEALER`
