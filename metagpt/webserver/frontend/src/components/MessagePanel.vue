<template>
  <div class="panel messages-panel">
    <div class="panel-header">
      <h3>{{ title }}</h3>
      <button class="btn-icon" @click="$emit('clear')" title="清空">🗑</button>
    </div>
    <div class="panel-content" ref="contentRef">
      <div v-if="messages.length === 0" class="empty-state">
        等待项目开始...
      </div>
      <TransitionGroup name="message" v-else>
        <div
          v-for="(msg, index) in messages"
          :key="msg.id || index"
          class="message-item"
          :class="messageClass(msg)"
        >
          <div class="message-header">
            <span class="message-from">{{ msg.sent_from || 'System' }}</span>
            <span class="message-time">{{ formatTime(msg.timestamp) }}</span>
          </div>
          <div class="message-content">{{ msg.content || msg.message }}</div>
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
    default: '消息面板',
  },
  messages: {
    type: Array,
    default: () => [],
  },
})

defineEmits(['clear'])

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

const messageClass = (msg) => {
  if (msg.type === 'system' || msg.sent_from === 'System') {
    return 'system'
  }
  return ''
}

// 自动滚动到底部
watch(() => props.messages.length, () => {
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

.btn-icon {
  width: 32px;
  height: 32px;
  background: transparent;
  border: none;
  border-radius: var(--border-radius);
  cursor: pointer;
  font-size: 16px;
  transition: var(--transition-fast);

  &:hover {
    background: var(--bg-hover);
  }
}

.panel-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  font-size: 13px;
}

.empty-state {
  color: var(--text-muted);
  text-align: center;
  padding: 40px 20px;
}

.message-item {
  padding: 12px;
  margin-bottom: 8px;
  background: var(--bg-tertiary);
  border-radius: var(--border-radius);
  border-left: 3px solid var(--accent-primary);

  &.system {
    border-left-color: var(--accent-warning);
    background: rgba(210, 153, 34, 0.1);
  }
}

.message-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 12px;
}

.message-from {
  color: var(--accent-cyan);
  font-weight: 500;
}

.message-time {
  color: var(--text-muted);
  font-family: var(--font-mono);
  font-size: 11px;
}

.message-content {
  color: var(--text-primary);
  word-break: break-word;
  white-space: pre-wrap;
}

// Transition
.message-enter-active {
  transition: all 0.3s ease;
}

.message-enter-from {
  opacity: 0;
  transform: translateX(-10px);
}
</style>

