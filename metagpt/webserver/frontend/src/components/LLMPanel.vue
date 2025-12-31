<template>
  <div class="panel llm-panel">
    <div class="panel-header">
      <h3>{{ title }}</h3>
      <span class="call-count" v-if="calls.length">{{ calls.length }} 次调用</span>
    </div>
    <div class="panel-content" ref="contentRef">
      <div v-if="calls.length === 0" class="empty-state">
        等待LLM调用...
      </div>
      <TransitionGroup name="llm" v-else>
        <div
          v-for="call in calls"
          :key="call.id"
          class="llm-item"
          :class="{ expanded: expandedId === call.id }"
          @click="toggleExpand(call.id)"
        >
          <div class="llm-header">
            <div class="llm-info">
              <span class="llm-agent">{{ call.agent_name }}</span>
              <span class="llm-model" v-if="call.model">{{ call.model }}</span>
              <span class="llm-cost" v-if="call.cost">${{ call.cost.toFixed(4) }}</span>
            </div>
            <span class="llm-time">{{ formatTime(call.timestamp) }}</span>
          </div>
          
          <div class="llm-preview" v-if="expandedId !== call.id">
            <div class="preview-label">请求:</div>
            <div class="preview-text">{{ truncate(call.prompt, 100) }}</div>
          </div>

          <Transition name="expand">
            <div v-if="expandedId === call.id" class="llm-detail">
              <div class="detail-section">
                <div class="detail-label">📤 请求 (Prompt)</div>
                <pre class="detail-content prompt">{{ call.prompt }}</pre>
              </div>
              <div class="detail-section">
                <div class="detail-label">📥 响应 (Response)</div>
                <pre class="detail-content response">{{ call.response }}</pre>
              </div>
              <div class="detail-meta" v-if="call.tokens">
                <span>Tokens: {{ call.tokens.prompt }} → {{ call.tokens.completion }}</span>
              </div>
            </div>
          </Transition>
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
    default: 'LLM 调用',
  },
  calls: {
    type: Array,
    default: () => [],
  },
})

const contentRef = ref(null)
const expandedId = ref(null)

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
  return text.length > length ? text.substring(0, length) + '...' : text
}

const toggleExpand = (id) => {
  expandedId.value = expandedId.value === id ? null : id
}

// 自动滚动到底部
watch(() => props.calls.length, () => {
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

.call-count {
  font-size: 11px;
  padding: 2px 8px;
  background: rgba(88, 166, 255, 0.2);
  color: var(--accent-primary);
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

.llm-item {
  padding: 10px 12px;
  margin-bottom: 8px;
  background: var(--bg-tertiary);
  border-radius: var(--border-radius);
  border-left: 3px solid var(--accent-cyan);
  cursor: pointer;
  transition: var(--transition-fast);

  &:hover {
    border-left-color: var(--accent-primary);
  }

  &.expanded {
    border-left-color: var(--accent-primary);
    background: rgba(88, 166, 255, 0.05);
  }
}

.llm-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
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

.llm-preview {
  display: flex;
  gap: 8px;
  font-size: 11px;
}

.preview-label {
  color: var(--text-muted);
  flex-shrink: 0;
}

.preview-text {
  color: var(--text-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.llm-detail {
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid var(--border-color);
}

.detail-section {
  margin-bottom: 10px;
}

.detail-label {
  font-size: 11px;
  color: var(--text-muted);
  margin-bottom: 6px;
  font-weight: 500;
}

.detail-content {
  font-family: var(--font-mono);
  font-size: 11px;
  padding: 10px;
  border-radius: var(--border-radius);
  max-height: 150px;
  overflow-y: auto;
  white-space: pre-wrap;
  word-break: break-word;
  margin: 0;

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
}

// Transitions
.llm-enter-active {
  transition: all 0.3s ease;
}

.llm-enter-from {
  opacity: 0;
  transform: translateY(-10px);
}

.expand-enter-active, .expand-leave-active {
  transition: all 0.2s ease;
}

.expand-enter-from, .expand-leave-to {
  opacity: 0;
  max-height: 0;
}
</style>

