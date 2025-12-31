<template>
  <div class="employees-grid">
    <div
      v-for="employee in employees"
      :key="employee.name"
      class="employee-card"
      :class="{ working: !employee.is_idle }"
    >
      <div class="employee-avatar">{{ avatarIcon(employee.profile) }}</div>
      <div class="employee-name">{{ employee.name }}</div>
      <div class="employee-role">{{ employee.profile }}</div>
      <span class="employee-status" :class="employee.is_idle ? 'idle' : 'working'">
        {{ employee.is_idle ? '空闲' : (employee.current_action || '工作中') }}
      </span>
    </div>
  </div>
</template>

<script setup>
defineProps({
  employees: {
    type: Array,
    default: () => [],
  },
})

const avatarIcon = (profile) => {
  const icons = {
    TeamLeader: '👨‍💼',
    ProductManager: '📋',
    Architect: '🏗️',
    Engineer: '💻',
    Engineer2: '💻',
    DataAnalyst: '📊',
    QaEngineer: '🔍',
    ProjectManager: '📅',
  }
  return icons[profile] || '🤖'
}
</script>

<style lang="scss" scoped>
.employees-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 12px;
}

.employee-card {
  background: var(--bg-tertiary);
  border-radius: var(--border-radius);
  padding: 16px;
  border: 1px solid var(--border-color);
  transition: var(--transition-fast);

  &:hover {
    border-color: var(--accent-primary);
  }

  &.working {
    border-color: var(--accent-primary);
    box-shadow: 0 0 12px rgba(88, 166, 255, 0.2);
  }
}

.employee-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  margin-bottom: 12px;
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-purple));
}

.employee-name {
  font-weight: 600;
  margin-bottom: 4px;
}

.employee-role {
  font-size: 12px;
  color: var(--accent-cyan);
  margin-bottom: 8px;
}

.employee-status {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 10px;
  display: inline-block;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;

  &.idle {
    background: var(--bg-hover);
    color: var(--text-muted);
  }

  &.working {
    background: rgba(88, 166, 255, 0.2);
    color: var(--accent-primary);
  }
}
</style>

