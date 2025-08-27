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
        <MAnnouncement v-for="(announcement, index) in announcements" :key="index" :announcement="announcement"
          :is-in-fade-in="announcementsFadeIns[index]" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, reactive } from 'vue';
import DataModel from '@/models/DataModel';
import { useRouter } from 'vue-router';
import MAnnouncement from '@/components/MAnnouncement.vue';

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
const announcementsLength = computed(() => announcements.value.length);
const announcementLoading = ref(false);
const announcementsFadeIns = ref(new Array(announcementsLength.value).fill(false))
const startFadeInAnnouncements = () => {
  Array.from({ length: announcementsLength.value }, (_, i) => {
    setTimeout(() => { announcementsFadeIns.value[i] = true }, 150 * i);
  })
}

onMounted(() => {
  nextTick(() => {
    if (!DataModel.serverUpdating) startFadeInAnnouncements();
    if (DataModel.serverUpdating) {
      announcementLoading.value = true;
      console.log('等待服务器数据更新');
      (async () => {
        await DataModel.serverUpdatePromise;
        announcements.value = DataModel.server?.announcements?.normal || [];
        console.log('服务器数据更新完成', announcements);
        announcementLoading.value = false;
        nextTick(startFadeInAnnouncements);
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
}

@keyframes logoFloat {

  0%,
  100% {
    transform: translateY(5px);
  }

  50% {
    transform: translateY(-5px);
  }
}

.logo-swap {
  animation: logoSwap 3s ease-in-out infinite;
}

@keyframes logoSwap {

  0%,
  100% {
    transform: rotate(5deg);
  }

  50% {
    transform: rotate(-5deg);
  }
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
</style>