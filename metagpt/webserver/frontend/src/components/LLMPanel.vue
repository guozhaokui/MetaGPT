<template>
  <div class="panel llm-panel">
    <div class="panel-header">
      <h3>{{ title }}</h3>
      <div class="header-controls">
        <span class="call-count" v-if="totalCount > 0">{{ currentIndex }}/{{ totalCount }}</span>
        <div class="nav-buttons">
          <button 
            class="nav-btn" 
            :disabled="!hasPrev || loading"
            @click="goToPrev"
            title="上一条"
          >
            ◀
          </button>
          <button 
            class="nav-btn" 
            :disabled="!hasNext || loading"
            @click="goToNext"
            title="下一条"
          >
            ▶
          </button>
          <button 
            class="nav-btn latest-btn" 
            :disabled="isLatest || loading"
            @click="goToLatest"
            title="最新"
          >
            ⏭
          </button>
        </div>
      </div>
    </div>
    <div class="panel-content" ref="contentRef">
      <div v-if="loading" class="loading-state">
        <span class="spinner"></span> 加载中...
      </div>
      <div v-else-if="!currentCall" class="empty-state">
        等待LLM调用...
      </div>
      <div v-else class="llm-detail-view">
        <div class="llm-header">
          <div class="llm-info">
            <span class="llm-agent">{{ currentCall.agent_name }}</span>
            <span class="llm-model" v-if="currentCall.model">{{ currentCall.model }}</span>
            <span class="llm-cost" v-if="currentCall.cost">${{ currentCall.cost.toFixed(4) }}</span>
          </div>
          <span class="llm-time">{{ formatTime(currentCall.timestamp) }}</span>
        </div>
        
        <div class="detail-section">
          <div class="detail-label">
            📤 请求 (Prompt)
            <span class="msg-count" v-if="fullMessages.length">{{ fullMessages.length }} 条消息</span>
          </div>
          <div class="messages-container">
            <div 
              v-for="(msg, idx) in fullMessages" 
              :key="idx" 
              class="message-item"
              :class="[msg.role, { expanded: expandedMsgs.has(idx) }]"
            >
              <div class="msg-header" @click="toggleMessage(idx)">
                <span class="toggle-icon">{{ expandedMsgs.has(idx) ? '▼' : '▶' }}</span>
                <span class="msg-role">{{ msg.role }}</span>
                <span class="msg-preview" v-if="!expandedMsgs.has(idx)">{{ truncate(msg.content, 50) }}</span>
              </div>
              <Transition name="expand">
                <pre v-if="expandedMsgs.has(idx)" class="msg-content">{{ msg.content }}</pre>
              </Transition>
            </div>
            <pre v-if="!fullMessages.length" class="detail-content prompt">{{ currentCall.prompt }}</pre>
          </div>
        </div>
        
        <div class="detail-section">
          <div class="detail-label clickable" @click="toggleResponse">
            <span class="toggle-icon">{{ responseExpanded ? '▼' : '▶' }}</span>
            📥 响应 (Response)
            <span class="msg-preview" v-if="!responseExpanded">{{ truncate(fullResponse || currentCall.response, 80) }}</span>
          </div>
          <Transition name="expand">
            <pre v-if="responseExpanded" class="detail-content response">{{ fullResponse || currentCall.response }}</pre>
          </Transition>
        </div>
        
        <div class="detail-meta" v-if="currentCall.tokens">
          <span>本次: {{ currentCall.tokens.prompt || 0 }} → {{ currentCall.tokens.completion || 0 }} tokens</span>
          <span v-if="currentCall.tokens.total_prompt"> | 累计: {{ currentCall.tokens.total_prompt }} → {{ currentCall.tokens.total_completion }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'

const props = defineProps({
  title: {
    type: String,
    default: 'LLM 调用',
  },
  calls: {
    type: Array,
    default: () => [],
  },
  projectId: {
    type: String,
    required: true,
  },
})

const route = useRoute()
const loading = ref(false)
const currentCall = ref(null)
const currentIndex = ref(0)
const totalCount = ref(0)
const hasPrev = ref(false)
const hasNext = ref(false)

// 展开/折叠状态
const expandedMsgs = ref(new Set())  // 展开的消息索引
const responseExpanded = ref(false)   // 响应是否展开

const isLatest = computed(() => currentIndex.value >= totalCount.value)

// 完整消息列表
const fullMessages = computed(() => {
  if (!currentCall.value) return []
  return currentCall.value.full_messages || []
})

// 完整响应
const fullResponse = computed(() => {
  if (!currentCall.value) return ''
  return currentCall.value.full_response || currentCall.value.response || ''
})

// 切换消息展开状态
const toggleMessage = (idx) => {
  if (expandedMsgs.value.has(idx)) {
    expandedMsgs.value.delete(idx)
  } else {
    expandedMsgs.value.add(idx)
  }
  // 触发响应式更新
  expandedMsgs.value = new Set(expandedMsgs.value)
}

// 切换响应展开状态
const toggleResponse = () => {
  responseExpanded.value = !responseExpanded.value
}

// 重置展开状态（切换记录时）
const resetExpandState = () => {
  expandedMsgs.value = new Set()
  responseExpanded.value = false
}

const formatTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return date.toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
}

const truncate = (text, length) => {
  if (!text) return ''
  const str = String(text)
  return str.length > length ? str.substring(0, length) + '...' : str
}

// 从服务器获取指定的 LLM 调用
const fetchLLMCall = async (callId) => {
  if (!props.projectId || !callId) {
    console.log('fetchLLMCall: missing projectId or callId', props.projectId, callId)
    return
  }
  
  console.log('fetchLLMCall:', callId)
  loading.value = true
  resetExpandState()  // 重置展开状态
  
  try {
    const response = await fetch(`/api/projects/${props.projectId}/llm-calls/${callId}`)
    console.log('fetchLLMCall response:', response.status)
    if (response.ok) {
      const data = await response.json()
      console.log('fetchLLMCall data:', data.id, 'prev:', data.prev_id, 'next:', data.next_id)
      currentCall.value = data
      currentIndex.value = data.index
      totalCount.value = data.total_count
      hasPrev.value = data.has_prev
      hasNext.value = data.has_next
    } else {
      console.error('fetchLLMCall failed:', response.status)
    }
  } catch (error) {
    console.error('Failed to fetch LLM call:', error)
  } finally {
    loading.value = false
  }
}

// 导航到上一条
const goToPrev = () => {
  console.log('goToPrev clicked, currentIndex:', currentIndex.value, 'hasPrev:', hasPrev.value)
  if (hasPrev.value && currentIndex.value > 1) {
    const prevId = String(currentIndex.value - 1).padStart(4, '0')
    console.log('Navigating to prev:', prevId)
    fetchLLMCall(prevId)
  }
}

// 导航到下一条
const goToNext = () => {
  console.log('goToNext clicked, currentIndex:', currentIndex.value, 'hasNext:', hasNext.value)
  if (hasNext.value && currentIndex.value < totalCount.value) {
    const nextId = String(currentIndex.value + 1).padStart(4, '0')
    console.log('Navigating to next:', nextId)
    fetchLLMCall(nextId)
  }
}

// 导航到最新
const goToLatest = () => {
  console.log('goToLatest clicked, totalCount:', totalCount.value)
  if (totalCount.value > 0) {
    const latestId = String(totalCount.value).padStart(4, '0')
    console.log('Navigating to latest:', latestId)
    fetchLLMCall(latestId)
  }
}

// 监听实时推送的新调用，自动更新到最新
watch(() => props.calls.length, (newLen, oldLen) => {
  if (newLen > oldLen && props.calls.length > 0) {
    const latestCall = props.calls[props.calls.length - 1]
    // 如果当前显示的是最新的，或者还没有显示任何调用，则自动更新
    if (isLatest.value || !currentCall.value) {
      currentCall.value = latestCall
      currentIndex.value = latestCall.index || newLen
      totalCount.value = latestCall.total_count || newLen
      hasPrev.value = currentIndex.value > 1
      hasNext.value = false
    } else {
      // 只更新总数，不切换显示
      totalCount.value = latestCall.total_count || newLen
      hasNext.value = currentIndex.value < totalCount.value
    }
  }
})

// 组件挂载时，如果有历史调用，加载最新的一条
onMounted(async () => {
  if (props.calls.length > 0) {
    const latestCall = props.calls[props.calls.length - 1]
    currentCall.value = latestCall
    currentIndex.value = latestCall.index || props.calls.length
    totalCount.value = latestCall.total_count || props.calls.length
    hasPrev.value = currentIndex.value > 1
    hasNext.value = false
  }
})
</script>

<style lang="scss" scoped>
.panel {
  background: var(--bg-card);
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-color);
  background: var(--bg-tertiary);

  h3 {
    font-size: 13px;
    font-weight: 500;
    color: var(--text-secondary);
  }
}

.header-controls {
  display: flex;
  align-items: center;
  gap: 12px;
}

.call-count {
  font-size: 11px;
  padding: 2px 8px;
  background: rgba(88, 166, 255, 0.2);
  color: var(--accent-primary);
  border-radius: 10px;
  font-family: var(--font-mono);
}

.nav-buttons {
  display: flex;
  gap: 4px;
}

.nav-btn {
  width: 28px;
  height: 24px;
  border: 1px solid var(--border-color);
  background: var(--bg-tertiary);
  color: var(--text-secondary);
  border-radius: 4px;
  cursor: pointer;
  font-size: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: var(--transition-fast);

  &:hover:not(:disabled) {
    background: var(--bg-hover);
    border-color: var(--accent-primary);
    color: var(--accent-primary);
  }

  &:disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }

  &.latest-btn {
    background: rgba(88, 166, 255, 0.15);
    border-color: var(--accent-primary);
    color: var(--accent-primary);
    
    &:hover:not(:disabled) {
      background: rgba(88, 166, 255, 0.3);
    }
  }
}

.panel-content {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
  font-size: 12px;
}

.empty-state, .loading-state {
  color: var(--text-muted);
  text-align: center;
  padding: 40px 20px;
}

.loading-state {
  .spinner {
    display: inline-block;
    width: 16px;
    height: 16px;
    border: 2px solid var(--border-color);
    border-top-color: var(--accent-primary);
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.llm-detail-view {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.llm-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--border-color);
}

.llm-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.llm-agent {
  color: var(--accent-cyan);
  font-weight: 500;
}

.llm-model {
  font-size: 10px;
  padding: 1px 6px;
  background: var(--bg-hover);
  color: var(--text-muted);
  border-radius: 8px;
}

.llm-cost {
  font-size: 10px;
  color: var(--accent-success);
  font-family: var(--font-mono);
}

.llm-time {
  color: var(--text-muted);
  font-family: var(--font-mono);
  font-size: 10px;
}

.detail-section {
  margin-bottom: 12px;
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.detail-label {
  font-size: 11px;
  color: var(--text-muted);
  margin-bottom: 6px;
  font-weight: 500;
  flex-shrink: 0;
}

.detail-content {
  font-family: var(--font-mono);
  font-size: 11px;
  padding: 10px;
  border-radius: var(--border-radius);
  flex: 1;
  overflow-y: auto;
  white-space: pre-wrap;
  word-break: break-word;
  margin: 0;
  min-height: 80px;
  max-height: 200px;

  &.prompt {
    background: rgba(88, 166, 255, 0.1);
    color: var(--accent-primary);
  }

  &.response {
    background: rgba(63, 185, 80, 0.1);
    color: var(--accent-success);
  }
}

.detail-meta {
  font-size: 10px;
  color: var(--text-muted);
  text-align: right;
  flex-shrink: 0;
  padding-top: 8px;
  border-top: 1px solid var(--border-color);
  
  span + span {
    margin-left: 8px;
  }
}

.msg-count {
  font-size: 10px;
  color: var(--accent-cyan);
  margin-left: 8px;
}

.messages-container {
  max-height: 300px;
  overflow-y: auto;
  border-radius: var(--border-radius);
  background: var(--bg-tertiary);
}

.message-item {
  border-bottom: 1px solid var(--border-color);
  
  &:last-child {
    border-bottom: none;
  }
  
  &.system {
    .msg-header { background: rgba(139, 92, 246, 0.15); }
    .msg-role { color: #a78bfa; }
    .msg-content { background: rgba(139, 92, 246, 0.08); color: #c4b5fd; }
    .msg-preview { color: #a78bfa; }
  }
  
  &.user {
    .msg-header { background: rgba(88, 166, 255, 0.15); }
    .msg-role { color: var(--accent-primary); }
    .msg-content { background: rgba(88, 166, 255, 0.08); color: var(--accent-primary); }
    .msg-preview { color: var(--accent-primary); }
  }
  
  &.assistant {
    .msg-header { background: rgba(63, 185, 80, 0.15); }
    .msg-role { color: var(--accent-success); }
    .msg-content { background: rgba(63, 185, 80, 0.08); color: var(--accent-success); }
    .msg-preview { color: var(--accent-success); }
  }
}

.msg-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 10px;
  cursor: pointer;
  transition: var(--transition-fast);
  
  &:hover {
    filter: brightness(1.1);
  }
}

.toggle-icon {
  font-size: 8px;
  color: var(--text-muted);
  flex-shrink: 0;
  width: 10px;
}

.msg-role {
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  flex-shrink: 0;
}

.msg-preview {
  font-size: 10px;
  opacity: 0.7;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
}

.msg-content {
  font-family: var(--font-mono);
  font-size: 11px;
  white-space: pre-wrap;
  word-break: break-word;
  margin: 0;
  padding: 8px 10px;
  max-height: 300px;
  overflow-y: auto;
}

.detail-label {
  &.clickable {
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 6px;
    
    &:hover {
      color: var(--text-primary);
    }
    
    .msg-preview {
      font-size: 11px;
      color: var(--text-muted);
      margin-left: 8px;
    }
  }
}

// 展开动画
.expand-enter-active, .expand-leave-active {
  transition: all 0.2s ease;
  overflow: hidden;
}

.expand-enter-from, .expand-leave-to {
  opacity: 0;
  max-height: 0;
  padding-top: 0;
  padding-bottom: 0;
}
</style>
