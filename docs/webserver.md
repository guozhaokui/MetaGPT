# MetaGPT Web Server

基于 FastAPI + Vue 3 的 Web 服务，提供可视化界面来管理和运行 MetaGPT 项目。

## 功能特性

### 项目管理
- ✅ 添加项目，选择项目
- ✅ 提供提示词、预算参数配置
- ✅ 列出所有的员工（Agent）

### 项目运行
- ✅ 提供开始按钮
- ✅ 开始后跟踪每个 Agent 的工作情况
- ✅ 实时打印每个 Agent 的思考过程
- ✅ 交流内容写入公共面板
- ✅ 项目结束后有明确的提示和总结信息

## 技术栈

### 后端
- **FastAPI** - 高性能 Python Web 框架
- **WebSocket** - 实时双向通信
- **Pydantic** - 数据验证

### 前端 (Vue 版本)
- **Vue 3** - 渐进式 JavaScript 框架
- **Pinia** - 状态管理
- **Vue Router** - 路由管理
- **Vite** - 构建工具
- **SCSS** - 样式预处理

## 快速开始

### 1. 安装后端依赖

```bash
pip install fastapi uvicorn[standard] websockets python-multipart
# 或者
pip install -r metagpt/webserver/requirements.txt
```

### 2. 安装前端依赖并构建

```bash
cd metagpt/webserver/frontend
pnpm install
pnpm build
```

> 如果没有安装 pnpm，先运行: `npm install -g pnpm`

### 3. 启动服务

```bash
# 返回项目根目录
cd ../../..

# 启动服务
python -m metagpt.webserver.run
```

### 4. 访问界面

打开浏览器访问: http://localhost:8000

- 主页面: http://localhost:8000
- API 文档: http://localhost:8000/docs

## 开发模式

如果你想进行前端开发，可以同时启动后端和前端开发服务器：

**终端1 - 启动后端：**
```bash
python -m metagpt.webserver.run --port 8000
```

**终端2 - 启动前端开发服务器：**
```bash
cd metagpt/webserver/frontend
pnpm dev
```

前端开发服务器运行在 http://localhost:3000，会自动代理 API 请求到后端。

## 启动参数

```bash
python -m metagpt.webserver.run --help

参数:
  --host HOST          服务器主机地址 (默认: 0.0.0.0)
  --port PORT          服务器端口 (默认: 8000)
  --reload             开启热重载模式（开发用）
  --workers WORKERS    工作进程数 (默认: 1)
  --log-level LEVEL    日志级别: debug/info/warning/error (默认: info)
```

## 目录结构

```
metagpt/webserver/
├── __init__.py           # 模块入口
├── app.py                # FastAPI 应用主文件
├── web_env.py            # 自定义 WebEnvironment
├── run.py                # 启动脚本
├── requirements.txt      # Python 依赖
├── static_vue/           # Vue 构建输出目录（pnpm build 生成）
└── frontend/             # Vue 源码目录
    ├── package.json
    ├── vite.config.js
    ├── index.html
    └── src/
        ├── main.js
        ├── App.vue
        ├── router/       # 路由配置
        ├── stores/       # Pinia 状态管理
        ├── services/     # API 服务
        ├── composables/  # 组合式函数
        ├── components/   # 组件
        ├── views/        # 页面
        └── styles/       # 全局样式
```

## API 接口

### 项目管理

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/projects` | 获取所有项目列表 |
| POST | `/api/projects` | 创建新项目 |
| GET | `/api/projects/{id}` | 获取项目详情 |
| PUT | `/api/projects/{id}` | 更新项目配置 |
| DELETE | `/api/projects/{id}` | 删除项目 |
| POST | `/api/projects/{id}/start` | 开始运行项目 |
| POST | `/api/projects/{id}/stop` | 停止运行项目 |
| GET | `/api/projects/{id}/messages` | 获取项目消息历史 |

### WebSocket

- `/ws/{project_id}` - 实时接收项目状态更新

## 核心组件

### 1. WebEnvironment (`web_env.py`)

继承自 `Environment`，添加了 WebSocket 消息推送功能：

```python
class WebEnvironment(Environment):
    def set_callbacks(
        self,
        message_callback,      # 消息回调
        agent_status_callback, # Agent状态回调
        thinking_callback,     # 思考过程回调
    ):
        ...
```

### 2. Pinia Stores

- **projects.js** - 项目状态管理
- **notification.js** - 通知管理
- **modal.js** - 模态框状态

### 3. WebSocket Composable

```javascript
// 使用示例
const { connect, disconnect, isConnected } = useWebSocket()

// 连接到项目
connect(projectId)

// 自动处理消息并更新 Store
```

## WebSocket 消息类型

| 类型 | 描述 |
|------|------|
| `connected` | 连接成功 |
| `message` | 普通消息 |
| `agent_status` | Agent 状态变化 |
| `thinking` | Agent 思考过程 |
| `project_status` | 项目状态变化 |
| `employees_updated` | 员工列表更新 |

## Vue 组件结构

```
App.vue
├── Sidebar.vue           # 侧边栏（项目列表）
├── CreateProjectModal.vue # 创建项目模态框
├── Notifications.vue     # 通知组件
└── <router-view>
    ├── HomePage.vue      # 欢迎页
    └── ProjectPage.vue   # 项目详情页
        ├── EmployeeGrid.vue    # 员工卡片网格
        ├── MessagePanel.vue    # 消息面板
        ├── ThinkingPanel.vue   # 思考过程面板
        └── SummarySection.vue  # 项目总结
```

## 扩展开发

### 添加新组件

1. 在 `src/components/` 创建新的 `.vue` 文件
2. 在需要的地方导入使用

### 添加新页面

1. 在 `src/views/` 创建新的页面组件
2. 在 `src/router/index.js` 添加路由配置

### 添加新的 Store

```javascript
// src/stores/myStore.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useMyStore = defineStore('myStore', () => {
  const state = ref({})
  
  const getter = computed(() => state.value)
  
  function action() {
    // ...
  }
  
  return { state, getter, action }
})
```

### 添加新的 Agent 类型

在 `app.py` 的 `run_project` 函数中修改员工配置：

```python
company.hire([
    TeamLeader(),
    ProductManager(),
    Architect(),
    Engineer2(),
    DataAnalyst(),
    # 添加新的角色
    QaEngineer(),
])
```

## 注意事项

1. 确保已正确配置 MetaGPT 的 LLM 设置 (`~/.metagpt/config2.yaml`)
2. 项目运行需要消耗 API 配额，请注意预算设置
3. 开发模式下前端运行在 3000 端口，会代理 API 到 8000 端口
4. 生产环境建议先构建前端，然后只运行后端
5. 生产部署建议配置反向代理（如 Nginx）

## 注意

如果未构建前端，访问首页会提示构建命令。构建后的文件输出到 `static_vue/` 目录。
