<template>
  <div class="view-container">
    <div class="header">
      <h1><i class="fas fa-graduation-cap"></i> {{ pageTitle }}</h1>
      <p>查看所有课程考试成绩及相关信息</p>
      
      <div class="stats-container">
        <div class="stat-card">
          <div class="value">{{ stats.courses }}</div>
          <div class="label">总课程数</div>
        </div>
        <div class="stat-card">
          <div class="value">{{ stats.avgScore }}</div>
          <div class="label">平均成绩</div>
        </div>
        <div class="stat-card">
          <div class="value">{{ stats.makeups }}</div>
          <div class="label">补考课程</div>
        </div>
      </div>
    </div>
    
    <div class="controls">
      <div class="search-box">
        <i class="fas fa-search"></i>
        <input 
          type="text" 
          v-model="searchQuery" 
          placeholder="搜索课程名称..."
          @input="handleSearch"
        >
      </div>
      
      <div class="expand-toggle" @click="toggleDetails">
        <i class="fas" :class="showDetails ? 'fa-compress' : 'fa-expand'"></i>
        <span>{{ showDetails ? '收起详情' : '展开详情' }}</span>
      </div>
    </div>
    
    <div class="table-container">
      <table class="score-table">
        <thead>
          <tr>
            <th>课程名称</th>
            <th>学期</th>
            <th>成绩</th>
            <th v-if="showDetails">课程编号</th>
            <th v-if="showDetails">学分</th>
            <th v-if="showDetails">学时</th>
            <th>补考情况</th>
            <th v-if="showDetails">课程属性</th>
            <th v-if="showDetails">考核方式</th>
            <th v-if="showDetails">授课教师</th>
            <th v-if="showDetails">考试时间</th>
            <th v-if="showDetails">考场</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(exam, index) in filteredExams" :key="index">
            <td>
              <div class="subject-name">{{ exam.课程名称 }}</div>
            </td>
            <td>{{ exam.开课学期 || '—' }}</td>
            <td>
              <span class="score-value" :class="getScoreClass(exam.考试成绩?.成绩)">
                {{ exam.考试成绩?.成绩 || '—' }}
              </span>
            </td>
            <td v-if="showDetails">{{ exam.课程编号 || '—' }}</td>
            <td v-if="showDetails">{{ exam.学分 || '—' }}</td>
            <td v-if="showDetails">{{ exam.总学时 || '—' }}</td>
            <td>
              <span v-if="exam.考试成绩?.补重学期" class="makeup-semester">
                {{ exam.考试成绩.补重学期 }}
              </span>
              <span v-else>—</span>
            </td>
            <td v-if="showDetails">{{ exam.课程属性 || '—' }}</td>
            <td v-if="showDetails">{{ exam.考核方式 || '—' }}</td>
            <td v-if="showDetails">{{ exam.考试安排?.授课教师 || '—' }}</td>
            <td v-if="showDetails">{{ exam.考试安排?.考试时间 || '—' }}</td>
            <td v-if="showDetails">{{ exam.考试安排?.考场 || '—' }}</td>
          </tr>
        </tbody>
      </table>
      
      <div v-if="filteredExams.length === 0" class="no-data">
        <i class="fas fa-inbox"></i>
        <p>没有找到匹配的课程信息</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import DataModel from '@/models/DataModel'

const route = useRoute()
const pageTitle = computed(() => route.meta.title || '考试成绩信息')
const exams = ref(DataModel.user?.exam?.subjects || [])
const searchQuery = ref('')
const showDetails = ref(false)

// 统计数据
const stats = computed(() => {
  const validExams = exams.value.filter(e => e.考试成绩?.成绩)
  const makeups = exams.value.filter(e => e.考试成绩?.补重学期).length
  
  return {
    courses: exams.value.length,
    avgScore: validExams.length 
      ? (validExams.reduce((sum, e) => sum + Number(e.考试成绩.成绩), 0) / validExams.length).toFixed(1)
      : '—',
    makeups
  }
})

// 过滤后的考试列表
const filteredExams = computed(() => {
  if (!searchQuery.value) return exams.value
  
  const query = searchQuery.value.toLowerCase()
  return exams.value.filter(exam => 
    exam.课程名称.toLowerCase().includes(query) || 
    exam.课程编号?.toLowerCase().includes(query)
  )
})

// 根据分数返回样式类
const getScoreClass = (score) => {
  if (!score) return ''
  if (score >= 90) return 'score-excellent'
  if (score >= 80) return 'score-good'
  if (score >= 70) return 'score-average'
  return 'score-poor'
}

// 切换详情显示
const toggleDetails = () => {
  showDetails.value = !showDetails.value
}
</script>

<style scoped>
.view-container {
  max-width: 1200px;
  margin: 0 auto;
  background: white;
  border-radius: 16px;
  /* box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08); */
  overflow: hidden;
}

.header {
  background: linear-gradient(120deg, #4b6cb7 0%, #182848 100%);
  color: white;
  padding: 30px 40px;
  position: relative;
}

.header h1 {
  font-weight: 600;
  font-size: 2.2rem;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 15px;
}

.header p {
  opacity: 0.85;
  max-width: 600px;
  line-height: 1.6;
}

.stats-container {
  display: flex;
  gap: 20px;
  margin-top: 25px;
  flex-wrap: wrap;
}

.stat-card {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 18px 25px;
  min-width: 180px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.stat-card .value {
  font-size: 2.2rem;
  font-weight: 700;
  margin-bottom: 5px;
}

.stat-card .label {
  font-size: 0.9rem;
  opacity: 0.85;
}

.controls {
  background: #f8fafc;
  padding: 20px 40px;
  border-bottom: 1px solid #eaeff5;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 15px;
}

.search-box {
  display: flex;
  align-items: center;
  background: white;
  border-radius: 50px;
  padding: 8px 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  border: 1px solid #e2e8f0;
}

.search-box input {
  border: none;
  padding: 8px 12px;
  min-width: 250px;
  outline: none;
  background: transparent;
}

.expand-toggle {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: #4b6cb7;
  font-weight: 500;
  padding: 8px 15px;
  border-radius: 50px;
  transition: all 0.3s ease;
}

.expand-toggle:hover {
  background: #ebf4ff;
}

.table-container {
  padding: 20px 30px;
  overflow-x: auto;
}

.score-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
}

.score-table th {
  background: #f1f5f9;
  text-align: left;
  padding: 18px 20px;
  font-weight: 600;
  color: #4a5568;
  text-transform: uppercase;
  font-size: 0.85rem;
  letter-spacing: 0.5px;
  border-bottom: 2px solid #e2e8f0;
}

.score-table td {
  padding: 18px 20px;
  border-bottom: 1px solid #edf2f7;
  transition: background 0.2s;
}

.score-table tbody tr:last-child td {
  border-bottom: none;
}

.score-table tbody tr:hover td {
  background: #f8fafc;
}

.subject-name {
  font-weight: 600;
  color: #2d3748;
  display: flex;
  align-items: center;
  gap: 12px;
}

.score-value {
  font-weight: 700;
  font-size: 1.1rem;
}

.score-excellent {
  color: #10b981;
}

.score-good {
  color: #3b82f6;
}

.score-average {
  color: #f59e0b;
}

.score-poor {
  color: #ef4444;
}

.makeup-semester {
  background: #fef3c7;
  color: #d97706;
  padding: 5px 12px;
  border-radius: 50px;
  font-size: 0.85rem;
  display: inline-block;
}

.no-data {
  text-align: center;
  padding: 40px;
  color: #94a3b8;
}

.no-data i {
  font-size: 3rem;
  margin-bottom: 15px;
  opacity: 0.5;
}

.no-data p {
  font-size: 1.1rem;
}

@media (max-width: 768px) {
  .header {
    padding: 20px;
  }
  
  .controls {
    padding: 15px;
  }
  
  .search-box input {
    min-width: 150px;
  }
  
  .score-table {
    font-size: 0.9rem;
  }
  
  .score-table th, 
  .score-table td {
    padding: 12px 15px;
  }
}
</style>