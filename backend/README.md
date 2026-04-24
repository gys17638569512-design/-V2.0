# Backend Foundation

本目录只承载 M01 的后端基础骨架，不包含任何业务 API、认证、数据库模型或 Alembic 迁移。

## 当前结构

- `app/api/`: 路由入口与系统级接口
- `app/core/`: 环境配置等基础能力
- `app/db/`: SQLAlchemy 基础对象与会话工厂
- `app/models/`: ORM 模型预留目录
- `app/repositories/`: 数据访问层预留目录
- `app/services/`: 业务服务层预留目录
- `app/schemas/`: 通用响应模型
- `tests/`: M01 最小测试

## 本地启动

1. 在仓库根目录复制环境变量示例：
   `Copy-Item .env.example .env`
2. 在仓库根目录启动开发环境：
   `docker compose up --build`
3. 打开接口：
   - 健康检查：`http://localhost:8000/api/v1/health`
   - OpenAPI：`http://localhost:8000/docs`

## 本地测试

如果使用 Python 虚拟环境：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend\requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest backend
```
