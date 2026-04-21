# API接口契约（API_CONTRACT.md）

## 基础规范
- Base URL: `/api/v1`
- 认证方式: `Authorization: Bearer {JWT_TOKEN}`
- 内容类型: `Content-Type: application/json`

## 统一响应格式
**成功响应**：
```json
{
  "code": 0,
  "msg": "ok",
  "data": {...} 或 [...]
}
```

**分页响应**：
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

**错误响应**：
```json
{
  "code": 401,
  "msg": "未授权，请重新登录",
  "data": null
}
```

## 分页参数（统一）
`GET /api/v1/work-orders?page=1&page_size=20&status=PENDING`

## 时间格式
所有时间字段使用ISO 8601格式：`2026-04-19T14:30:00+08:00`

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

### 工单状态枚举
`PENDING` / `ASSIGNED` / `ACCEPTED` / `IN_PROGRESS` / `PENDING_SIGN` / `COMPLETED` / `CANCELLED` / `REVIEWED`

### 工单优先级枚举
`NORMAL` / `URGENT`

### 角色枚举
`SUPER_ADMIN` / `ADMIN` / `MANAGER` / `TECH` / `CLIENT` / `DEALER`
