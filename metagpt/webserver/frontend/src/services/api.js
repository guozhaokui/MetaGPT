/**
 * API 服务
 */

const API_BASE = '/api'

async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`
  const config = {
    headers: {
      'Content-Type': 'application/json',
    },
    ...options,
  }

  if (config.body && typeof config.body === 'object') {
    config.body = JSON.stringify(config.body)
  }

  const response = await fetch(url, config)
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(error.detail || `HTTP ${response.status}`)
  }
  
  return response.json()
}

export default {
  // 项目列表
  getProjects() {
    return request('/projects')
  },

  // 项目详情
  getProject(id) {
    return request(`/projects/${id}`)
  },

  // 创建项目
  createProject(data) {
    return request('/projects', {
      method: 'POST',
      body: data,
    })
  },

  // 更新项目
  updateProject(id, data) {
    return request(`/projects/${id}`, {
      method: 'PUT',
      body: data,
    })
  },

  // 删除项目
  deleteProject(id) {
    return request(`/projects/${id}`, {
      method: 'DELETE',
    })
  },

  // 启动项目
  startProject(id) {
    return request(`/projects/${id}/start`, {
      method: 'POST',
    })
  },

  // 停止项目
  stopProject(id) {
    return request(`/projects/${id}/stop`, {
      method: 'POST',
    })
  },

  // 获取消息历史
  getMessages(id) {
    return request(`/projects/${id}/messages`)
  },
}

