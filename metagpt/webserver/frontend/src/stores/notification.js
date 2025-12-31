import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useNotification = defineStore('notification', () => {
  const notifications = ref([])
  let idCounter = 0

  function add(message, type = 'info', duration = 4000) {
    const id = ++idCounter
    notifications.value.push({
      id,
      message,
      type,
      timestamp: Date.now(),
    })

    if (duration > 0) {
      setTimeout(() => {
        remove(id)
      }, duration)
    }

    return id
  }

  function remove(id) {
    const index = notifications.value.findIndex(n => n.id === id)
    if (index > -1) {
      notifications.value.splice(index, 1)
    }
  }

  function success(message, duration) {
    return add(message, 'success', duration)
  }

  function error(message, duration = 6000) {
    return add(message, 'error', duration)
  }

  function warning(message, duration) {
    return add(message, 'warning', duration)
  }

  function info(message, duration) {
    return add(message, 'info', duration)
  }

  return {
    notifications,
    add,
    remove,
    success,
    error,
    warning,
    info,
  }
})

