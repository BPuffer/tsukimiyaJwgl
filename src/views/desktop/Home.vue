<template>
  <div class="home-container">
    <!-- 学生信息卡片 -->
    <div class="student-card">
      <h2>学生信息</h2>
      <div class="info-item">
        <span class="label">姓名：</span>
        <span class="value">{{ studentInfo.name }}</span>
      </div>
      <div class="info-item">
        <span class="label">学号：</span>
        <span class="value">{{ studentInfo.id }}</span>
      </div>
      <div class="info-item">
        <span class="label">院系：</span>
        <span class="value">{{ studentInfo.department }}</span>
      </div>
      <div class="info-item">
        <span class="label">专业：</span>
        <span class="value">{{ studentInfo.major }}</span>
      </div>
      <div class="info-item">
        <span class="label">班级：</span>
        <span class="value">{{ studentInfo.class }}</span>
      </div>
    </div>

    <!-- 快捷按钮区域 -->
    <div class="quick-actions">
      <h2>快捷操作</h2>
      <div class="buttons">
        <button 
          v-for="button in quickButtons" 
          :key="button.id"
          @click="navigateTo(button.endpoint)"
          class="action-button"
        >
          {{ button.label }}
        </button>
      </div>
    </div>

    <!-- 脚 -->
    <!-- <Footer></Footer> -->
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import Footer from '@/components/Footer.vue';

const router = useRouter();

const studentInfo = ref({
  name: '张三',
  id: '2304040117',
  department: '计算机学院',
  major: '软件工程',
  class: '软件2304班'
});

const quickButtons = ref([
  { id: 1, label: '课程表', endpoint: '/schedule' },
  { id: 2, label: '成绩查询', endpoint: '/grades' },
  { id: 3, label: '考试安排', endpoint: '/exams' },
  { id: 4, label: '选课系统', endpoint: '/course-selection' },
  { id: 5, label: '个人信息', endpoint: '/profile' },
  { id: 6, label: '校园通知', endpoint: '/notices' }
]);

const navigateTo = (endpoint) => {
  router.push(endpoint);
};
</script>

<style scoped>
.home-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.student-card {
  background: #f5f5f5;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 30px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.student-card h2 {
  margin-top: 0;
  color: #333;
  border-bottom: 1px solid #ddd;
  padding-bottom: 10px;
}

.info-item {
  margin: 15px 0;
  display: flex;
}

.label {
  font-weight: bold;
  width: 80px;
}

.value {
  flex: 1;
}

.quick-actions h2 {
  color: #333;
  margin-bottom: 20px;
}

.buttons {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
}

.action-button {
  background: #4a89dc;
  color: white;
  border: none;
  padding: 12px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 16px;
  transition: background 0.3s;
}

.action-button:hover {
  background: #3b7dd8;
}
</style>
