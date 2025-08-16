<template>
  <!-- 科目卡片列表 -->
  <div class="exam-cards-container">
    <div v-if="processedExams.length === 0" class="empty-state">
      <i class="fas fa-book-open"></i>
      <h3>没有找到科目数据</h3>
      <p>请检查您的课程安排或稍后再试</p>
    </div>

    <div v-for="exam in processedExams" :key="exam.课程编号" class="exam-card"
      :class="{ 'upcoming': exam.status === 'upcoming', 'completed': exam.status === 'completed' }"
      @click="openDrawer(exam)">
      <div class="subject-info">
        <div class="subject-name">{{ exam.课程名称 }}</div>
        <div class="exam-status" :class="exam.status">
          <i v-if="exam.status === 'upcoming'" class="fas fa-hourglass-half"></i>
          <i v-if="exam.status === 'completed'" class="fas fa-check-circle"></i>
          <span>{{ ' ' + exam.countdownText }}</span>
        </div>
      </div>
      <div class="subject-meta">
        <span>{{ exam.开课学期 }}</span>
        <span>•</span>
        <span>{{ exam.学分 }}学分</span>
        <span>•</span>
        <span>{{ exam.总学时 }}学时</span>
      </div>
    </div>
  </div>

  <!-- 抽屉组件 -->
  <div v-if="drawerVisible" class="drawer-mask" @click="closeDrawer">
    <div class="drawer">
      <div class="drawer-header">
        <h2>{{ activeExam.课程名称 }}</h2>
        <button class="close-btn" @click="closeDrawer">
          <i class="fas fa-times"></i>
        </button>
      </div>

      <div class="drawer-content">
        <!-- 基本信息部分 -->
        <div class="info-section">
          <h3>课程信息</h3>
          <div class="info-grid">
            <div class="info-item">
              <label>序号</label>
              <span>{{ activeExam.序号 || '无' }}</span>
            </div>
            <div class="info-item">
              <label>课程编号</label>
              <span>{{ activeExam.课程编号 || '无' }}</span>
            </div>
            <div class="info-item">
              <label>开课学期</label>
              <span>{{ activeExam.开课学期 || '无' }}</span>
            </div>
            <div class="info-item">
              <label>课程名称</label>
              <span>{{ activeExam.课程名称 || '无' }}</span>
            </div>
            <div class="info-item">
              <label>开课单位</label>
              <span>{{ activeExam.开课单位 || '无' }}</span>
            </div>
            <div class="info-item">
              <label>课程属性</label>
              <span>{{ activeExam.课程属性 || '无' }}</span>
            </div>
            <div class="info-item">
              <label>课程性质</label>
              <span>{{ activeExam.课程性质 || '无' }}</span>
            </div>
            <div class="info-item">
              <label>是否考试</label>
              <span>{{ activeExam.是否考试 || '无' }}</span>
            </div>
            <div class="info-item">
              <label>学分</label>
              <span>{{ activeExam.学分 || '无' }}</span>
            </div>
            <div class="info-item">
              <label>总学时</label>
              <span>{{ activeExam.总学时 || '无' }}</span>
            </div>
            <div class="info-item">
              <label>考核方式</label>
              <span>{{ activeExam.考核方式 || '无' }}</span>
            </div>
          </div>
        </div>

        <!-- 考试安排部分 -->
        <div class="info-section" v-if="activeExam.考试安排">
          <h3>考试安排</h3>
          <div class="info-grid">
            <div class="info-item">
              <label>考试时间</label>
              <span>{{ activeExam.考试安排.考试时间 || '-' }}</span>
            </div>
            <div class="info-item">
              <label>考场</label>
              <span>{{ activeExam.考试安排.考场 || '-' }}</span>
            </div>
            <div class="info-item">
              <label>校区</label>
              <span>{{ activeExam.考试安排.校区 || '-' }}</span>
            </div>
            <div class="info-item">
              <label>考试场次</label>
              <span>{{ activeExam.考试安排.考试场次 || '-' }}</span>
            </div>
            <div class="info-item">
              <label>授课教师</label>
              <span>{{ activeExam.考试安排.授课教师 || '-' }}</span>
            </div>
            <div class="info-item">
              <label>座位号</label>
              <span>{{ activeExam.考试安排.座位号 || '-' }}</span>
            </div>
            <div class="info-item">
              <label>准考证号</label>
              <span>{{ activeExam.考试安排.准考证号 || '-' }}</span>
            </div>
          </div>
        </div>

        <!-- 考试成绩部分 -->
        <div class="info-section" v-if="activeExam.考试成绩">
          <h3>考试成绩</h3>
          <div class="info-grid">
            <div class="info-item">
              <label>成绩</label>
              <span class="grade-value">{{ activeExam.考试成绩.成绩 || '-' }}</span>
            </div>
            <div class="info-item">
              <label>绩点</label>
              <span>{{ activeExam.考试成绩.绩点 || '-' }}</span>
            </div>
            <div class="info-item">
              <label>考试性质</label>
              <span>{{ activeExam.考试成绩.考试性质 || '-' }}</span>
            </div>
            <div class="info-item">
              <label>分组名</label>
              <span>{{ activeExam.考试成绩.分组名 || '-' }}</span>
            </div>
            <div class="info-item">
              <label>成绩标识</label>
              <span>{{ activeExam.考试成绩.成绩标识 || '-' }}</span>
            </div>
            <div class="info-item">
              <label>补重学期</label>
              <span>{{ activeExam.考试成绩.补重学期 || '-' }}</span>
            </div>
            <div class="info-item">
              <label>课程类别</label>
              <span>{{ activeExam.考试成绩.课程类别 || '-' }}</span>
            </div>
          </div>
        </div>

        <!-- 无考试安排/成绩提示 -->
        <div v-if="!activeExam.考试安排 && !activeExam.考试成绩" class="no-data-section">
          <i class="fas fa-info-circle"></i>
          <p>暂无考试安排和成绩信息</p>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import DataModel from '@/models/DataModel';

const route = useRoute();
const now = ref(new Date());
const drawerVisible = ref(false);
const activeExam = ref(null);

const exams = ref(DataModel.user?.exam?.subjects || []);

// 处理考试数据，添加状态和倒计时
const processedExams = computed(() => {
  return exams.value.map(exam => {
    let examDate = null;
    let diffDays = null;
    let countdownText = '';
    let status = 'no-arrangement';

    if (exam.考试安排 && exam.考试安排.考试时间) {
      const timePart = exam.考试安排.考试时间.split('~')[0];
      examDate = new Date(timePart.replace(/-/g, '/'));
      const diffTime = examDate - now.value;
      diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

      if (diffTime > 0) {
        status = 'upcoming';
        if (diffDays === 1) {
          countdownText = '明天考试';
        } else if (diffDays === 0) {
          countdownText = '今天考试';
        } else {
          countdownText = `${diffDays}天后`;
        }
      } else {
        status = 'completed';
        const daysPassed = Math.floor(-diffTime / (1000 * 60 * 60 * 24));
        countdownText = daysPassed === 0 ? '今天考完' : `${daysPassed}天前`;
      }
    }

    
    if (exam.考试成绩) {
      countdownText = ` ${exam.考试成绩?.成绩}`;
      status = 'completed';
      if (/^[-+]?(\d+(\.\d*)?|\.\d+)$/.test(`${exam.考试成绩?.成绩}`)) {
        countdownText += '分';
      }
    }

    return {
      ...exam,
      examDate,
      countdownText,
      status
    };
  }).sort((a, b) => {
    // 优先显示有考试安排的，然后按时间排序
    if (a.examDate && b.examDate) return a.examDate - b.examDate;
    if (a.examDate) return -1;
    if (b.examDate) return 1;
    return a.课程名称.localeCompare(b.课程名称);
  });
});

// 格式化考试时间
const formatExamTime = (timeStr) => {
  if (!timeStr) return '';
  const [datePart, timePart] = timeStr.split(' ');
  return `${datePart} ${timePart.split('-')[0]}`;
};

// 打开抽屉
const openDrawer = (exam) => {
  activeExam.value = exam;
  drawerVisible.value = true;
};

// 关闭抽屉
const closeDrawer = () => {
  drawerVisible.value = false;
  setTimeout(() => {
    activeExam.value = null;
  }, 300);
};

onMounted(() => {
  // 更新当前时间（每分钟更新一次）
  setInterval(() => {
    now.value = new Date();
  }, 60000);
});
</script>

<style scoped>
/* #region 考试卡片 */
.exam-cards-container {
  margin-top: 10px;
  padding: 0 10px;
  display: grid;
  grid-template-columns: 1fr;
  gap: 16px;
  margin-bottom: 40px;
}

.exam-card {
  background: #fff7f7c0;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  padding: 18px;
  cursor: pointer;
  /* transition: all 0.25s ease; */
  border-left: 4px solid #3498db;
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: flex-start;
}

.exam-card.upcoming {
  border-left-color: #f39c12;
}

.exam-card.completed {
  border-left-color: #2ecc71;
}

.subject-info {
  flex: 1;
  width: 100%;
  display: flex;
  flex-direction: row;
  flex-wrap: nowrap;
  justify-content: space-between;
  align-items: center;
}

.subject-name {
  font-size: 1.2rem;
  font-weight: 600;
  color: #2c3e50;
}
@media (max-width: 375px) {.subject-name {
    font-size: 1rem;
}}
@media (max-width: 320px) {.subject-name {
    font-size: 0.9rem;
}}


.subject-meta {
  display: flex;
  gap: 3px;
  font-size: 0.9rem;
  color: #7f8c8d;
  flex-wrap: nowrap;
  max-height: 0.9em + 3px;
  overflow: hidden;
}
@media (max-width: 375px) {.subject-meta {
    font-size: 0.84rem;
}}
@media (max-width: 320px) {.subject-meta {
    font-size: 0.78rem;
}}

.exam-status {
  font-weight: 600;
  padding: 6px 12px;
  border-radius: 16px;
  font-size: 0.9rem;
  min-width: 5em;
  text-align: center;
}
@media (max-width: 375px) {.exam-status {
    font-size: 0.84rem;
}}
@media (max-width: 320px) {.exam-status {
    font-size: 0.78rem;
}}

.exam-status.upcoming {
  background: #fef9e7c0;
  color: #f39c12;
}

.exam-status.completed {
  background: #eafaf1c0;
  color: #27ae60;
}
/* #endregion 考试卡片 */

/* #region 抽屉样式 */
.drawer-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1000;
  display: flex;
  justify-content: center;
  align-items: flex-end;
  animation: fadeIn 0.3s ease;
}

.drawer {
  background: white;
  width: 100%;
  max-width: 800px;
  border-radius: 20px 20px 0 0;
  max-height: 85vh;
  overflow-y: auto;
  transform: translateY(0);
  transition: transform 0.3s ease;
  box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.1);
}

.drawer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #eee;
  position: sticky;
  top: 0;
  background: white;
  z-index: 10;
}

.drawer-header h2 {
  margin: 0;
  font-size: 1.4rem;
  color: #2c3e50;
}
@media (max-width: 375px) {.drawer-header h2 {
    font-size: 1.2rem;
}}
@media (max-width: 320px) {.drawer-header h2 {
    font-size: 1.1rem;
}}

.close-btn {
  background: none;
  border: none;
  font-size: 1.2rem;
  color: #7f8c8d;
  cursor: pointer;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  background: #f5f7fa;
  color: #e74c3c;
}

.drawer-content {
  padding: 20px;
  flex: 1;
  display: flex;
  flex-direction: row;
  flex-wrap: nowrap;
  gap: 5px;
}

.info-section {
  padding: 10px;
  flex: 1 0 0;
  min-width: 0;
  border-radius: 20px;
}

.info-section h3 {
  font-size: 1.15rem;
  color: #3498db;
  margin-top: 0;
  margin-bottom: 18px;
  padding-bottom: 8px;
  border-bottom: 1px solid #eee;
}
@media (max-width: 375px) {.info-section h3 {
    font-size: 1.08rem;
}}
@media (max-width: 320px) {.info-section h3 {
    font-size: 0.95rem;
}}

.info-section:nth-child(1) {
  background-color: #f5f7fa;
}

.info-section:nth-child(2) {
  background-color: #fdf5e6;
}

.info-section:nth-child(3) {
  background-color: #e8f7fa;
}


.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 16px;
}

.info-item {
  display: flex;
  flex-direction: column;
}

.info-item label {
  font-size: 0.85rem;
  color: #7f8c8d;
  margin-bottom: 5px;
}
@media (max-width: 375px) {.info-item label {
    font-size: 0.8rem;
}}
@media (max-width: 320px) {.info-item label {
    font-size: 0.75rem;
}}

.info-item span {
  font-size: 1rem;
  color: #2c3e50;
  font-weight: 500;
}
@media (max-width: 375px) {.info-item span {
    font-size: 0.9rem;
}}
@media (max-width: 320px) {.info-item span {
    font-size: 0.85rem;
}}

.grade-value {
  font-weight: 700;
  color: #27ae60;
}

/* #region 小组件 */
/* 抽屉无安排/成绩 */
.no-data-section {
  text-align: center;
  padding: 30px 0;
  color: #7f8c8d;
}

.no-data-section i {
  font-size: 3rem;
  margin-bottom: 15px;
  color: #bdc3c7;
}

.no-data-section p {
  margin: 0;
  font-size: 1.1rem;
}

/* 列表为空 */
.empty-state {
  grid-column: 1 / -1;
  text-align: center;
  padding: 50px 20px;
  background: #fff7f7c0;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
}

.empty-state i {
  font-size: 4rem;
  color: #bdc3c7;
  margin-bottom: 20px;
}

.empty-state h3 {
  color: #7f8c8d;
  margin-bottom: 15px;
}

/* 动画效果 */
@keyframes fadeIn {
  from {
    opacity: 0;
  }

  to {
    opacity: 1;
  }
}

.header-section {
  flex-direction: column;
  align-items: flex-start;
}

.filter-section {
  width: 100%;
  justify-content: center;
}

.info-grid {
  grid-template-columns: 1fr;
}
/* #endregion */

/* #endregion */

</style>