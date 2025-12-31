#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
自定义Web环境，支持实时消息推送
"""

import asyncio
from typing import Callable, Optional, Any
from pydantic import Field

from metagpt.environment import Environment
from metagpt.roles import Role
from metagpt.schema import Message, SerializationMixin
from metagpt.logs import logger
from metagpt.utils.common import any_to_name


class WebEnvironment(Environment, SerializationMixin):
    """Web环境，支持实时消息推送到前端"""

    message_callback: Optional[Callable] = Field(default=None, exclude=True)
    agent_status_callback: Optional[Callable] = Field(default=None, exclude=True)
    thinking_callback: Optional[Callable] = Field(default=None, exclude=True)
    llm_callback: Optional[Callable] = Field(default=None, exclude=True)
    tool_callback: Optional[Callable] = Field(default=None, exclude=True)
    cost_callback: Optional[Callable] = Field(default=None, exclude=True)

    def set_callbacks(
        self,
        message_callback: Optional[Callable] = None,
        agent_status_callback: Optional[Callable] = None,
        thinking_callback: Optional[Callable] = None,
        llm_callback: Optional[Callable] = None,
        tool_callback: Optional[Callable] = None,
        cost_callback: Optional[Callable] = None,
    ):
        """设置各种回调函数"""
        if message_callback:
            self.message_callback = message_callback
        if agent_status_callback:
            self.agent_status_callback = agent_status_callback
        if thinking_callback:
            self.thinking_callback = thinking_callback
        if llm_callback:
            self.llm_callback = llm_callback
        if tool_callback:
            self.tool_callback = tool_callback
        if cost_callback:
            self.cost_callback = cost_callback

    def publish_message(self, message: Message, peekable: bool = True, publicer: str = "") -> bool:
        """重写消息发布，同时推送到前端
        
        Args:
            message: 要发布的消息
            peekable: 是否可以被其他角色窥视
            publicer: 发布者名称（兼容 TeamLeader 调用）
        """
        result = super().publish_message(message, peekable)

        # 推送消息到WebSocket
        if self.message_callback:
            try:
                msg_data = {
                    "type": "message",
                    "id": message.id,
                    "content": message.content,
                    "role": message.role,
                    "sent_from": str(message.sent_from) if message.sent_from else "User",
                    "send_to": list(message.send_to) if message.send_to else [],
                    "cause_by": str(message.cause_by) if message.cause_by else "",
                }
                asyncio.create_task(self._safe_callback(self.message_callback, msg_data))
            except Exception as e:
                logger.warning(f"Failed to push message: {e}")

        return result

    async def _safe_callback(self, callback: Callable, data: Any):
        """安全地执行回调"""
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(data)
            else:
                callback(data)
        except Exception as e:
            logger.warning(f"Callback error: {e}")

    async def run(self, k=1):
        """重写run方法，跟踪每个agent的工作状态"""
        logger.info(f"WebEnvironment.run called with k={k}")
        for i in range(k):
            logger.info(f"Round {i+1}/{k}, checking roles...")
            futures = []
            for role in self.roles.values():
                logger.info(f"  Role {role.name}: is_idle={role.is_idle}, msg_buffer_empty={role.rc.msg_buffer.empty()}")
                if role.is_idle:
                    continue
                future = self._run_role_with_tracking(role)
                futures.append(future)

            logger.info(f"  Active roles: {len(futures)}")
            if futures:
                await asyncio.gather(*futures)
            logger.debug(f"is idle: {self.is_idle}")

    async def _run_role_with_tracking(self, role: Role):
        """运行角色并跟踪状态"""
        logger.info(f"  Running role {role.name}...")
        
        # 推送agent开始工作状态
        if self.agent_status_callback:
            await self._safe_callback(
                self.agent_status_callback,
                {
                    "type": "agent_status",
                    "agent_name": role.name,
                    "profile": role.profile,
                    "status": "working",
                    "action": role.action_description or "思考中...",
                },
            )

        try:
            # 运行角色
            result = await role.run()
            logger.info(f"  Role {role.name} finished, result: {type(result)}, content_len: {len(result.content) if result and result.content else 0}")

            # 如果有结果，推送思考过程
            if result and self.thinking_callback:
                await self._safe_callback(
                    self.thinking_callback,
                    {
                        "type": "thinking",
                        "agent_name": role.name,
                        "profile": role.profile,
                        "action": any_to_name(result.cause_by) if result.cause_by else "",
                        "content": result.content[:1000] if result.content else "",  # 截取前1000字符
                    },
                )
            
            # 如果角色完成了任务（不是 TeamLeader），将结果发送给 TeamLeader
            # 这样 TeamLeader 可以继续分配下一个任务
            if result and role.profile != "Team Leader" and result.content:
                from metagpt.const import TEAMLEADER_NAME
                team_leader = self.roles.get(TEAMLEADER_NAME)
                if team_leader and team_leader.name != role.name:
                    # 创建一个通知消息给 TeamLeader
                    from metagpt.actions.di.run_command import RunCommand
                    notification = Message(
                        content=f"[{role.profile} {role.name} 完成任务报告]\n{result.content[:500]}",
                        role="user",
                        cause_by=RunCommand,
                        send_to={TEAMLEADER_NAME},
                        sent_from=role.name,
                    )
                    # 将消息放入 TeamLeader 的消息缓冲区
                    team_leader.put_message(notification)
                    logger.info(f"Forwarded {role.name}'s result to TeamLeader")

        except Exception as e:
            logger.error(f"Role {role.name} run error: {e}")
            import traceback
            logger.error(traceback.format_exc())
            if self.agent_status_callback:
                await self._safe_callback(
                    self.agent_status_callback,
                    {
                        "type": "agent_status",
                        "agent_name": role.name,
                        "profile": role.profile,
                        "status": "error",
                        "error": str(e),
                    },
                )
            raise

        # 推送agent完成状态
        if self.agent_status_callback:
            await self._safe_callback(
                self.agent_status_callback,
                {
                    "type": "agent_status",
                    "agent_name": role.name,
                    "profile": role.profile,
                    "status": "idle",
                },
            )

    async def push_llm_call(self, agent_name: str, model: str, prompt: str, response: str, 
                           cost: float = 0, tokens: dict = None, total_cost: float = 0):
        """推送LLM调用信息"""
        if self.llm_callback:
            await self._safe_callback(
                self.llm_callback,
                {
                    "type": "llm_call",
                    "agent_name": agent_name,
                    "model": model,
                    "prompt": prompt[:500] if prompt else "",  # 截断过长的prompt
                    "response": response[:1000] if response else "",  # 截断过长的response
                    "cost": cost,
                    "tokens": tokens,
                    "total_cost": total_cost,
                },
            )

    async def push_tool_usage(self, agent_name: str, tool_name: str, args: dict = None, result: str = ""):
        """推送工具使用信息"""
        if self.tool_callback:
            await self._safe_callback(
                self.tool_callback,
                {
                    "type": "tool_usage",
                    "agent_name": agent_name,
                    "tool_name": tool_name,
                    "args": args,
                    "result": result[:500] if result else "",  # 截断过长的结果
                },
            )

    async def push_cost_update(self, total_cost: float):
        """推送花费更新"""
        if self.cost_callback:
            await self._safe_callback(
                self.cost_callback,
                {
                    "type": "cost_update",
                    "total_cost": total_cost,
                },
            )

    def get_employees_info(self) -> list:
        """获取所有员工信息"""
        employees = []
        for role in self.roles.values():
            employees.append(
                {
                    "name": role.name,
                    "profile": role.profile,
                    "goal": role.goal,
                    "constraints": getattr(role, 'constraints', ''),
                    "desc": getattr(role, 'desc', ''),
                    "is_idle": role.is_idle,
                }
            )
        return employees

    def __repr__(self):
        return f"WebEnvironment(roles={list(self.roles.keys())})"
