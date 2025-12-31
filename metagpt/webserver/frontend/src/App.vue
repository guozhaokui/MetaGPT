<template>
  <div class="app-container">
    <!-- 侧边栏 -->
    <Sidebar />
    
    <!-- 主内容区 -->
    <main class="main-content">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>

    <!-- 创建项目模态框 -->
    <CreateProjectModal />
    
    <!-- 通知组件 -->
    <Notifications />
  </div>
</template>

<script setup>
import Sidebar from '@/components/Sidebar.vue'
import CreateProjectModal from '@/components/CreateProjectModal.vue'
import Notifications from '@/components/Notifications.vue'
</script>

<style lang="scss">
.app-container {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

.main-content {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>

