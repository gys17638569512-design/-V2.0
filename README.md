# 数字化维保系统（DMMS）
湖南智造机械科技有限公司 · Digital Maintenance Management System

## 技术栈
- 后端：FastAPI + MySQL 8.0 + Redis
- PC前端：Vue3 + Element Plus + Pinia
- 小程序：uni-app
- 部署：Ubuntu 22.04 + Docker

## 开发规范
所有AI工具开始工作前必须读取 AGENTS.md

## 当前后端基础结果
- 已建立 `backend/` 最小可运行后端骨架
- 已提供开发用 `docker-compose.yml`、`backend/Dockerfile`、`.env.example`
- 已建立 SQLAlchemy 2.x ORM 基础、最小 `User` / `Customer` 地基表
- 已提供 Alembic 初始化结构与 M02 基线迁移
- 已提供 M03 最小认证闭环：`POST /api/v1/auth/login`、`POST /api/v1/auth/refresh`、`POST /api/v1/auth/logout`、`GET /api/v1/auth/me`
- 当前基础开放接口包括系统健康检查：`GET /api/v1/health`

## 协同与计划
- 当前协同规则：`tasks/handover/NEXUS_COLLABORATION_RULES.md`
- 当前执行计划：`tasks/handover/CURRENT_EXECUTION_PLAN.md`

## 快速启动
1. 在仓库根目录复制环境变量文件：`Copy-Item .env.example .env`
2. 在仓库根目录启动开发环境：`docker compose up --build`
3. 访问：
   - 健康检查：`http://localhost:8000/api/v1/health`
   - OpenAPI 文档：`http://localhost:8000/docs`

## 项目进度
查看 PROGRESS.md
