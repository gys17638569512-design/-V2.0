# Backend Foundation

本目录当前承载 M01-M02 的后端基础，不包含认证逻辑、业务 API 或任何超出地基层的服务实现。

## 当前结构

- `app/api/`: 路由入口与系统级接口
- `app/core/`: 环境配置等基础能力
- `app/db/`: SQLAlchemy 基础对象、公共 ORM 基类与会话工厂
- `app/models/`: 最小 ORM 模型地基（`User` / `Customer`）
- `app/repositories/`: 数据访问层预留目录
- `app/services/`: 业务服务层预留目录
- `app/schemas/`: 通用响应模型
- `alembic/`: Alembic 环境与版本迁移
- `tests/`: 基础接口与数据库迁移测试

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

## 数据库迁移

运行 M02 基线迁移：

```powershell
python -m alembic -c backend\alembic.ini upgrade head
```
```
