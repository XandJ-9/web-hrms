# 项目结构说明

此文档基于工作区：`d:\\svn\\xujia\\常用脚本\\code_store\\web-hrms`，对仓库的主要目录、关键文件、技术栈、运行方式和注意事项作说明。

## 一、总体概览
该仓库是一个前后端分离的 Web 应用，包含两个主要子项目：
- `backend/`：后端（Django）项目
- `frontend/`：前端（Vue 3 + Vite）应用（RuoYi 前端）

仓库根目录还包含一些全局或辅助文件，如数据库文件、顶层 README、虚拟环境目录等。

根目录（部分）
- `.git/`, `.gitignore`
- `.python-version`, `.venv/`（存在）
- `db.sqlite3`（SQLite 数据库文件，位于根或 backend 下）
- `backend/`（后端 Django 项目）
- `frontend/`（前端 Vue + Vite 项目）
- 以及若干顶级配置或文档文件（如根 README）

## 二、后端（backend）
路径：`backend/`

主要内容（已观察到）
- `manage.py`、`main.py`
- `pyproject.toml`：项目元信息（显示 name = "backend", Python >= 3.12）
- `requirements.txt`：列出后端运行时依赖（包括 Django 5.2.8、djangorestframework、asgiref、sqlparse、tzdata 等）
- `db.sqlite3`（位于 backend 根或仓库根）
- `hrms/`：Django 应用或项目目录（包含 `settings.py`, `urls.py`, `wsgi.py`, `asgi.py` 等）
- `system/`：Django app（包含 `models.py`, `views.py`, `serializers.py`, `urls.py` 等）
- `migrations/`：数据库迁移文件

技术栈 & 要点
- Python（pyproject 标明 requires-python >= 3.12）
- Django 5.x（通过 `requirements.txt`）
- Django REST framework 用于 API
- SQLite 数据库（开发/示例用）

常用运行/开发命令（在 `cmd.exe` 环境下）
1. 创建或激活虚拟环境（示例）
   - python -m venv .venv
   - .venv\Scripts\activate
2. 安装依赖
   - pip install -r backend\requirements.txt
3. 运行数据库迁移
   - python backend\manage.py migrate
4. 启动开发服务器
   - python backend\manage.py runserver 0.0.0.0:8000

备注
- `backend/README.md` 文件存在但为空（没有启动或配置说明）。
- `pyproject.toml` 中仅有基本信息，依赖主要由 `requirements.txt` 管理。

## 三、前端（frontend）
路径：`frontend/`

主要内容（已观察到）
- `index.html`：入口 HTML（加载 `/src/main.js`）
- `package.json`：项目元数据与依赖（该前端基于 RuoYi）
  - 依赖（部分）：Vue 3, Element Plus, axios, pinia, vue-router, echarts 等
  - 开发依赖：vite, @vitejs/plugin-vue, unplugin-auto-import 等
  - 脚本（部分）：`dev`（vite）、`build:prod`、`build:stage`、`preview`
- `src/`：前端源码（包含 `App.vue`, `main.js`, `views/`, `components/`, `api/`, `utils/` 等）
- `public/`, `html/`, `bin/`（包含构建、运行脚本：`bin\\run-web.bat`, `bin\\build.bat` 等）
- `vite/`：Vite 插件或配置片段
- `LICENSE`、`README.md`（README 非空，包含大量 RuoYi 文档）

技术栈 & 要点
- Vue 3 + Vite + Element Plus
- Pinia 用于状态管理
- 项目显然是基于开源 RuoYi 前端模版（RuoYi v3.9.0）
- 构建工具：Vite

常用运行/开发命令（在 `cmd.exe` 环境下）
1. 安装依赖
   - npm install
   或（如果你偏好 yarn）
   - yarn
2. 启动开发服务器
   - npm run dev
   或
   - yarn dev
3. 构建（生产/测试）
   - npm run build:prod
   - npm run build:stage

备注
- `frontend/README.md` 包含 RuoYi 使用与启动说明（建议参照其中步骤）。
- `bin\\run-web.bat` 可用于在 Windows 环境下快速启动前端（检查该脚本以确认具体 command）。

## 四、关键文件与作用（快速索引）
- `backend/manage.py`：Django 管理命令入口（运行服务器、迁移等）
- `backend/pyproject.toml`：项目元信息（Python 版本等）
- `backend/requirements.txt`：后端依赖
- `backend/hrms/`：Django 项目配置（settings, urls）
- `backend/system/`：业务 app（models/serializers/views）
- `frontend/package.json`：前端依赖与脚本
- `frontend/index.html`：前端入口 HTML（Vite dev server 会提供）
- `bin/*.bat`：项目提供的 Windows 批处理脚本（构建/运行等）

## 五、如何在本地运行（推荐的顺序）
示例：在 Windows（cmd.exe）上
1. 后端（Python/Django）
   - cd d:\\svn\\xujia\\常用脚本\\code_store\\web-hrms\\backend
   - python -m venv .venv
   - .venv\Scripts\activate
   - pip install -r requirements.txt
   - python manage.py migrate
   - python manage.py runserver 0.0.0.0:8000
2. 前端（Vite）
   - cd d:\\svn\\xujia\\常用脚本\\code_store\\web-hrms\\frontend
   - npm install
   - npm run dev
3. 在开发阶段，前端通常会在默认端口（如 5173）运行，后端在 8000。根据前端配置，可能需要调整代理或环境变量以正确调用后端 API。

## 六、注意事项与建议
- 后端 `pyproject.toml` 声明 Python >=3.12，请使用匹配版本的 Python 环境。
- 仓库包含 `db.sqlite3`：可能含示例/测试数据，注意不要在生产环境中直接使用。
- `backend/README.md` 为空，建议补充启动、环境变量与默认管理员账号信息。
- 前端基于 RuoYi：如需要自定义主题或组件，请查看 `src/` 目录中的 `components`、`plugins`、`views`。
- 若需 docker 化或生产部署，建议新增 Dockerfile、docker-compose 或更详细的部署说明。
- 如果你想我把本 Markdown 保存为文件（例如 `PROJECT_STRUCTURE.md` 或更新 `README.md`），我可以直接写入仓库并提交修改（仅在你确认保存位置和文件名后执行）。

## 七、附：我从仓库读取到的关键片段（概要）
- `backend/pyproject.toml`：项目名 backend，requires-python = ">=3.12"
- `backend/requirements.txt`：asgiref==3.10.0, Django==5.2.8, djangorestframework==3.16.1, sqlparse==0.5.3, tzdata==2025.2
- `frontend/package.json`：Vue 3、Element Plus、Vite 等依赖；脚本：`dev`, `build:prod`, `build:stage`, `preview`
- `frontend/index.html`：Vite + SPA 入口，加载 `/src/main.js`，标题 “若依管理系统”

---

文件由分析工具自动生成。若需要我替换或追加更多细节（例如环境变量示例、启动脚本具体参数或 Docker 文件），请告诉我。
