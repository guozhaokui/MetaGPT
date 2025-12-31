<template>
  <aside class="sidebar">
    <!-- Logo区 -->
    <div class="sidebar-header">
      <div class="logo">
        <span class="logo-icon">🤖</span>
        <span class="logo-text">MetaGPT</span>
      </div>
      <button class="btn-new-project" @click="modalStore.showCreateProject()">
        <span>+</span> 新建项目
      </button>
    </div>

    <!-- 项目列表 -->
    <div class="section-title">📁 项目列表</div>
    <div class="project-list">
      <div v-if="projectStore.loading" class="loading">
        加载中...
      </div>

      <div v-else-if="!projectStore.hasProjects" class="empty-state">
        暂无项目
      </div>

      <template v-else>
        <div
          v-for="project in projectStore.projectList"
          :key="project.id"
          class="project-item"
          :class="{ active: project.id === projectStore.currentProjectId }"
          @click="selectProject(project.id)"
        >
          <div class="project-item-header">
            <span class="project-item-name">{{ project.name }}</span>
            <div class="project-actions">
              <!-- 运行按钮 -->
              <button
                v-if="project.status === 'created' || project.status === 'stopped'"
                class="action-btn run"
                @click.stop="startProject(project.id)"
                title="运行项目"
              >
                ▶
              </button>
              <!-- 暂停按钮 -->
              <button
                v-if="project.status === 'running'"
                class="action-btn pause"
                @click.stop="pauseProject(project.id)"
                title="暂停项目"
              >
                ⏸
              </button>
              <!-- 继续按钮 -->
              <button
                v-if="project.status === 'paused'"
                class="action-btn resume"
                @click.stop="resumeProject(project.id)"
                title="继续运行"
              >
                ▶
              </button>
              <!-- 停止按钮（运行中或暂停时可用） -->
              <button
                v-if="project.status === 'running' || project.status === 'paused'"
                class="action-btn stop"
                @click.stop="stopProject(project.id)"
                title="停止项目"
              >
                ⏹
              </button>
              <span class="status-dot" :class="project.status"></span>
            </div>
          </div>
          <div class="project-item-meta">
            <span class="cost">${{ (project.total_cost || 0).toFixed(2) }}</span>
            <span class="status-text">{{ statusText(project.status) }}</span>
          </div>
        </div>
      </template>
    </div>

    <!-- 当前项目详情（可展开） -->
    <div v-if="projectStore.currentProject" class="current-project-section">
      <div class="section-title clickable" @click="showProjectDetails = !showProjectDetails">
        <span>📋 项目详情</span>
        <span class="toggle-icon">{{ showProjectDetails ? '▼' : '▶' }}</span>
      </div>
      
      <Transition name="slide">
        <div v-if="showProjectDetails" class="project-details">
          <div class="detail-row">
            <span class="label">需求:</span>
            <span class="value idea">{{ projectStore.currentProject.idea }}</span>
          </div>
          <div class="detail-row">
            <span class="label">预算:</span>
            <span class="value">${{ projectStore.currentProject.investment }}</span>
          </div>
          <div class="detail-row">
            <span class="label">花费:</span>
            <span class="value cost">${{ (projectStore.currentProject.total_cost || 0).toFixed(4) }}</span>
          </div>
          <div class="detail-row">
            <span class="label">轮次:</span>
            <span class="value">{{ projectStore.currentProject.n_round }}</span>
          </div>
        </div>
      </Transition>
    </div>

    <!-- 团队成员 -->
    <div v-if="projectStore.currentProject" class="team-section">
      <div class="section-title">👥 团队成员</div>
      <div class="team-list">
        <div
          v-for="employee in projectStore.currentProject.employees || []"
          :key="employee.name"
          class="team-member"
          :class="{ working: !employee.is_idle }"
        >
          <span class="status-indicator" :class="employee.is_idle ? 'idle' : 'working'"></span>
          <span class="member-profile">{{ employee.profile }}</span>
          <span class="member-name">{{ employee.name }}</span>
        </div>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useProjectStore } from '@/stores/projects'
import { useModalStore } from '@/stores/modal'

const router = useRouter()
const projectStore = useProjectStore()
const modalStore = useModalStore()

const showProjectDetails = ref(false)

const statusText = (status) => {
  const map = {
    created: '已创建',
    running: '运行中',
    paused: '已暂停',
    completed: '已完成',
    failed: '失败',
    stopped: '已停止',
  }
  return map[status] || status
}

const selectProject = (id) => {
  router.push(`/project/${id}`)
}

const startProject = async (id) => {
  try {
    await projectStore.startProject(id)
    // 如果不是当前项目，跳转过去
    if (id !== projectStore.currentProjectId) {
      router.push(`/project/${id}`)
    }
  } catch (error) {
    console.error('Start project failed:', error)
  }
}

const stopProject = async (id) => {
  try {
    await projectStore.stopProject(id)
  } catch (error) {
    console.error('Stop project failed:', error)
  }
}

const pauseProject = async (id) => {
  try {
    await projectStore.pauseProject(id)
  } catch (error) {
    console.error('Pause project failed:', error)
  }
}

const resumeProject = async (id) => {
  try {
    await projectStore.resumeProject(id)
  } catch (error) {
    console.error('Resume project failed:', error)
  }
}

onMounted(() => {
  projectStore.fetchProjects()
})
</script>

<style lang="scss" scoped>
.sidebar {
  width: 260px;
  background: var(--bg-secondary);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  overflow-y: auto;
}

.sidebar-header {
  padding: 16px;
  border-bottom: 1px solid var(--border-color);
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
}

.logo-icon {
  font-size: 24px;
}

.logo-text {
  font-size: 18px;
  font-weight: 600;
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-purple));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.btn-new-project {
  width: 100%;
  padding: 8px 14px;
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-purple));
  color: white;
  border: none;
  border-radius: var(--border-radius);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  transition: var(--transition-normal);

  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(88, 166, 255, 0.3);
  }
}

.section-title {
  padding: 10px 16px 6px;
  font-size: 11px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  display: flex;
  justify-content: space-between;
  align-items: center;

  &.clickable {
    cursor: pointer;
    &:hover {
      color: var(--text-secondary);
    }
  }
}

.toggle-icon {
  font-size: 10px;
}

.project-list {
  flex: 1;
  overflow-y: auto;
  padding: 0 10px 10px;
  min-height: 100px;
  max-height: 200px;
}

.project-item {
  padding: 10px 12px;
  margin-bottom: 4px;
  border-radius: var(--border-radius);
  cursor: pointer;
  transition: var(--transition-fast);
  border: 1px solid transparent;
  background: var(--bg-tertiary);

  &:hover {
    border-color: var(--border-color);
  }

  &.active {
    border-color: var(--accent-primary);
    background: rgba(88, 166, 255, 0.1);
  }
}

.project-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.project-item-name {
  font-size: 13px;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 140px;
}

.project-actions {
  display: flex;
  align-items: center;
  gap: 6px;
}

.action-btn {
  width: 22px;
  height: 22px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: var(--transition-fast);
  opacity: 0;

  .project-item:hover & {
    opacity: 1;
  }

  &.run {
    background: rgba(63, 185, 80, 0.2);
    color: var(--accent-success);

    &:hover {
      background: rgba(63, 185, 80, 0.4);
      transform: scale(1.1);
    }
  }

  &.pause {
    background: rgba(255, 166, 87, 0.2);
    color: var(--accent-warning);
    opacity: 1;

    &:hover {
      background: rgba(255, 166, 87, 0.4);
      transform: scale(1.1);
    }
  }

  &.resume {
    background: rgba(63, 185, 80, 0.2);
    color: var(--accent-success);
    opacity: 1;

    &:hover {
      background: rgba(63, 185, 80, 0.4);
      transform: scale(1.1);
    }
  }

  &.stop {
    background: rgba(248, 81, 73, 0.2);
    color: var(--accent-danger);
    opacity: 1;

    &:hover {
      background: rgba(248, 81, 73, 0.4);
      transform: scale(1.1);
    }
  }
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;

  &.created { background: var(--text-muted); }
  &.running { background: var(--accent-primary); animation: pulse 1.5s infinite; }
  &.paused { background: var(--accent-warning); }
  &.completed { background: var(--accent-success); }
  &.failed { background: var(--accent-danger); }
  &.stopped { background: #6e7681; }
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.6; transform: scale(0.9); }
}

.project-item-meta {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: var(--text-muted);
}

.cost {
  color: var(--accent-success);
  font-family: var(--font-mono);
}

// 项目详情
.current-project-section {
  border-top: 1px solid var(--border-color);
  padding-bottom: 10px;
}

.project-details {
  padding: 0 16px;
}

.detail-row {
  display: flex;
  gap: 8px;
  padding: 4px 0;
  font-size: 12px;

  .label {
    color: var(--text-muted);
    flex-shrink: 0;
  }

  .value {
    color: var(--text-primary);
    
    &.idea {
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }

    &.cost {
      color: var(--accent-success);
      font-family: var(--font-mono);
    }
  }
}

// 团队成员
.team-section {
  border-top: 1px solid var(--border-color);
  flex-shrink: 0;
}

.team-list {
  padding: 0 10px 10px;
}

.team-member {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 10px;
  margin-bottom: 2px;
  border-radius: var(--border-radius);
  font-size: 12px;
  transition: var(--transition-fast);

  &.working {
    background: rgba(88, 166, 255, 0.1);
  }
}

.status-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;

  &.idle {
    background: #6e7681;
    box-shadow: 0 0 0 2px rgba(110, 118, 129, 0.3);
  }

  &.working {
    background: #3fb950;
    box-shadow: 0 0 0 2px rgba(63, 185, 80, 0.3);
    animation: pulse 1.5s infinite;
  }
}

.member-profile {
  color: var(--accent-cyan);
  font-size: 11px;
  min-width: 90px;
}

.member-name {
  color: var(--text-primary);
  font-weight: 500;
}

// 过渡动画
.slide-enter-active, .slide-leave-active {
  transition: all 0.2s ease;
}

.slide-enter-from, .slide-leave-to {
  opacity: 0;
  max-height: 0;
  padding-top: 0;
  padding-bottom: 0;
}

.slide-enter-to, .slide-leave-from {
  max-height: 200px;
}

.loading, .empty-state {
  text-align: center;
  padding: 20px 16px;
  color: var(--text-muted);
  font-size: 12px;
}
</style>
