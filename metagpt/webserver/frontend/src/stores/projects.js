import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useNotification } from './notification'
import api from '@/services/api'

export const useProjectStore = defineStore('projects', () => {
  // State
  const projects = ref([])
  const currentProjectId = ref(null)
  const currentProject = ref(null)
  const loading = ref(false)
  const messages = ref([])
  const thinkingLogs = ref([])
  const llmCalls = ref([])  // LLM调用记录
  const toolUsages = ref([])  // 工具使用记录

  // Getters
  const projectList = computed(() => projects.value)
  const hasProjects = computed(() => projects.value.length > 0)
  const isRunning = computed(() => currentProject.value?.status === 'running')

  // Actions
  async function fetchProjects() {
    loading.value = true
    try {
      projects.value = await api.getProjects()
    } catch (error) {
      useNotification().error('加载项目列表失败')
    } finally {
      loading.value = false
    }
  }

  async function fetchProject(id) {
    loading.value = true
    try {
      currentProject.value = await api.getProject(id)
      currentProjectId.value = id
    } catch (error) {
      useNotification().error('加载项目详情失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  async function createProject(projectData) {
    try {
      const project = await api.createProject(projectData)
      await fetchProjects()
      useNotification().success('项目创建成功！')
      return project
    } catch (error) {
      useNotification().error('创建项目失败')
      throw error
    }
  }

  async function updateProject(id, data) {
    try {
      await api.updateProject(id, data)
      if (currentProjectId.value === id) {
        await fetchProject(id)
      }
    } catch (error) {
      useNotification().error('更新项目失败')
      throw error
    }
  }

  async function deleteProject(id) {
    try {
      await api.deleteProject(id)
      if (currentProjectId.value === id) {
        currentProject.value = null
        currentProjectId.value = null
      }
      await fetchProjects()
      useNotification().success('项目已删除')
    } catch (error) {
      useNotification().error('删除项目失败')
      throw error
    }
  }

  async function startProject(id) {
    try {
      await api.startProject(id)
      useNotification().success('项目开始运行！')
    } catch (error) {
      useNotification().error('启动项目失败')
      throw error
    }
  }

  async function stopProject(id) {
    try {
      await api.stopProject(id)
      useNotification().warning('项目已停止')
    } catch (error) {
      useNotification().error('停止项目失败')
      throw error
    }
  }

  // WebSocket message handlers
  function addMessage(msg) {
    messages.value.push({
      ...msg,
      timestamp: msg.timestamp || new Date().toISOString(),
    })
  }

  function addThinking(log) {
    thinkingLogs.value.push({
      ...log,
      id: Date.now() + Math.random(),
      timestamp: log.timestamp || new Date().toISOString(),
    })
  }

  // 添加LLM调用记录
  function addLLMCall(call) {
    llmCalls.value.push({
      ...call,
      id: Date.now() + Math.random(),
      timestamp: call.timestamp || new Date().toISOString(),
    })
  }

  // 添加工具使用记录
  function addToolUsage(usage) {
    toolUsages.value.push({
      ...usage,
      id: Date.now() + Math.random(),
      timestamp: usage.timestamp || new Date().toISOString(),
    })
    
    // 同时添加到思考日志中
    addThinking({
      agent_name: usage.agent_name,
      action: `🔧 ${usage.tool_name}`,
      content: `调用工具: ${usage.tool_name}\n参数: ${JSON.stringify(usage.args, null, 2)}\n结果: ${usage.result || '执行中...'}`,
      type: 'tool',
    })
  }

  function updateEmployees(employees) {
    if (currentProject.value) {
      currentProject.value.employees = employees
    }
  }

  function updateStatus(status) {
    if (currentProject.value) {
      currentProject.value.status = status
    }
    // 更新列表中的状态
    const project = projects.value.find(p => p.id === currentProjectId.value)
    if (project) {
      project.status = status
    }
  }

  function updateCost(cost) {
    if (currentProject.value) {
      currentProject.value.total_cost = cost
    }
    // 更新列表中的花费
    const project = projects.value.find(p => p.id === currentProjectId.value)
    if (project) {
      project.total_cost = cost
    }
  }

  function updateEmployeeStatus(data) {
    if (!currentProject.value?.employees) return
    
    const employee = currentProject.value.employees.find(
      e => e.name === data.agent_name
    )
    if (employee) {
      employee.is_idle = data.status === 'idle'
      employee.current_action = data.action || ''
    }
  }

  function clearMessages() {
    messages.value = []
    thinkingLogs.value = []
    llmCalls.value = []
    toolUsages.value = []
  }

  function reset() {
    currentProject.value = null
    currentProjectId.value = null
    messages.value = []
    thinkingLogs.value = []
    llmCalls.value = []
    toolUsages.value = []
  }

  return {
    // State
    projects,
    currentProjectId,
    currentProject,
    loading,
    messages,
    thinkingLogs,
    llmCalls,
    toolUsages,
    
    // Getters
    projectList,
    hasProjects,
    isRunning,
    
    // Actions
    fetchProjects,
    fetchProject,
    createProject,
    updateProject,
    deleteProject,
    startProject,
    stopProject,
    addMessage,
    addThinking,
    addLLMCall,
    addToolUsage,
    updateEmployees,
    updateStatus,
    updateCost,
    updateEmployeeStatus,
    clearMessages,
    reset,
  }
})
