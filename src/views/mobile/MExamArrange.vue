<template>
  <div class="exam-arrange-container">
    <div v-if="upcomingExams.length === 0 && completedExams.length === 0" class="empty-state">
      <i class="fas fa-calendar-times"></i>
      <h3>暂无考试安排</h3>
      <p>当前没有找到有效的考试安排信息</p>
    </div>

    <!-- 即将到来的考试 -->
    <div v-if="upcomingExams.length > 0" class="exam-section">
      <div class="section-header">
        <i class="fas fa-clock"></i>
        <h2>即将进行的考试</h2>
      </div>
      <div class="exam-cards">
        <div v-for="exam in upcomingExams" :key="exam.课程编号" class="arrange-card upcoming">
          <div class="card-header">
            <div class="subject-name">{{ exam.课程名称 }}</div>
            <div class="countdown-badge">
              <i class="fas fa-hourglass-half"></i>
              {{ exam.countdownText }}
            </div>
          </div>

          <div class="card-details">
            <div class="detail-item">
              <i class="fas fa-graduation-cap"></i>
              <span>{{ exam.学分 }}学分</span>
            </div>
            <div class="detail-item">
              <i class="fas fa-map-marker-alt"></i>
              <span>{{ exam.考试安排.考场 || '待定' }}</span>
            </div>
          </div>

          <div class="exam-time">
            <i class="fas fa-calendar-alt"></i>
            <span>{{ formatExamDate(exam.考试安排.考试时间) }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 已完成的考试 -->
    <div v-if="completedExams.length > 0" class="exam-section">
      <div class="section-header">
        <i class="fas fa-check-circle"></i>
        <h2>已完成的考试</h2>
      </div>
      <div class="exam-cards">
        <div v-for="exam in completedExams" :key="exam.课程编号" class="arrange-card completed">
          <div class="card-header">
            <div class="subject-name">{{ exam.课程名称 }}</div>
            <div class="countdown-badge">
              <i class="fas fa-check"></i>
              {{ exam.countdownText }}
            </div>
          </div>

          <div class="card-details">
            <div class="detail-item">
              <i class="fas fa-graduation-cap"></i>
              <span>{{ exam.学分 }}学分</span>
            </div>
            <div class="detail-item">
              <i class="fas fa-map-marker-alt"></i>
              <span>{{ exam.考试安排.考场 || '待定' }}</span>
            </div>
          </div>

          <div class="exam-time">
            <i class="fas fa-calendar-alt"></i>
            <span>{{ formatExamDate(exam.考试安排.考试时间) }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import DataModel from '@/models/DataModel';

const now = ref(new Date());

// 过滤并处理考试数据
const processedExams = computed(() => {
  return (DataModel.user?.exam?.subjects || [])
    .filter(exam => exam.考试安排 && exam.考试安排.考试时间)
    .map(exam => {
      // 提取考试开始时间
      const timePart = exam.考试安排.考试时间.split('~')[0];
      const examDate = new Date(timePart.replace(/-/g, '/'));
      const diffTime = examDate - now.value;
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

      let countdownText = '';
      let status = '';
      let daysUntil = diffDays;

      if (diffTime > 0) {
        status = 'upcoming';
        if (diffDays === 1) {
          countdownText = '明天考试';
          daysUntil = 1;
        } else if (diffDays === 0) {
          countdownText = '今天考试';
          daysUntil = 0;
        } else {
          countdownText = `${diffDays}天后`;
          // 计算进度条（最多显示30天内的进度）
          daysUntil = diffDays;
        }
      } else {
        status = 'completed';
        const daysPassed = Math.floor(-diffTime / (1000 * 60 * 60 * 24));
        countdownText = daysPassed === 0 ? '今天完成' : `${daysPassed}天前`;
        daysUntil = -daysPassed;
      }

      return {
        ...exam,
        examDate,
        countdownText,
        status,
        daysUntil
      };
    });
});

// 即将进行的考试（按时间升序）
const upcomingExams = computed(() => {
  return processedExams.value
    .filter(exam => exam.status === 'upcoming')
    .sort((a, b) => a.examDate - b.examDate);
});

// 已完成的考试（按时间降序，最近完成的在前）
const completedExams = computed(() => {
  return processedExams.value
    .filter(exam => exam.status === 'completed')
    .sort((a, b) => b.examDate - a.examDate);
});

// 格式化考试日期
const formatExamDate = (rawTimeStr) => {
  if (!rawTimeStr) return '';
  const timeStr = rawTimeStr.replace(' - ', '-')
  // 提取日期和时间部分
  const [datePart, timeRange] = timeStr.split(' ');
  const [startTime, endTime] = timeRange?.includes('-') ? timeRange?.split('-') : timeRange?.split('~');

  // 格式化日期
  const [year, month, day] = datePart.split('-');
  const formattedDate = `${month}月${day}日`;

  // 格式化时间
  const formatTime = (timeStr) => {
    const [hours, minutes] = timeStr.split(':');
    const hourNum = parseInt(hours, 10);
    return `${hourNum}:${minutes}`;
  };
  return `${formattedDate} ${formatTime(startTime)}-${formatTime(endTime)}`;
}; //2025-07-18 14:00 - 16:00

// 更新时间
let timer;
onMounted(() => {
  timer = setInterval(() => {
    now.value = new Date();
  }, 60000); // 每分钟更新一次
});

onUnmounted(() => {
  clearInterval(timer);
});
</script>

<style scoped>
.exam-arrange-container {
  padding: 16px;
}

/* 空状态样式 */
.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #888;
  background-color: #fff7f7c0;
}

.empty-state i {
  font-size: 48px;
  margin-bottom: 16px;
  color: #c0c0c0;
}

.empty-state h3 {
  margin: 8px 0;
  font-weight: 500;
}

.empty-state p {
  margin: 0;
  font-size: 14px;
}

/* 部分标题 */
.section-header {
  display: flex;
  align-items: center;
  margin: 24px 0 12px 0;
  padding-bottom: 8px;
  border-bottom: 1px solid #eee;
}

.section-header i {
  margin-right: 10px;
  font-size: 18px;
}

.section-header h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

/* 考试卡片容器 */
.exam-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

/* 考试卡片 */
.arrange-card {
  background: #fff7f7c0;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  padding: 16px;
  transition: transform 0.2s, box-shadow 0.2s;
  border-left: 4px solid #4CAF50;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
}

.arrange-card.upcoming {
  border-left-color: #2196F3;
}

.arrange-card.completed {
  border-left-color: #9E9E9E;
  opacity: 0.85;
}

/* 卡片头部 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.subject-name {
  font-weight: 600;
  font-size: 16px;
  color: #333;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
}

.countdown-badge {
  font-size: 13px;
  font-weight: 500;
  padding: 4px 8px;
  border-radius: 12px;
  background: #e3f2fd;
  color: #2196F3;
  display: flex;
  align-items: center;
  min-width: 5em;
  justify-content: center;
}

.arrange-card.completed .countdown-badge {
  background: #f5f5f5;
  color: #757575;
}

.countdown-badge i {
  margin-right: 4px;
  font-size: 12px;
}

/* 卡片详情 */
.card-details {
  display: flex;
  gap: 12px;
  margin: 2px 0;
}

.detail-item {
  display: flex;
  align-items: center;
  font-size: 13px;
  color: #666;
}

.detail-item i {
  margin-right: 6px;
  font-size: 12px;
  color: #9E9E9E;
}

/* 考试时间 */
.exam-time {
  display: flex;
  align-items: center;
  font-size: 13px;
  color: #E91E63;
  font-weight: 500;
}

.exam-time i {
  margin-right: 6px;
}

.arrange-card.completed .exam-time {
  color: #9E9E9E;
}

</style>