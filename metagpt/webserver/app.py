#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MetaGPT Web Server 主应用
提供REST API和WebSocket接口
"""

import asyncio
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from metagpt.config2 import config
from metagpt.context import Context
from metagpt.team import Team
from metagpt.roles import (
    ProductManager,
    Architect,
    Engineer2,
    DataAnalyst,
    TeamLeader,
    Engineer,
    ProjectManager,
    QaEngineer,
)
from metagpt.webserver.web_env import WebEnvironment
from metagpt.logs import logger
from metagpt.schema import Message
from metagpt.actions import UserRequirement

# ============ Pydantic Models ============


class ProjectCreate(BaseModel):
    """创建项目的请求模型"""

    name: str = Field(..., description="项目名称")
    idea: str = Field(..., description="项目提示词/需求描述")
    investment: float = Field(default=3.0, description="预算（美元）")
    n_round: int = Field(default=20, description="最大运行轮次")
    use_mgx: bool = Field(default=False, description="是否使用MGX模式")


class ProjectUpdate(BaseModel):
    """更新项目的请求模型"""

    name: Optional[str] = None
    idea: Optional[str] = None
    investment: Optional[float] = None
    n_round: Optional[int] = None


class EmployeeInfo(BaseModel):
    """员工信息"""

    name: str
    profile: str
    goal: str
    is_idle: bool = True


class ProjectInfo(BaseModel):
    """项目信息"""

    id: str
    name: str
    idea: str
    investment: float
    n_round: int
    status: str  # created, running, completed, failed
    employees: List[EmployeeInfo]
    created_at: str
    total_cost: float = 0.0
    output_path: str = ""
    error_message: str = ""


class ProjectSummary(BaseModel):
    """项目摘要"""

    id: str
    name: str
    status: str
    created_at: str


# ============ 全局状态管理 ============


class ProjectManager_:
    """项目管理器"""

    def __init__(self):
        self.projects: Dict[str, dict] = {}
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.running_tasks: Dict[str, asyncio.Task] = {}

    def create_project(self, project_data: ProjectCreate) -> str:
        """创建新项目"""
        project_id = str(uuid.uuid4())[:8]

        # 默认员工配置
        default_employees = [
            EmployeeInfo(name="Mike", profile="TeamLeader", goal="领导团队完成项目"),
            EmployeeInfo(name="Alice", profile="ProductManager", goal="创建成功的产品"),
            EmployeeInfo(name="Bob", profile="Architect", goal="设计可复用的模块化系统"),
            EmployeeInfo(name="Alex", profile="Engineer", goal="编写优雅高效的代码"),
            EmployeeInfo(name="David", profile="DataAnalyst", goal="分析数据提供洞察"),
        ]

        self.projects[project_id] = {
            "id": project_id,
            "name": project_data.name,
            "idea": project_data.idea,
            "investment": project_data.investment,
            "n_round": project_data.n_round,
            "use_mgx": project_data.use_mgx,
            "status": "created",
            "employees": [e.model_dump() for e in default_employees],
            "created_at": datetime.now().isoformat(),
            "total_cost": 0.0,
            "output_path": "",
            "error_message": "",
            "messages": [],  # 存储所有消息历史
            "team": None,
            "context": None,
        }

        return project_id

    def get_project(self, project_id: str) -> Optional[dict]:
        """获取项目"""
        return self.projects.get(project_id)

    def get_all_projects(self) -> List[dict]:
        """获取所有项目"""
        return list(self.projects.values())

    def update_project(self, project_id: str, update_data: ProjectUpdate) -> bool:
        """更新项目"""
        if project_id not in self.projects:
            return False

        project = self.projects[project_id]
        if project["status"] == "running":
            return False

        if update_data.name is not None:
            project["name"] = update_data.name
        if update_data.idea is not None:
            project["idea"] = update_data.idea
        if update_data.investment is not None:
            project["investment"] = update_data.investment
        if update_data.n_round is not None:
            project["n_round"] = update_data.n_round

        return True

    def delete_project(self, project_id: str) -> bool:
        """删除项目"""
        if project_id not in self.projects:
            return False

        project = self.projects[project_id]
        if project["status"] == "running":
            return False

        del self.projects[project_id]
        return True

    async def broadcast(self, project_id: str, data: dict):
        """向项目的所有连接广播消息"""
        if project_id in self.active_connections:
            dead_connections = []
            for ws in self.active_connections[project_id]:
                try:
                    await ws.send_json(data)
                except Exception:
                    dead_connections.append(ws)

            # 移除断开的连接
            for ws in dead_connections:
                self.active_connections[project_id].remove(ws)


# 全局项目管理器实例
project_manager = ProjectManager_()

# ============ FastAPI 应用 ============

app = FastAPI(
    title="MetaGPT Web Server",
    description="MetaGPT项目管理Web服务",
    version="1.0.0",
)

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件目录 - Vue构建输出
static_dir = Path(__file__).parent / "static_vue"

# 加载Vue构建版本
if static_dir.exists() and (static_dir / "assets").exists():
    app.mount("/assets", StaticFiles(directory=static_dir / "assets"), name="assets")


# ============ REST API ============


@app.get("/", response_class=HTMLResponse)
async def root():
    """首页"""
    index_file = static_dir / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return HTMLResponse(
        content="""
        <html>
            <head>
                <title>MetaGPT Web Server</title>
                <style>
                    body { font-family: system-ui; background: #0d1117; color: #e6edf3; 
                           display: flex; align-items: center; justify-content: center; 
                           height: 100vh; margin: 0; }
                    .container { text-align: center; }
                    h1 { color: #58a6ff; }
                    code { background: #21262d; padding: 12px 20px; border-radius: 8px; 
                           display: block; margin: 20px 0; }
                    a { color: #58a6ff; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🤖 MetaGPT Web Server</h1>
                    <p>请先构建前端:</p>
                    <code>cd metagpt/webserver/frontend && pnpm install && pnpm build</code>
                    <p>API文档: <a href="/docs">/docs</a></p>
                </div>
            </body>
        </html>
        """
    )


@app.post("/api/projects", response_model=ProjectInfo)
async def create_project(project: ProjectCreate):
    """创建新项目"""
    project_id = project_manager.create_project(project)
    project_data = project_manager.get_project(project_id)
    return ProjectInfo(
        id=project_data["id"],
        name=project_data["name"],
        idea=project_data["idea"],
        investment=project_data["investment"],
        n_round=project_data["n_round"],
        status=project_data["status"],
        employees=[EmployeeInfo(**e) for e in project_data["employees"]],
        created_at=project_data["created_at"],
        total_cost=project_data["total_cost"],
        output_path=project_data["output_path"],
        error_message=project_data["error_message"],
    )


@app.get("/api/projects", response_model=List[ProjectSummary])
async def list_projects():
    """获取所有项目列表"""
    projects = project_manager.get_all_projects()
    return [
        ProjectSummary(
            id=p["id"],
            name=p["name"],
            status=p["status"],
            created_at=p["created_at"],
        )
        for p in projects
    ]


@app.get("/api/projects/{project_id}", response_model=ProjectInfo)
async def get_project(project_id: str):
    """获取项目详情"""
    project_data = project_manager.get_project(project_id)
    if not project_data:
        raise HTTPException(status_code=404, detail="Project not found")

    return ProjectInfo(
        id=project_data["id"],
        name=project_data["name"],
        idea=project_data["idea"],
        investment=project_data["investment"],
        n_round=project_data["n_round"],
        status=project_data["status"],
        employees=[EmployeeInfo(**e) for e in project_data["employees"]],
        created_at=project_data["created_at"],
        total_cost=project_data["total_cost"],
        output_path=project_data["output_path"],
        error_message=project_data["error_message"],
    )


@app.put("/api/projects/{project_id}", response_model=ProjectInfo)
async def update_project(project_id: str, update_data: ProjectUpdate):
    """更新项目"""
    if not project_manager.update_project(project_id, update_data):
        raise HTTPException(status_code=400, detail="Cannot update project")

    return await get_project(project_id)


@app.delete("/api/projects/{project_id}")
async def delete_project(project_id: str):
    """删除项目"""
    if not project_manager.delete_project(project_id):
        raise HTTPException(status_code=400, detail="Cannot delete project")

    return {"message": "Project deleted", "project_id": project_id}


@app.post("/api/projects/{project_id}/start")
async def start_project(project_id: str):
    """开始运行项目"""
    project_data = project_manager.get_project(project_id)
    if not project_data:
        raise HTTPException(status_code=404, detail="Project not found")

    if project_data["status"] == "running":
        raise HTTPException(status_code=400, detail="Project already running")

    # 异步启动项目
    task = asyncio.create_task(run_project(project_id))
    project_manager.running_tasks[project_id] = task

    return {"message": "Project started", "project_id": project_id}


@app.post("/api/projects/{project_id}/stop")
async def stop_project(project_id: str):
    """停止运行中的项目"""
    if project_id in project_manager.running_tasks:
        task = project_manager.running_tasks[project_id]
        task.cancel()
        del project_manager.running_tasks[project_id]

        project_data = project_manager.get_project(project_id)
        if project_data:
            project_data["status"] = "stopped"

        return {"message": "Project stopped", "project_id": project_id}

    raise HTTPException(status_code=400, detail="Project is not running")


@app.get("/api/projects/{project_id}/messages")
async def get_project_messages(project_id: str):
    """获取项目的所有消息历史"""
    project_data = project_manager.get_project(project_id)
    if not project_data:
        raise HTTPException(status_code=404, detail="Project not found")

    return {"messages": project_data.get("messages", [])}


# ============ 项目运行逻辑 ============


async def run_project(project_id: str):
    """运行项目的核心逻辑"""
    project_data = project_manager.get_project(project_id)
    if not project_data:
        return

    project_data["status"] = "running"
    project_data["messages"] = []

    # 创建消息回调
    async def on_message(data: dict):
        """消息回调"""
        data["timestamp"] = datetime.now().isoformat()
        project_data["messages"].append(data)
        await project_manager.broadcast(project_id, data)

    async def on_agent_status(data: dict):
        """Agent状态回调"""
        data["timestamp"] = datetime.now().isoformat()

        # 更新员工状态
        for emp in project_data["employees"]:
            if emp["name"] == data.get("agent_name"):
                emp["is_idle"] = data.get("status") == "idle"
                break

        await project_manager.broadcast(project_id, data)

    async def on_thinking(data: dict):
        """思考过程回调"""
        data["timestamp"] = datetime.now().isoformat()
        project_data["messages"].append(data)
        await project_manager.broadcast(project_id, data)

    async def on_llm_call(data: dict):
        """LLM调用回调"""
        data["timestamp"] = datetime.now().isoformat()
        await project_manager.broadcast(project_id, data)

    async def on_tool_usage(data: dict):
        """工具使用回调"""
        data["timestamp"] = datetime.now().isoformat()
        await project_manager.broadcast(project_id, data)

    async def on_cost_update(data: dict):
        """花费更新回调"""
        if "total_cost" in data:
            project_data["total_cost"] = data["total_cost"]
        await project_manager.broadcast(project_id, data)

    try:
        # 推送开始消息
        await on_message(
            {
                "type": "project_status",
                "status": "started",
                "message": f"项目 '{project_data['name']}' 开始运行",
            }
        )

        # 创建上下文和环境
        ctx = Context(config=config)
        env = WebEnvironment(context=ctx)
        env.set_callbacks(
            message_callback=on_message,
            agent_status_callback=on_agent_status,
            thinking_callback=on_thinking,
            llm_callback=on_llm_call,
            tool_callback=on_tool_usage,
            cost_callback=on_cost_update,
        )

        # 创建团队
        company = Team(context=ctx, env=env, use_mgx=project_data.get("use_mgx", False))

        # 雇佣员工
        company.hire(
            [
                TeamLeader(),
                ProductManager(),
                Architect(),
                Engineer2(),
                DataAnalyst(),
            ]
        )

        # 更新员工信息
        project_data["employees"] = [
            {
                "name": role.name,
                "profile": role.profile,
                "goal": role.goal,
                "is_idle": role.is_idle,
            }
            for role in env.roles.values()
        ]

        # 推送员工列表
        await on_message(
            {
                "type": "employees_updated",
                "employees": project_data["employees"],
            }
        )

        # 设置投资
        company.invest(project_data["investment"])

        # 包装每个角色的 LLM，以捕获 LLM 调用的输入输出
        def wrap_llm_for_role(role, role_name: str):
            """包装角色的 LLM 以捕获调用"""
            if not hasattr(role, 'llm') or role.llm is None:
                return
            
            original_aask = role.llm.aask
            
            async def wrapped_aask(msg, system_msgs=None, format_msgs=None, images=None, timeout=None, stream=None, **kwargs):
                # 构建 prompt 摘要
                if isinstance(msg, str):
                    prompt_summary = msg[:300] if len(msg) > 300 else msg
                elif isinstance(msg, list):
                    # 提取最后一条用户消息
                    user_msgs = [m.get('content', '') for m in msg if m.get('role') == 'user']
                    prompt_summary = user_msgs[-1][:300] if user_msgs else str(msg)[:300]
                else:
                    prompt_summary = str(msg)[:300]
                
                # 调用原始方法
                result = await original_aask(msg, system_msgs, format_msgs, images, timeout, stream, **kwargs)
                
                # 获取花费信息
                cost_manager = company.cost_manager
                total_cost = cost_manager.total_cost if cost_manager else 0
                
                # 推送 LLM 调用信息
                await on_llm_call({
                    "type": "llm_call",
                    "agent_name": role_name,
                    "model": getattr(role.llm.config, 'model', 'unknown'),
                    "prompt": prompt_summary,
                    "response": result[:500] if result else "",
                    "cost": 0,  # 单次调用花费难以精确计算
                    "tokens": {
                        "prompt": cost_manager.total_prompt_tokens if cost_manager else 0,
                        "completion": cost_manager.total_completion_tokens if cost_manager else 0,
                    },
                    "total_cost": total_cost,
                })
                
                return result
            
            role.llm.aask = wrapped_aask
        
        # 包装 RoleZero 的 _run_commands 方法以捕获工具调用
        def wrap_run_commands_for_role(role, role_name: str):
            """包装角色的 _run_commands 以捕获工具调用"""
            if not hasattr(role, '_run_commands'):
                return
            
            original_run_commands = role._run_commands
            
            async def wrapped_run_commands(commands):
                # 先推送工具调用信息
                for cmd in commands:
                    cmd_name = cmd.get('command_name', 'unknown')
                    cmd_args = cmd.get('args', {})
                    await on_tool_usage({
                        "type": "tool_usage",
                        "agent_name": role_name,
                        "tool_name": cmd_name,
                        "args": cmd_args,
                        "result": "执行中...",
                    })
                
                # 执行原始方法
                result = await original_run_commands(commands)
                
                # 推送执行结果
                await on_tool_usage({
                    "type": "tool_usage",
                    "agent_name": role_name,
                    "tool_name": "命令执行完成",
                    "args": {},
                    "result": result[:300] if result else "",
                })
                
                return result
            
            role._run_commands = wrapped_run_commands
        
        # 为每个角色包装 LLM 和工具调用
        for role_name, role in env.roles.items():
            wrap_llm_for_role(role, role_name)
            wrap_run_commands_for_role(role, role_name)

        # 调试: 打印角色信息
        logger.info(f"Hired roles: {list(env.roles.keys())}")
        for role_name, role in env.roles.items():
            logger.info(f"  Role {role_name}: is_idle={role.is_idle}, watch={role.rc.watch}")

        # 运行项目 - Team.run_project() 有bug，忽略了 send_to 参数
        # 所以我们需要手动发布消息，确保消息发送给 TeamLeader (Mike)
        logger.info(f"Starting project with idea: {project_data['idea'][:50]}...")
        
        # 手动发布消息给 TeamLeader，这样他才能收到并开始分配任务
        initial_message = Message(
            content=project_data["idea"],
            role="user",  # OpenAI API 只接受 'system', 'assistant', 'user' 等标准角色
            cause_by=UserRequirement,
            send_to={"Mike"}  # 明确发送给 TeamLeader
        )
        env.publish_message(initial_message)
        company.idea = project_data["idea"]
        
        # 自定义运行循环，不像 Team.run() 那样在 is_idle 时立即退出
        # 而是运行完整的 n_round 轮，给所有角色足够的机会工作
        n_round = project_data["n_round"]
        consecutive_idle_rounds = 0
        max_idle_rounds = 3  # 连续3轮都 idle 才退出
        
        for round_num in range(1, n_round + 1):
            # 检查预算
            if company.cost_manager.total_cost >= company.cost_manager.max_budget:
                logger.warning("Budget exceeded, stopping project")
                await on_cost_update({"type": "cost_update", "total_cost": company.cost_manager.total_cost})
                break
            
            # 运行一轮
            logger.info(f"=== Round {round_num}/{n_round} ===")
            await env.run()
            
            # 推送花费更新
            await on_cost_update({"type": "cost_update", "total_cost": company.cost_manager.total_cost})
            
            # 检查是否所有角色都空闲
            if env.is_idle:
                consecutive_idle_rounds += 1
                logger.info(f"All roles idle, consecutive idle rounds: {consecutive_idle_rounds}/{max_idle_rounds}")
                if consecutive_idle_rounds >= max_idle_rounds:
                    logger.info("Max consecutive idle rounds reached, finishing project")
                    break
            else:
                consecutive_idle_rounds = 0
            
            logger.debug(f"Round {round_num} completed, {n_round - round_num} rounds left")
        
        logger.info(f"Project finished. is_idle={env.is_idle}")

        # 项目完成
        project_data["status"] = "completed"
        project_data["total_cost"] = company.cost_manager.total_cost
        project_data["output_path"] = str(ctx.kwargs.get("project_path", ""))

        await on_message(
            {
                "type": "project_status",
                "status": "completed",
                "message": f"项目完成！总花费: ${company.cost_manager.total_cost:.4f}",
                "total_cost": company.cost_manager.total_cost,
                "output_path": project_data["output_path"],
            }
        )

    except asyncio.CancelledError:
        project_data["status"] = "stopped"
        await on_message(
            {
                "type": "project_status",
                "status": "stopped",
                "message": "项目已停止",
            }
        )

    except Exception as e:
        logger.error(f"Project {project_id} failed: {e}")
        project_data["status"] = "failed"
        project_data["error_message"] = str(e)
        await on_message(
            {
                "type": "project_status",
                "status": "failed",
                "message": f"项目失败: {str(e)}",
                "error": str(e),
            }
        )

    finally:
        if project_id in project_manager.running_tasks:
            del project_manager.running_tasks[project_id]


# ============ WebSocket ============


@app.websocket("/ws/{project_id}")
async def websocket_endpoint(websocket: WebSocket, project_id: str):
    """WebSocket连接端点"""
    await websocket.accept()

    # 验证项目存在
    project_data = project_manager.get_project(project_id)
    if not project_data:
        await websocket.close(code=4004, reason="Project not found")
        return

    # 添加到活动连接
    if project_id not in project_manager.active_connections:
        project_manager.active_connections[project_id] = []
    project_manager.active_connections[project_id].append(websocket)

    # 发送当前状态
    await websocket.send_json(
        {
            "type": "connected",
            "project_id": project_id,
            "status": project_data["status"],
            "employees": project_data["employees"],
        }
    )

    # 发送历史消息
    for msg in project_data.get("messages", []):
        await websocket.send_json(msg)

    try:
        while True:
            # 保持连接，接收客户端消息
            data = await websocket.receive_text()
            # 可以处理客户端发来的命令，如停止项目等
            logger.debug(f"Received from client: {data}")

    except WebSocketDisconnect:
        # 移除连接
        if project_id in project_manager.active_connections:
            project_manager.active_connections[project_id].remove(websocket)
            if not project_manager.active_connections[project_id]:
                del project_manager.active_connections[project_id]


# ============ 健康检查 ============


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "projects_count": len(project_manager.projects),
        "running_projects": len(project_manager.running_tasks),
    }


# ============ Vue Router 历史模式支持 ============
# 必须放在所有API路由之后，作为兜底路由


@app.get("/{full_path:path}", response_class=HTMLResponse)
async def catch_all(full_path: str):
    """支持Vue Router历史模式 - 所有非API路径返回index.html"""
    index_file = static_dir / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    raise HTTPException(status_code=404)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

