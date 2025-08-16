<template>
  <div class="view-container">
    <div class="exam-list">
      <div 
        v-for="(exam, index) in exams" 
        :key="index" 
        class="exam-card"
        :class="getExamStatusClass(exam)"
        @click="toggleDetails(index, $event)"
      >
        <div class="card-main">
          <div class="exam-header">
            <h3>{{ exam.课程名称 }}</h3>
            <span class="exam-credit">{{ exam.学分 }}学分</span>
          </div>
          
          <div class="exam-time">
            <div class="time-label">考试时间:</div>
            <div class="time-value">{{ exam.考试安排?.考试时间 || '未安排' }}</div>
          </div>
          
          <div class="exam-location">
            <div class="location-label">考场:</div>
            <div class="location-value">{{ exam.考试安排?.考场 || '未安排' }}</div>
          </div>
          
          <div class="countdown" v-if="getExamStatus(exam) === 'pending'">
            <div class="countdown-label">剩余时间:</div>
            <div class="countdown-value">{{ getCountdownText(exam) }}</div>
          </div>
          
          <div class="exam-status" v-else>
            <div class="status-label">状态:</div>
            <div class="status-value">{{ getExamStatusText(exam) }}</div>
          </div>
        </div>
        
        <div class="card-details" :class="{ 'expanded': expandedIndex === index }">
          <div class="detail-row">
            <span class="detail-label">授课教师:</span>
            <span>{{ exam.考试安排?.授课教师 || '—' }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">考核方式:</span>
            <span>{{ exam.考核方式 || '—' }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">课程性质:</span>
            <span>{{ exam.课程性质 || '—' }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>


<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue';
import { useRoute } from 'vue-router';
import DataModel from '@/models/DataModel';

const route = useRoute();
const exams = ref(DataModel.user?.exam?.subjects || []);
const expandedIndex = ref(null);
const timer = ref(null);

// 切换详情显示
let closeCooldown = false;
const toggleDetails = (index, event) => {
  event.stopPropagation(); // 关键：阻止事件冒泡
  expandedIndex.value = expandedIndex.value === index ? null : index;
};

const closeDetails = () => {
  expandedIndex.value = null;
};

// 获取考试状态
const getExamStatus = (exam) => {
  if (!exam.考试安排?.考试时间) return 'unknown';
  
  const [startStr, endStr] = exam.考试安排.考试时间.split(' - ');
  const startTime = new Date(startStr);
  const endTime = new Date(endStr);
  const now = new Date();
  
  if (now < startTime) return 'pending';
  if (now >= startTime && now <= endTime) return 'ongoing';
  return 'completed';
};

// 获取倒计时文本
const getCountdownText = (exam) => {
  if (!exam.考试安排?.考试时间) return '未安排';
  
  const [startStr] = exam.考试安排.考试时间.split(' - ');
  const startTime = new Date(startStr);
  const now = new Date();
  const diff = startTime - now;
  
  if (diff <= 0) return '已开始';
  
  const days = Math.floor(diff / (1000 * 60 * 60 * 24));
  if (days > 0) return `${days}天`;
  
  const hours = Math.floor(diff / (1000 * 60 * 60));
  if (hours > 0) return `${hours}小时`;
  
  const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
  const seconds = Math.floor((diff % (1000 * 60)) / 1000);
  return `${minutes}分${seconds}秒`;
};

// 获取考试状态文本
const getExamStatusText = (exam) => {
  const status = getExamStatus(exam);
  return {
    pending: '即将开始',
    ongoing: '考试中',
    completed: '已完成',
    unknown: '未安排'
  }[status];
};

// 获取考试状态类
const getExamStatusClass = (exam) => {
  const status = getExamStatus(exam);
  return `status-${status}`;
};

// 定时更新倒计时
const startTimer = () => {
  timer.value = setInterval(() => {
    exams.value = [...exams.value];
  }, 1000);
};

onMounted(() => {
  startTimer();
  window.addEventListener('click', closeDetails);
});
onBeforeUnmount(() => clearInterval(timer.value));
</script>

<style scoped>
/* #region 基础容器样式 */
.view-container {
  max-width: 1200px;
  margin: 0 auto;
  background: white;
  border-radius: 16px;
  overflow: hidden;
}
/* #endregion */

/* #region 考试卡片列表 */
.exam-list {
  padding: 20px;
  display: grid;
  gap: 15px;
}
/* #endregion */

/* #region 卡片 */

/* #region 考试卡片 */
.exam-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  transition: all 0.3s ease;
  cursor: pointer;
  border-left: 6px solid #4b6cb7;
}

.exam-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
}

.card-main {
  padding: 20px;
}
/* #endregion */

/* #region 卡片标题 */
.exam-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.exam-header h3 {
  font-size: 1.2rem;
  font-weight: 600;
  color: #2d3748;
  margin: 0;
}

.exam-credit {
  background: #e2e8f0;
  padding: 4px 12px;
  border-radius: 50px;
  font-size: 0.9rem;
  font-weight: 500;
}
/* #endregion */

/* #region 卡片内容 */
.exam-time,
.exam-location,
.countdown,
.exam-status {
  display: flex;
  margin-bottom: 8px;
}

.time-label,
.location-label,
.countdown-label,
.status-label {
  font-weight: 500;
  color: #4a5568;
  min-width: 80px;
}

.time-value,
.location-value,
.countdown-value,
.status-value {
  font-weight: 500;
}
/* #endregion */

/* #region 卡片抽屉 */
.card-details {
  max-height: 0;
  overflow: hidden;
  transition: max-height 0.3s ease;
  background: #f8fafc;
}

.card-details.expanded {
  max-height: 200px;
  padding: 15px 20px;
}

.detail-row {
  display: flex;
  margin-bottom: 8px;
}

.detail-label {
  font-weight: 500;
  color: #4a5568;
  min-width: 80px;
}
/* #endregion */

/* #region 状态样式 */
.status-pending {
  border-left-color: #ef4444;
}

.status-pending .countdown-value {
  color: #ef4444;
  font-weight: 700;
}

.status-ongoing {
  border-left-color: #3b82f6;
}

.status-ongoing .status-value {
  color: #3b82f6;
  font-weight: 700;
}

.status-completed {
  border-left-color: #10b981;
}

.status-completed .status-value {
  color: #10b981;
  font-weight: 700;
}

.status-unknown {
  border-left-color: #94a3b8;
}
/* #endregion */

/* #endregion */

/* #region 响应式设计 */
@media (max-width: 768px) {
  .header {
    padding: 20px;
  }
  
  .exam-list {
    padding: 15px;
  }
  
  .card-main {
    padding: 15px;
  }
}
/* #endregion */
</style>