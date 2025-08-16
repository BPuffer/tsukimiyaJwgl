<template>
  <div class="mobile-bottom-nav">
    <div class="nav-items">
      <div 
        v-for="item in navItemsMobile" 
        :key="item.id" 
        class="nav-item"
        :class="{ 'active': currentRoute === item.route.name }"
        @click="navigateTo(item.route)"
      >
        <img 
          :src="getIconUrl(item)" 
          :alt="item.name" 
          class="nav-icon"
        />
        <span class="nav-label">{{ item.name }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';

const navItemsMobile = [
  { id: 'm', name: '主页', icon: 'm-home', route: { name: 'm' } },
  { id: 'm-schedule', name: '课程', icon: 'calendar', route: { name: 'mschedule' } },
  { id: 'm-exams', name: '考试', icon: 'exam', route: { name: 'mexams' } },
  { id: 'm-bonus', name: '加分', icon: 'plus', route: { name: 'mbonus' } },
  { id: 'm-profile', name: '我的', icon: 'user', route: { name: 'mprofile' } }
];

// 所有图标
import mHomeActive from '@/assets/icons/iconmonstr-home-1.svg';
import mHomeInactive from '@/assets/icons/iconmonstr-home-2.svg';
import calendarActive from '@/assets/icons/iconmonstr-calendar-4.svg';
import calendarInactive from '@/assets/icons/iconmonstr-calendar-4.svg';
import examActive from '@/assets/icons/iconmonstr-school-21.svg';
import examInactive from '@/assets/icons/iconmonstr-school-22.svg';
import bonusActive from '@/assets/icons/iconmonstr-star-filled.svg';
import bonusInactive from '@/assets/icons/iconmonstr-star-lined.svg';
import profileActive from '@/assets/icons/iconmonstr-id-card-23.svg';
import profileInactive from '@/assets/icons/iconmonstr-id-card-8.svg';

const iconMap = {
  'm.Active': mHomeActive,
  'm.Inactive': mHomeInactive,
  'm-schedule.Active': calendarActive,
  'm-schedule.Inactive': calendarInactive,
  'm-exams.Active': examActive,
  'm-exams.Inactive': examInactive,
  'm-bonus.Active': bonusActive,
  'm-bonus.Inactive': bonusInactive,
  'm-profile.Active': profileActive,
  'm-profile.Inactive': profileInactive
};


const router = useRouter();
const route = useRoute();
const currentRoute = computed(() => route.name);

const getIconUrl = (item) => {
  const isActive = currentRoute.value === item.route.name;
  return iconMap[`${item.id}.${isActive ? 'Active' : 'Inactive'}`];
};


const navigateTo = (route) => {
  if (route !== currentRoute.value) {
    router.push(route);
  }
};
</script>

<style scoped>
/* 底部导航栏容器 */
.mobile-bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background-color: #fff7f7c0;
  box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.05);
  height: 64px;
  z-index: 50;
  backdrop-filter: blur(6px);
}

/* 导航项容器 */
.nav-items {
  display: flex;
  height: 100%;
}

/* 单个导航项 */
.nav-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  color: #6B7280;
}

/* 激活状态的导航项 */
.nav-item.active {
  color: #3B82F6;
}

.nav-item.active .nav-icon {
  color: #f00
}

/* 导航图标 */
.nav-icon {
  width: 24px;
  height: 24px;
  margin-bottom: 4px;
  transition: filter 0.3s ease;
}

/* 非激活状态的图标颜色处理 */
.nav-item:not(.active) .nav-icon {
  filter: invert(43%) sepia(11%) saturate(276%) hue-rotate(192deg) brightness(93%) contrast(87%);
}

/* 导航标签 */
.nav-label {
  font-size: 10px;
  font-weight: 500;
  transition: color 0.3s ease;
}
</style>
    