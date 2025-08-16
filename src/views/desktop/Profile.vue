<template>
  <div class="profile-view">
    <h1>我的信息</h1>
    <div class="user-card">
      <img v-if="userProfile && userProfile.icon" 
          :src="userProfile.icon" 
          class="avatar" 
          :class="{ 'rotate': isRotating }"
          @click="avatarClick"
          @mouseover="isHovering = true"
          @mouseleave="isHovering = false" />
      <div v-else class="avatar-placeholder"></div>
      <div class="user-info">
        <!-- <p>姓名：{{ isLoggedIn ? userProfile.学生姓名 : '请登录' }}</p> -->
        <p v-if="isLoggedIn">姓名：{{ userProfile.学生姓名 }}</p>
        <p v-else>请登录</p>
        <template v-if="isLoggedIn">
          <p>学号：{{ userProfile.学生编号 }}</p>
          <p>学院：{{ userProfile.所属院系 }}</p>
          <p>专业：{{ userProfile.专业名称 }}</p>
          <p>班级：{{ userProfile.班级名称 }}</p>
        </template>
      </div>
    </div>
    
    <div class="actions">
      <button @click="logout">退出登录</button>
      <button @click="clearData">清除本地数据</button>
    </div>
  </div>
</template>

<script setup>
import DataModel from '@/models/DataModel';
import { computed, ref  } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const userProfile = computed(() => DataModel.user?.profile || {});
const isLoggedIn = computed(() => !!DataModel.currentLoginUser);

const logout = () => {
  DataModel.setCurrentLoginUser(null);
  router.push('/login');
};

const clearData = () => {
  localStorage.removeItem('rawdata');
  location.reload();
};

const isHovering = ref(false);
const isRotating = ref(false);

const avatarClick = () => {
  if (!isRotating.value) {
    rotateAvatar();
  }
};

const rotateAvatar = () => {
  isRotating.value = true;
  setTimeout(() => {
    isRotating.value = false;
  }, 1000);
};

</script>

<style scoped>
/* #region 头像整点小活 */
.avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  margin-right: 20px;
  object-fit: cover;
  transition: all 0.3s ease, transform 1s ease;
  cursor: pointer;
}

.avatar:hover {
  transform: scale(1.1);
  transition: transform 0.3s ease;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
}

.avatar.rotate {
  scale: 1.1;
  animation: rotate 1s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
/* #endregion */

.profile-view {
  padding: 20px;
  max-width: 600px;
  margin: 0 auto;
}

.user-card {
  display: flex;
  align-items: center;
  background: #f5f5f5;
  border-radius: 10px;
  padding: 20px;
  margin-bottom: 20px;
}

.avatar-placeholder {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: #3498db;
  margin-right: 20px;
}

.user-info p {
  margin: 6px 0;
  font-size: 15px;
}

.actions {
  display: flex;
  gap: 10px;
}

.actions button {
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  background: #3498db;
  color: white;
}

.actions button:last-child {
  background: #e74c3c;
}
</style>