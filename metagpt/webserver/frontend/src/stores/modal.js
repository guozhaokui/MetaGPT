import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useModalStore = defineStore('modal', () => {
  const createProjectVisible = ref(false)

  function showCreateProject() {
    createProjectVisible.value = true
  }

  function hideCreateProject() {
    createProjectVisible.value = false
  }

  return {
    createProjectVisible,
    showCreateProject,
    hideCreateProject,
  }
})

