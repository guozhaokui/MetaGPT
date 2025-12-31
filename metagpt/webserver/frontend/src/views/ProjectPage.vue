<template>
  <div class="project-page" v-if="project">
    <!-- 项目头部 -->
    <header class="project-header">
      <div class="project-title-section">
        <h2>{{ project.name }}</h2>
        <span class="status-badge" :class="project.status">
          {{ statusText(project.status) }}
        </span>
      </div>
      <div class="project-actions">
        <button
          v-if="project.status !== 'running'"
          class="btn-primary"
          @click="handleStart"
          :disabled="project.status === 'completed'"
        >
          ▶ 开始运行
        </button>
        <button
          v-else
          class="btn-danger"
          @click="handleStop"
        >
          ⏹ 停止
        </button>
        <button class="btn-secondary" @click="handleDelete">
          🗑 删除
        </button>
      </div>
    </header>

    <!-- 项目配置区 -->
    <section class="project-config">
      <div class="config-card">
        <h3>📝 项目需求</h3>
        <textarea
          v-model="configForm.idea"
          placeholder="输入你的项目需求描述..."
          rows="2"
          :disabled="project.status === 'running'"
        ></textarea>
      </div>
      <div class="config-row">
        <div class="config-item">
          <label>💰 预算 (USD)</label>
          <input
            type="number"
            v-model.number="configForm.investment"
            min="0.1"
            step="0.1"
            :disabled="project.status === 'running'"
          />
        </div>
        <div class="config-item">
          <label>🔄 运行轮次</label>
          <input
            type="number"
            v-model.number="configForm.n_round"
            min="1"
            max="50"
            :disabled="project.status === 'running'"
          />
        </div>
        <div class="config-item">
          <label>📊 当前花费</label>
          <span class="cost-display">${{ (project.total_cost || 0).toFixed(4) }}</span>
        </div>
      </div>
    </section>

    <!-- 工作面板区 - 三栏布局 -->
    <section class="work-panels">
      <!-- 消息面板 -->
      <MessagePanel
        title="💬 消息交流"
        :messages="projectStore.messages"
        @clear="projectStore.clearMessages()"
      />

      <!-- 思考/工具面板 -->
      <ThinkingPanel
        title="🧠 思考 & 工具"
        :logs="projectStore.thinkingLogs"
      />

      <!-- LLM调用面板 -->
      <LLMPanel
        title="🤖 LLM 调用"
        :calls="projectStore.llmCalls"
        :project-id="project.id"
      />
    </section>
  </div>

  <!-- 加载状态 -->
  <div v-else-if="projectStore.loading" class="loading-page">
    <div class="loading-spinner"></div>
    <p>加载中...</p>
  </div>
</template>

<script setup>
import { computed, reactive, watch, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useProjectStore } from '@/stores/projects'
import { useWebSocket } from '@/composables/useWebSocket'
import MessagePanel from '@/components/MessagePanel.vue'
import ThinkingPanel from '@/components/ThinkingPanel.vue'
import LLMPanel from '@/components/LLMPanel.vue'

const route = useRoute()
const router = useRouter()
const projectStore = useProjectStore()
const { connect, disconnect } = useWebSocket()

const project = computed(() => projectStore.currentProject)

const configForm = reactive({
  idea: '创建一个基于web的俄罗斯方块游戏。要求实现全部流程，形成项目。不要用搜索功能。',
  investment: 5.0,
  n_round: 20,
})

const statusText = (status) => {
  const map = {
    created: '已创建',
    running: '运行中',
    completed: '已完成',
    failed: '失败',
    stopped: '已停止',
  }
  return map[status] || status
}

const loadProject = async () => {
  try {
    await projectStore.fetchProject(route.params.id)
    projectStore.clearMessages()
    
    // 同步表单数据
    if (project.value) {
      configForm.idea = project.value.idea
      configForm.investment = project.value.investment
      configForm.n_round = project.value.n_round
    }
    
    // 连接WebSocket
    connect(route.params.id)
  } catch (error) {
    router.push('/')
  }
}

const handleStart = async () => {
  // 先更新配置
  await projectStore.updateProject(route.params.id, {
    idea: configForm.idea,
    investment: configForm.investment,
    n_round: configForm.n_round,
  })
  
  // 启动项目
  await projectStore.startProject(route.params.id)
}

const handleStop = async () => {
  await projectStore.stopProject(route.params.id)
}

const handleDelete = async () => {
  if (!confirm('确定要删除这个项目吗？此操作不可恢复。')) return
  
  await projectStore.deleteProject(route.params.id)
  router.push('/')
}

// 监听路由变化
watch(() => route.params.id, (newId) => {
  if (newId) {
    loadProject()
  }
})

onMounted(() => {
  loadProject()
})

onUnmounted(() => {
  disconnect()
  projectStore.reset()
})
</script>

<style lang="scss" scoped>
.project-page {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.project-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-color);
}

.project-title-section {
  display: flex;
  align-items: center;
  gap: 12px;

  h2 {
    font-size: 20px;
    font-weight: 600;
  }
}

.project-actions {
  display: flex;
  gap: 8px;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 500;
  text-transform: uppercase;

  &.created { background: var(--bg-tertiary); color: var(--text-secondary); }
  &.running { 
    background: rgba(88, 166, 255, 0.2); 
    color: var(--accent-primary);
    animation: pulse 2s infinite;
  }
  &.completed { background: rgba(63, 185, 80, 0.2); color: var(--accent-success); }
  &.failed { background: rgba(248, 81, 73, 0.2); color: var(--accent-danger); }
  &.stopped { background: rgba(210, 153, 34, 0.2); color: var(--accent-warning); }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

// 配置区
.project-config {
  background: var(--bg-card);
  border-radius: var(--border-radius-lg);
  padding: 16px;
  border: 1px solid var(--border-color);
}

.config-card {
  h3 {
    margin-bottom: 10px;
    font-size: 13px;
    color: var(--text-secondary);
  }

  textarea {
    width: 100%;
    padding: 10px;
    background: var(--bg-tertiary);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius);
    color: var(--text-primary);
    font-family: var(--font-sans);
    font-size: 13px;
    resize: vertical;
    min-height: 60px;

    &:focus {
      outline: none;
      border-color: var(--accent-primary);
    }

    &:disabled {
      opacity: 0.6;
      cursor: not-allowed;
    }
  }
}

.config-row {
  display: flex;
  gap: 16px;
  margin-top: 12px;
}

.config-item {
  flex: 1;

  label {
    display: block;
    margin-bottom: 6px;
    font-size: 12px;
    color: var(--text-secondary);
  }

  input {
    width: 100%;
    padding: 8px 10px;
    background: var(--bg-tertiary);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius);
    color: var(--text-primary);
    font-size: 13px;

    &:focus {
      outline: none;
      border-color: var(--accent-primary);
    }

    &:disabled {
      opacity: 0.6;
      cursor: not-allowed;
    }
  }
}

.cost-display {
  display: block;
  font-size: 20px;
  font-weight: 600;
  font-family: var(--font-mono);
  color: var(--accent-success);
}

// 工作面板 - 三栏
.work-panels {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  flex: 1;
  min-height: 300px;
}

// 按钮
.btn-primary, .btn-secondary, .btn-danger {
  padding: 8px 16px;
  border-radius: var(--border-radius);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition-fast);
}

.btn-primary {
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-purple));
  color: white;
  border: none;

  &:hover:not(:disabled) {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(88, 166, 255, 0.3);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

.btn-secondary {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);

  &:hover {
    background: var(--bg-hover);
  }
}

.btn-danger {
  background: rgba(248, 81, 73, 0.2);
  color: var(--accent-danger);
  border: 1px solid var(--accent-danger);

  &:hover {
    background: rgba(248, 81, 73, 0.3);
  }
}

// 加载页面
.loading-page {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  color: var(--text-muted);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--border-color);
  border-top-color: var(--accent-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

// 响应式
@media (max-width: 1400px) {
  .work-panels {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 1000px) {
  .work-panels {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .config-row {
    flex-direction: column;
  }

  .project-header {
    flex-direction: column;
    gap: 12px;
  }

  .project-actions {
    width: 100%;
    justify-content: flex-end;
  }
}
</style>
