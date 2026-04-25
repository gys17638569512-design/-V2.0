# Backend Foundation

本目录当前承载 M01-M03 的后端基础，已包含最小认证逻辑与首个管理员初始化命令，但仍未进入业务 API 开发阶段。

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
```

## 数据库迁移

运行 M02 基线迁移：

```powershell
python -m alembic -c backend\alembic.ini upgrade head
```

## 初始化首个管理员

完成数据库迁移后，可运行下面的命令创建系统第一位管理员：

```powershell
cd backend
python -m app.bootstrap_admin --username admin --password "请改成强密码" --full-name "系统管理员"
```

说明：
- 这个命令只允许创建第一位管理员
- 如果系统里已经有管理员，再次执行会直接拒绝
