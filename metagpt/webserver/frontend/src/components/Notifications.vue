<template>
  <Teleport to="body">
    <div class="notifications-container">
      <TransitionGroup name="notification">
        <div
          v-for="notification in notificationStore.notifications"
          :key="notification.id"
          class="notification"
          :class="notification.type"
        >
          <span class="notification-icon">{{ icons[notification.type] }}</span>
          <span class="notification-message">{{ notification.message }}</span>
          <button class="notification-close" @click="notificationStore.remove(notification.id)">
            ×
          </button>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<script setup>
import { useNotification } from '@/stores/notification'

const notificationStore = useNotification()

const icons = {
  success: '✓',
  error: '✕',
  warning: '⚠',
  info: 'ℹ',
}
</script>

<style lang="scss" scoped>
.notifications-container {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 2000;
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-width: 400px;
}

.notification {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  background: var(--bg-card);
  border-radius: var(--border-radius);
  border: 1px solid var(--border-color);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);

  &.success {
    border-left: 3px solid var(--accent-success);
    .notification-icon { color: var(--accent-success); }
  }

  &.error {
    border-left: 3px solid var(--accent-danger);
    .notification-icon { color: var(--accent-danger); }
  }

  &.warning {
    border-left: 3px solid var(--accent-warning);
    .notification-icon { color: var(--accent-warning); }
  }

  &.info {
    border-left: 3px solid var(--accent-primary);
    .notification-icon { color: var(--accent-primary); }
  }
}

.notification-icon {
  font-size: 16px;
  font-weight: bold;
}

.notification-message {
  flex: 1;
  font-size: 14px;
  color: var(--text-primary);
}

.notification-close {
  width: 24px;
  height: 24px;
  background: transparent;
  border: none;
  font-size: 18px;
  color: var(--text-muted);
  cursor: pointer;
  transition: var(--transition-fast);

  &:hover {
    color: var(--text-primary);
  }
}

// Transition
.notification-enter-active,
.notification-leave-active {
  transition: all 0.3s ease;
}

.notification-enter-from {
  opacity: 0;
  transform: translateX(100px);
}

.notification-leave-to {
  opacity: 0;
  transform: translateX(100px);
}

.notification-move {
  transition: transform 0.3s ease;
}
</style>

