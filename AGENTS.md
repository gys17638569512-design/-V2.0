# DMMS 数字化维保系统 · AI开发规范
# 所有AI工具必须在开始任何工作前读取本文件
# 版本：v1.0 · 湖南智造机械科技有限公司

## 项目基本信息
- 系统名称：数字化维保系统（DMMS）
- 公司：湖南智造机械科技有限公司
- GitHub仓库：git@github.com:gys17638569512-design/-V2.0.git
- 仓库结构：Monorepo（所有端在同一仓库）
- 部署环境：Ubuntu 22.04 + Docker + Docker Compose

## 技术栈（锁定，不可更改）
后端：Python 3.10+ / FastAPI / SQLAlchemy 2.x / MySQL 8.0 / Redis
PC前端：Vue3 3.4+ / Element Plus / Pinia / TypeScript / Axios
小程序：uni-app（非原生微信小程序）
PDF生成：WeasyPrint（必须配置中文字体）
文件存储：阿里云OSS（私有URL+签名访问）
容器：Docker + Docker Compose

## 绝对禁止事项
❌ 禁止在代码里硬编码任何密码、密钥、手机号
❌ 禁止跳过Alembic直接修改数据库结构
❌ 禁止在Router层直接操作数据库（必须经过Service层）
❌ 禁止在前端代码里硬编码下拉选项值（必须从接口取）
❌ 禁止一次生成超过1个模块的代码
❌ 禁止跳过pytest直接进入下一个模块
❌ 禁止修改已有的数据库迁移文件

## 后端分层架构（严格遵守）
请求 → routers/（参数验证+权限检查）
      → services/（业务逻辑+数据隔离）
      → repositories/（数据库CRUD）
      → models/（ORM表结构）

## 数据隔离规则（必须在Service层实现）
MANAGER角色：.filter(Customer.manager_id == current_user.id)
TECH角色：.filter(WorkOrder.engineer_id == current_user.id)
CLIENT角色：只能看自己企业的数据
ADMIN角色：无限制，看本发展商所有数据

## 统一响应格式
成功：{"code": 0, "msg": "ok", "data": {...}}
失败：{"code": 错误码, "msg": "错误描述", "data": null}
错误码：400参数错误/401未授权/403无权限/404不存在/500服务器错误

## 命名规范
Python文件/函数/变量：snake_case
Python类：PascalCase
Vue组件文件：PascalCase.vue
Vue变量：camelCase
数据库表名：snake_case复数（work_orders, customers）
API路径：kebab-case复数（/api/v1/work-orders）
Git提交：feat(模块): 描述 / fix(模块): 描述

## 环境变量规则
所有配置从.env文件读取，不硬编码在代码里
后端：DATABASE_URL / SECRET_KEY / OSS_* / SMS_* / WECHAT_*
前端：VITE_API_BASE_URL

## 每个模块完成后必须执行
1. 后端：pytest tests/ -v 确认全绿
2. 前端：npm run build 确认无错误
3. git add . && git commit -m "feat(模块名): 完成XX功能"
4. 更新PROGRESS.md：把当前模块标记为✅
