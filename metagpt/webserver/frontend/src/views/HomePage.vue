<template>
  <div class="home-page">
    <div class="welcome-content">
      <h1>🚀 欢迎使用 MetaGPT</h1>
      <p>AI驱动的多智能体协作平台</p>
      <p class="sub-text">选择一个项目或创建新项目开始</p>
      <button class="btn-primary large" @click="modalStore.showCreateProject()">
        创建第一个项目
      </button>
    </div>
  </div>
</template>

<script setup>
import { useModalStore } from '@/stores/modal'

const modalStore = useModalStore()
</script>

<style lang="scss" scoped>
.home-page {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: radial-gradient(ellipse at center, var(--bg-secondary) 0%, var(--bg-primary) 70%);
}

.welcome-content {
  text-align: center;
  animation: fadeIn 0.5s ease;

  h1 {
    font-size: 42px;
    margin-bottom: 12px;
    background: linear-gradient(135deg, var(--accent-primary), var(--accent-cyan));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  p {
    font-size: 18px;
    color: var(--text-secondary);
    margin-bottom: 8px;
  }

  .sub-text {
    font-size: 14px;
    color: var(--text-muted);
    margin-bottom: 32px;
  }
}

.btn-primary.large {
  padding: 14px 32px;
  font-size: 16px;
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-purple));
  color: white;
  border: none;
  border-radius: var(--border-radius);
  cursor: pointer;
  transition: var(--transition-normal);

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(88, 166, 255, 0.4);
  }
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>

