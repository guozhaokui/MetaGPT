import { ref, onUnmounted } from 'vue'
import { useProjectStore } from '@/stores/projects'

export function useWebSocket() {
  const ws = ref(null)
  const isConnected = ref(false)
  const projectStore = useProjectStore()

  function connect(projectId) {
    // 先断开已有连接
    disconnect()

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl = `${protocol}//${window.location.host}/ws/${projectId}`

    ws.value = new WebSocket(wsUrl)

    ws.value.onopen = () => {
      console.log('WebSocket connected')
      isConnected.value = true
    }

    ws.value.onclose = () => {
      console.log('WebSocket disconnected')
      isConnected.value = false
    }

    ws.value.onerror = (error) => {
      console.error('WebSocket error:', error)
    }

    ws.value.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        handleMessage(data)
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error)
      }
    }
  }

  function disconnect() {
    if (ws.value) {
      ws.value.close()
      ws.value = null
    }
    isConnected.value = false
  }

  function handleMessage(data) {
    console.log('WS Message:', data.type, data)

    switch (data.type) {
      case 'connected':
        if (data.employees) {
          projectStore.updateEmployees(data.employees)
        }
        break

      case 'message':
        projectStore.addMessage(data)
        break

      case 'agent_status':
        projectStore.updateEmployeeStatus(data)
        break

      case 'thinking':
        projectStore.addThinking(data)
        break

      case 'llm_call':
        // LLM调用记录
        projectStore.addLLMCall({
          agent_name: data.agent_name,
          model: data.model,
          prompt: data.prompt,
          response: data.response,
          cost: data.cost,
          tokens: data.tokens,
        })
        // 同时更新花费
        if (data.total_cost !== undefined) {
          projectStore.updateCost(data.total_cost)
        }
        break

      case 'tool_usage':
        // 工具使用记录
        projectStore.addToolUsage({
          agent_name: data.agent_name,
          tool_name: data.tool_name,
          args: data.args,
          result: data.result,
        })
        break

      case 'cost_update':
        // 花费更新
        if (data.total_cost !== undefined) {
          projectStore.updateCost(data.total_cost)
        }
        break

      case 'project_status':
        projectStore.updateStatus(data.status)
        projectStore.addMessage({
          type: 'system',
          content: data.message,
          sent_from: 'System',
        })
        
        // 如果完成，更新花费
        if (data.status === 'completed' && data.total_cost !== undefined) {
          projectStore.updateCost(data.total_cost)
          if (projectStore.currentProject) {
            projectStore.currentProject.output_path = data.output_path || ''
          }
        }
        
        // 刷新项目列表
        projectStore.fetchProjects()
        break

      case 'employees_updated':
        projectStore.updateEmployees(data.employees)
        break

      default:
        console.log('Unknown message type:', data.type)
    }
  }

  function send(data) {
    if (ws.value && isConnected.value) {
      ws.value.send(JSON.stringify(data))
    }
  }

  // 组件卸载时自动断开连接
  onUnmounted(() => {
    disconnect()
  })

  return {
    ws,
    isConnected,
    connect,
    disconnect,
    send,
  }
}
