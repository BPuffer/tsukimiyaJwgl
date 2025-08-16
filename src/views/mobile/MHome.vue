<template>
  <div class="home-container">
    <!-- 顶部欢迎区域 -->
    <div class="header">
      <div class="welcome-bubble">
        <div class="welcome-text">{{ welcomeTip }}</div>
      </div>
      <div class="logo-container">
        <div class="logo-swap">
          <div class="logo-float">
            <img src="@/assets/img/logo.png" alt="月宫の小站" class="logo">
          </div>
        </div>
      </div>
    </div>

    <!-- 公告区域 -->
    <div class="announcements-section">
      <div class="section-header">
        <i class="fa-solid fa-bullhorn"></i>
        <h2>最新公告</h2>
      </div>
      <div v-if="announcementLoading" class="announcement-loading">
        <div class="loading-spinner"></div>
        <div class="loading-text">如果你看到这条消息超过5秒说明服务器可能又挂了...</div>
      </div>
      <div class="announcements-container">
        <div 
          v-for="(announcement, index) in announcements" 
          :key="index"
          class="announcement-card"
          :style="{ '--hue': announcement.hue }"
        >
          <div class="announcement-header">
            <div class="announcement-title">{{ announcement.title }}</div>
            <div class="announcement-date">{{ announcement.date }}</div>
          </div>
          <div class="announcement-content">{{ announcement.content }}</div>
          <div class="announcement-footer">
            <div class="announcement-tag">{{ announcement.tag }}</div>
          </div>
        </div>
      </div>
    </div>
    <!-- <Footer></Footer> -->
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, reactive } from 'vue';
import DataModel from '@/models/DataModel';
import Footer from '@/components/Footer.vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const userProfile = computed(() => DataModel.user?.profile || {});
const welcomeTip = computed(() => {
  if (userProfile.value.学生姓名) {
    const hour = (new Date()).getHours();
    const prefixGreet = (
      hour <= 1 ? "晚上好，" :
      hour <= 4 ? "怎么还不睡？" :
      hour <= 10 ? "早上好，" :
      hour <= 14 ? "中午好，" : "晚上好，"
    );
    return `${prefixGreet}${userProfile.value.学生姓名}！`;
  } else {
    return '请先登录！';  
  }
})
const announcements = ref(DataModel.server?.announcements?.normal || []);
const announcementLoading = ref(false);


onMounted(() => {
  nextTick(() => {
    if (!DataModel.serverUpdating) {
      const elements = document.querySelectorAll('.student-card, .announcement-card');
      elements.forEach((el, index) => {
        setTimeout(() => {
          el.style.opacity = '1';
          el.style.transform = 'translateY(0)';
        }, 150 * index);
      });
    }
    if (DataModel.serverUpdating) {
      announcementLoading.value = true;
      console.log('服务器数据正在更新');
      (async () => {
        await DataModel.serverUpdatePromise;
        announcements.value = DataModel.server?.announcements?.normal || [];
        console.log('服务器数据更新完成', announcements);
        announcementLoading.value = false;
        nextTick(() => {
          const elements = document.querySelectorAll('.student-card, .announcement-card');
          elements.forEach((el, index) => {
            setTimeout(() => {
              el.style.opacity = '1';
              el.style.transform = 'translateY(0)';
            }, 150 * index);
          });
        });
      })()
    }
  });
});
</script>

<style scoped>
/* 基础样式 */
.home-container {
  position: relative;
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  overflow: hidden;
  min-height: 100vh;
}

/* 头部区域 */
.header {
  position: relative;
  z-index: 2;
  margin-top: 20px;
  margin-bottom: 30px;
}

.logo-container {
  display: flex;
  justify-content: center;
  position: fixed;
  right: 10%;
  top: 5%;
  height: 5%;
  object-fit: contain;
}

.logo {
  height: 5vh;
}


.logo-float {
  animation: logoFloat 5s ease-in-out infinite;
}@keyframes logoFloat {
  0%, 100% { transform: translateY(5px); }
  50% { transform: translateY(-5px); }
}

.logo-swap {
  animation: logoSwap 3s ease-in-out infinite;
}@keyframes logoSwap {
  0%, 100% { transform: rotate(5deg); }
  50% { transform: rotate(-5deg); }
}

.welcome-bubble {
  background: rgba(255, 255, 255, 0.75);
  border-radius: 25px;
  padding: 5px 20px 10px;
  position: relative;
  border: 3px solid #ffb8e4;
}

.welcome-text {
  font-size: 1.6em;
  font-weight: bold;
  color: #ff6b9d;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
}

/* 公告区域 */
.announcements-section {
  position: relative;
  z-index: 2;
  margin-top: 20px;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 20px;
  color: #ff6b9d;
}

.section-header h2 {
  font-size: 24px;
  text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.1);
  margin: 0;
}

.section-icon {
  width: 40px;
  height: 40px;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
}

.announcements-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.announcement-card {
  background: rgba(255, 255, 255, 0.75);
  border-radius: 20px;
  padding: 20px;
  border: 3px solid hsl(var(--hue), 100%, 80%);
  position: relative;
  overflow: hidden;
  transform: translateY(20px);
  opacity: 0;
  transition: all 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.announcement-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
}

.announcement-title {
  font-size: 18px;
  font-weight: bold;
  color: #5a67d8;
  flex: 1;
  padding-right: 10px;
}

.announcement-date {
  font-size: 14px;
  color: #ff7eb8;
  white-space: nowrap;
}

.announcement-content {
  color: #4a5568;
  line-height: 1.6;
  margin-bottom: 15px;
  font-size: 16px;
  white-space: pre-line;
}

.announcement-footer {
  display: flex;
  justify-content: flex-end;
}

.announcement-tag {
  background: hsl(var(--hue), 100%, 90%);
  color: hsl(var(--hue), 60%, 40%);
  padding: 5px 15px;
  border-radius: 15px;
  font-size: 14px;
  font-weight: bold;
}
</style>