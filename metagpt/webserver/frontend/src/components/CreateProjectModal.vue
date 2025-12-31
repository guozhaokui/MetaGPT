<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="modalStore.createProjectVisible" class="modal">
        <div class="modal-overlay" @click="modalStore.hideCreateProject()"></div>
        <div class="modal-content">
          <div class="modal-header">
            <h3>🆕 创建新项目</h3>
            <button class="btn-close" @click="modalStore.hideCreateProject()">×</button>
          </div>
          
          <form @submit.prevent="handleSubmit" class="modal-form">
            <div class="form-group">
              <label for="projectName">项目名称</label>
              <input
                id="projectName"
                v-model="form.name"
                type="text"
                required
                placeholder="例如：2048游戏"
                ref="nameInput"
              />
            </div>

            <div class="form-group">
              <label for="projectIdea">项目需求</label>
              <textarea
                id="projectIdea"
                v-model="form.idea"
                required
                rows="4"
                placeholder="详细描述你想要开发的项目..."
              ></textarea>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label for="projectBudget">预算 (USD)</label>
                <input
                  id="projectBudget"
                  v-model.number="form.investment"
                  type="number"
                  min="0.1"
                  step="0.1"
                />
              </div>
              <div class="form-group">
                <label for="projectRounds">运行轮次</label>
                <input
                  id="projectRounds"
                  v-model.number="form.n_round"
                  type="number"
                  min="1"
                  max="20"
                />
              </div>
            </div>

            <div class="modal-actions">
              <button type="button" class="btn-secondary" @click="modalStore.hideCreateProject()">
                取消
              </button>
              <button type="submit" class="btn-primary" :disabled="loading">
                {{ loading ? '创建中...' : '创建项目' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { reactive, ref, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useProjectStore } from '@/stores/projects'
import { useModalStore } from '@/stores/modal'

const router = useRouter()
const projectStore = useProjectStore()
const modalStore = useModalStore()

const nameInput = ref(null)
const loading = ref(false)

const form = reactive({
  name: '',
  idea: '创建一个基于web的俄罗斯方块游戏。要求实现全部流程，形成项目。不要用搜索功能。',
  investment: 5.0,
  n_round: 20,
})

const resetForm = () => {
  form.name = ''
  form.idea = '创建一个基于web的俄罗斯方块游戏。要求实现全部流程，形成项目。不要用搜索功能。'
  form.investment = 5.0
  form.n_round = 20
}

const handleSubmit = async () => {
  loading.value = true
  try {
    const project = await projectStore.createProject({ ...form })
    modalStore.hideCreateProject()
    resetForm()
    router.push(`/project/${project.id}`)
  } catch (error) {
    // Error handled in store
  } finally {
    loading.value = false
  }
}

// 打开模态框时聚焦输入框
watch(() => modalStore.createProjectVisible, (visible) => {
  if (visible) {
    nextTick(() => {
      nameInput.value?.focus()
    })
  }
})
</script>

<style lang="scss" scoped>
.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
}

.modal-content {
  position: relative;
  width: 100%;
  max-width: 500px;
  background: var(--bg-card);
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--border-color);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-color);

  h3 {
    font-size: 18px;
    font-weight: 600;
  }
}

.btn-close {
  width: 32px;
  height: 32px;
  background: transparent;
  border: none;
  font-size: 24px;
  color: var(--text-muted);
  cursor: pointer;
  transition: var(--transition-fast);

  &:hover {
    color: var(--text-primary);
  }
}

.modal-form {
  padding: 24px;
}

.form-group {
  margin-bottom: 20px;

  label {
    display: block;
    margin-bottom: 8px;
    font-size: 13px;
    color: var(--text-secondary);
  }

  input, textarea {
    width: 100%;
    padding: 12px;
    background: var(--bg-tertiary);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius);
    color: var(--text-primary);
    font-family: var(--font-sans);
    font-size: 14px;

    &:focus {
      outline: none;
      border-color: var(--accent-primary);
    }
  }
}

.form-row {
  display: flex;
  gap: 16px;

  .form-group {
    flex: 1;
  }
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
}

.btn-primary, .btn-secondary {
  padding: 10px 20px;
  border-radius: var(--border-radius);
  font-size: 14px;
  cursor: pointer;
  transition: var(--transition-fast);
}

.btn-primary {
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-purple));
  color: white;
  border: none;

  &:hover:not(:disabled) {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(88, 166, 255, 0.3);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

.btn-secondary {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);

  &:hover {
    background: var(--bg-hover);
  }
}

// Transition
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.25s ease;

  .modal-content {
    transition: transform 0.25s ease;
  }
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;

  .modal-content {
    transform: scale(0.95) translateY(-20px);
  }
}
</style>

