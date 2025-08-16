<template>
  <div class="nav-desktop">
    <div class="nav-header">
      <h2>教务导航</h2>
    </div>
    
    <div class="nav-items">
      <div 
        v-for="item in navItems" 
        :key="item.id" 
        class="nav-item"
        @click="navigateTo(item.route)"
      >
        <img 
          :src="getIconUrl(item.icon)" 
          :alt="item.name" 
          class="nav-icon" 
        />
        <span class="nav-text">{{ item.name }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'; // 添加路由支持
const navItems = [
  { id: 'profile', name: '我的', icon: 'user', route: { name: 'profile' } },
  { id: 'schedule', name: '课程表', icon: 'calendar', route: { name: 'schedule' } },
  { id: 'exams', name: '考试安排', icon: 'exam', route: { name: 'exams' } },
  { id: 'scores', name: '考试成绩', icon: 'score', route: { name: 'scores' } },
  { id: 'second-class', name: '第二课堂', icon: 'activity', route: { name: 'second-class' } },
  { id: 'campus-query', name: '校园查询', icon: 'search', route: { name: 'campus-query' } },
  { id: 'bonus', name: '我要加分', icon: 'plus', route: { name: 'bonus' } }
];
const router = useRouter(); // 获取路由实例

const getIconUrl = (iconName) => {
  return new URL(`../assets/icons/${iconName}.svg`, import.meta.url).href;
};

const navigateTo = (route) => {
  router.push(route);
};
</script>

<style scoped>
.nav-desktop {
  position: fixed;
  left: 0;
  top: 0;
  width: 200px;
  height: 100vh;
  background: #2c3e50;
  color: white;
  padding: 20px 0;
  box-shadow: 2px 0 5px rgba(0, 0, 0, 0.1);
  z-index: 100;
}

.nav-header {
  padding: 0 20px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.nav-header h2 {
  margin: 0;
  font-size: 1.2rem;
  font-weight: 500;
}

.nav-items {
  padding: 20px 0;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  cursor: pointer;
  transition: background 0.2s;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.1);
}

.nav-icon {
  width: 20px;
  height: 20px;
  margin-right: 15px;
  filter: invert(100%) sepia(0%) saturate(0%) hue-rotate(93deg) brightness(103%) contrast(103%);
}

.nav-text {
  font-size: 14px;
}
</style>