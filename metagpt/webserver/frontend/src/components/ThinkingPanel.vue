<template>
  <div class="panel thinking-panel">
    <div class="panel-header">
      <h3>{{ title }}</h3>
      <div class="header-actions">
        <span class="log-count" v-if="logs.length">{{ logs.length }}</span>
      </div>
    </div>
    <div class="panel-content" ref="contentRef">
      <div v-if="logs.length === 0" class="empty-state">
        等待Agent开始工作...
      </div>
      <TransitionGroup name="thinking" v-else>
        <div
          v-for="(log, index) in logs"
          :key="log.id || index"
          class="thinking-item"
          :class="{ 'is-tool': log.type === 'tool' }"
        >
          <div class="thinking-header">
            <div class="thinking-agent">
              <span class="thinking-agent-name">{{ log.agent_name }}</span>
              <span 
                class="thinking-action" 
                :class="{ 'tool-action': log.type === 'tool' }"
                v-if="log.action"
              >
                {{ log.action }}
              </span>
            </div>
            <span class="thinking-time">{{ formatTime(log.timestamp) }}</span>
          </div>
          <div class="thinking-content" :class="{ 'tool-content': log.type === 'tool' }">
            {{ log.content }}
          </div>
          
          <!-- 工具调用详情 -->
          <div v-if="log.tool_name" class="tool-details">
            <div class="tool-row">
              <span class="tool-label">工具:</span>
              <span class="tool-value tool-name">{{ log.tool_name }}</span>
            </div>
            <div class="tool-row" v-if="log.args">
              <span class="tool-label">参数:</span>
              <code class="tool-value">{{ formatArgs(log.args) }}</code>
            </div>
            <div class="tool-row" v-if="log.result">
              <span class="tool-label">结果:</span>
              <span class="tool-value tool-result">{{ truncate(log.result, 200) }}</span>
            </div>
          </div>
        </div>
      </TransitionGroup>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'

const props = defineProps({
  title: {
    type: String,
    default: '思考过程',
  },
  logs: {
    type: Array,
    default: () => [],
  },
})

const contentRef = ref(null)

const formatTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return date.toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
}

const formatArgs = (args) => {
  if (!args) return ''
  if (typeof args === 'string') return args
  try {
    return JSON.stringify(args, null, 2)
  } catch {
    return String(args)
  }
}

const truncate = (text, length) => {
  if (!text) return ''
  const str = String(text)
  return str.length > length ? str.substring(0, length) + '...' : str
}

// 自动滚动到底部
watch(() => props.logs.length, () => {
  nextTick(() => {
    if (contentRef.value) {
      contentRef.value.scrollTop = contentRef.value.scrollHeight
    }
  })
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

.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.log-count {
  font-size: 11px;
  padding: 2px 8px;
  background: rgba(163, 113, 247, 0.2);
  color: var(--accent-purple);
  border-radius: 10px;
}

.panel-content {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
  font-size: 12px;
}

.empty-state {
  color: var(--text-muted);
  text-align: center;
  padding: 40px 20px;
}

.thinking-item {
  padding: 10px 12px;
  margin-bottom: 8px;
  background: var(--bg-tertiary);
  border-radius: var(--border-radius);
  border-left: 3px solid var(--accent-purple);
  
  &.is-tool {
    border-left-color: var(--accent-warning);
    background: rgba(210, 153, 34, 0.05);
  }
}

.thinking-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.thinking-agent {
  display: flex;
  align-items: center;
  gap: 8px;
}

.thinking-agent-name {
  color: var(--accent-purple);
  font-weight: 500;
}

.thinking-action {
  font-size: 10px;
  padding: 2px 8px;
  background: rgba(163, 113, 247, 0.2);
  color: var(--accent-purple);
  border-radius: 10px;

  &.tool-action {
    background: rgba(210, 153, 34, 0.2);
    color: var(--accent-warning);
  }
}

.thinking-time {
  color: var(--text-muted);
  font-family: var(--font-mono);
  font-size: 10px;
}

.thinking-content {
  font-size: 12px;
  color: var(--text-secondary);
  font-family: var(--font-mono);
  max-height: 100px;
  overflow-y: auto;
  white-space: pre-wrap;
  word-break: break-word;

  &.tool-content {
    color: var(--accent-warning);
  }
}

// 工具详情
.tool-details {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px dashed var(--border-color);
  font-size: 11px;
}

.tool-row {
  display: flex;
  gap: 8px;
  margin-bottom: 4px;
  align-items: flex-start;
}

.tool-label {
  color: var(--text-muted);
  flex-shrink: 0;
  min-width: 40px;
}

.tool-value {
  color: var(--text-primary);
  font-family: var(--font-mono);
  
  &.tool-name {
    color: var(--accent-warning);
    font-weight: 500;
  }
  
  &.tool-result {
    color: var(--accent-success);
  }
}

code.tool-value {
  font-size: 10px;
  background: var(--bg-hover);
  padding: 4px 8px;
  border-radius: var(--border-radius);
  max-height: 60px;
  overflow-y: auto;
  display: block;
  white-space: pre-wrap;
  word-break: break-all;
}

// Transition
.thinking-enter-active {
  transition: all 0.3s ease;
}

.thinking-enter-from {
  opacity: 0;
  transform: translateX(-10px);
}
</style>
