<template>
  <section class="summary-section">
    <div class="summary-card">
      <h3>📊 项目总结</h3>
      <div class="summary-content">
        <div class="summary-item">
          <span class="summary-label">状态</span>
          <span class="summary-value success">✅ 完成</span>
        </div>
        <div class="summary-item">
          <span class="summary-label">总花费</span>
          <span class="summary-value">${{ (project.total_cost || 0).toFixed(4) }}</span>
        </div>
        <div class="summary-item" v-if="project.output_path">
          <span class="summary-label">输出目录</span>
          <span class="summary-value path">{{ project.output_path }}</span>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
defineProps({
  project: {
    type: Object,
    required: true,
  },
})
</script>

<style lang="scss" scoped>
.summary-section {
  background: linear-gradient(135deg, rgba(63, 185, 80, 0.1), rgba(88, 166, 255, 0.1));
  border-radius: var(--border-radius-lg);
  padding: 24px;
  border: 1px solid var(--accent-success);
  animation: fadeIn 0.5s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.summary-card {
  h3 {
    margin-bottom: 16px;
    color: var(--accent-success);
    font-size: 16px;
  }
}

.summary-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid var(--border-color);

  &:last-child {
    border-bottom: none;
  }
}

.summary-label {
  color: var(--text-secondary);
  font-size: 14px;
}

.summary-value {
  font-weight: 500;
  font-family: var(--font-mono);
  font-size: 14px;

  &.success {
    color: var(--accent-success);
  }

  &.path {
    font-size: 12px;
    color: var(--text-primary);
    max-width: 60%;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
}
</style>

