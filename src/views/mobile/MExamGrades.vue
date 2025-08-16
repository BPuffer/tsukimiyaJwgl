<template>
  <div class="m-exam-grades">
    <!-- 控制栏 -->
    <div class="controls">
      <!-- 简介模式下的学期筛选 -->
      <div v-if="!props.showDetails" class="term-filter">
        <span style="white-space: nowrap;">学期：</span>
        <select v-model="selectedTerm" class="term-select">
          <option value="">全部学期</option>
          <option v-for="term in uniqueTerms" :key="term" :value="term">{{ term }}</option>
        </select>
      </div>

      <!-- 完全模式下的表达式筛选 -->
      <div v-else class="expression-filter">
        <div class="search-box">
          <i class="fas fa-search"></i>
          <input type="text" v-model="filterExpression" placeholder="输入筛选表达式，如'学分>=3 数学'"
            @keyup.enter="onFilterUpdate">
        </div>
        <span @click="openFilterTipWindow"><i class="fa-solid fa-circle-question" style="font-size: 1.2em;"></i></span>
      </div>
    </div>
    <div v-if="onDebug" class="controls controls-debug">
      <div class="search-box search-box-debug">
        <i class="fa-solid fa-lock"></i>
        <div>
          <input 
            type="text" 
            v-model="debugExpression" 
            placeholder="DataModel已暴露...">
        </div>
      </div>
    </div>
    <!-- 表格容器（带横向滚动控制） -->
    <div class="table-container" :class="{ 'scrollable': props.showDetails }">
      <table class="grades-table" :class="{ 'compact-mode': !props.showDetails }">
        <thead>
          <tr>
            <th>课程名称</th>
            <th>学分</th>
            <th>成绩</th>
            <template v-if="props.showDetails">
              <th>开课学期</th>
              <th>课程编号</th>
              <th>课程属性</th>
              <th>课程性质</th>
              <th>考核方式</th>
              <th>成绩标识</th>
              <th>绩点</th>
              <th>补重学期</th>
              <th>考试性质</th>
            </template>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(exam, index) in filteredExams" :key="index">
            <td>{{ exam.课程名称 || '—' }}</td>
            <td>{{ exam.学分 || '—' }}</td>
            <td :class="getScoreClass(exam.考试成绩?.成绩)">
              {{ exam.考试成绩?.成绩 || '—' }}
            </td>
            <template v-if="props.showDetails">
              <td>{{ exam.开课学期 || '—' }}</td>
              <td>{{ exam.课程编号 || '—' }}</td>
              <td>{{ exam.课程属性 || '—' }}</td>
              <td>{{ exam.课程性质 || '—' }}</td>
              <td>{{ exam.考核方式 || '—' }}</td>
              <td>{{ exam.考试成绩?.成绩标识 || '—' }}</td>
              <td>{{ exam.考试成绩?.绩点 || '—' }}</td>
              <td>{{ exam.考试成绩?.补重学期 || '—' }}</td>
              <td>{{ exam.考试成绩?.考试性质 || '—' }}</td>
            </template>
          </tr>
        </tbody>
      </table>

      <!-- 无数据提示 -->
      <div v-if="filteredExams.length === 0" class="no-data">
        <i class="fas fa-inbox"></i>
        <p>没有找到匹配的课程成绩信息</p>
      </div>
    </div>
  
    <div 
      @click="closeFilterTipWindow" 
      class="filter-tips-mask"
      :class="{'mask-show': filterTipWindowOpening}"
    >
      <div class="filter-tips">
        <div class="tip-title">筛选表达式使用提示：</div>
        <ul>
          <li>多个条件用空格分隔，筛选项将满足全部条件</li>
          <li>支持运算符：=(等于), !=(不等于)。</li>
          <li>针对数值，可以使用>, >=, <, <=</li>
          <li>示例：<code>开课学期=2024-2025-1 学分>=3 概论</code></li>
        </ul>
        <div class="debug-output-container">
          <div v-if="onDebug" class="debug-output">
            {{ debugValue }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import DataModel from '@/models/DataModel'

const props = defineProps({
  showDetails: Boolean
})

// 原始考试数据（过滤掉没有成绩的科目）
const exams = computed(() => {
  return (DataModel.user?.exam?.subjects || [])
    .filter(subject =>
      subject.考试成绩?.成绩 &&
      subject.考试成绩.成绩 !== null &&
      subject.考试成绩.成绩 !== ''
    )
})

// 简单学期筛选
const selectedTerm = ref('')
const uniqueTerms = computed(() => {
  const terms = new Set()
  exams.value.forEach(exam => {
    if (exam.开课学期) terms.add(exam.开课学期)
  })
  return Array.from(terms).sort().reverse()
})

// 复杂表达式筛选
const filterExpression = ref('')
const appliedExpression = ref('')
const expressionConditions = ref([])
const filterTipWindowOpening = ref(false)

// 调试器
const onDebug = computed(() => filterExpression.value == "!debug")
const debugExpression = ref('')
const debugValue = ref('')
const debugCommit = () => {
  try {
    debugValue.value = eval(debugExpression.value)
  } catch (error) {
    debugValue.value = '表达式错误'
  }
}

// 提交防抖
const applyCooldown = 1000
let lastApply = null;
let applyTimeout = null;
const onFilterUpdate = () => {
  if ((Date.now() - lastApply) < applyCooldown) {
    if (!applyTimeout){
      applyTimeout = setTimeout(() => {
        onFilterUpdate()
        clearTimeout(applyTimeout)
        applyTimeout = null;
      }, applyCooldown - (Date.now() - lastApply) + 100)
    }
    return;
  }
  appliedExpression.value = filterExpression.value
  parseExpression()
  lastApply = Date.now()
}
watch(filterExpression, onFilterUpdate)


// 筛选表达式提示窗口
const openFilterTipWindow = () => {
  filterTipWindowOpening.value = true
  if (onDebug.value) { debugCommit() }
}
const closeFilterTipWindow = () => {
  filterTipWindowOpening.value = false
}

// 解析
const parseExpression = () => {
  expressionConditions.value = []

  if (!filterExpression.value.trim()) return

  // 拆分条件（支持带空格的引号包裹值）
  const tokens = filterExpression.value
    .replace('≥', '>=')
    .replace('≤', '<=')
    .replace('≠', '!=')
    .replace('＜', '<')
    .replace('＞', '>')
    .match(/(?:[^\s"']+|"[^"]*"|'[^']*')+/g) || []

  tokens.forEach(token => {
    // 尝试匹配各种运算符
    const match = token.match(/([\u4e00-\u9fa5a-zA-Z0-9_]+)\s*(=|!=|>=|<=|>|<|包含)\s*(.+)/)

    if (match) {
      // 键值对条件
      const key = match[1].trim()
      const operator = match[2].trim()
      let value = match[3].trim()

      // 移除值两端的引号（如果有）
      if ((value.startsWith('"') && value.endsWith('"')) ||
        (value.startsWith("'") && value.endsWith("'"))) {
        value = value.slice(1, -1)
      }

      expressionConditions.value.push({ key, operator, value })
    } else {
      // 纯文本条件（默认在课程名称中搜索）
      expressionConditions.value.push({
        key: '课程名称',
        operator: 'in',
        value: token.trim()
      })
    }
  })
}

// 筛选后的考试数据
const filteredExams = computed(() => {
  if (!props.showDetails) {
    // 简介模式：仅按学期筛选
    if (!selectedTerm.value) return exams.value
    return exams.value.filter(exam => exam.开课学期 === selectedTerm.value)
  }

  // 完全模式：应用表达式筛选
  return expressionConditions.value.length === 0 ? exams.value : exams.value.filter(
    exam => {
    // 检查是否满足所有条件
    return expressionConditions.value.every(condition => {
      const { key, operator, value } = condition
      let examValue = exam[key]

      // 处理嵌套属性
      if (key === '成绩') {
        examValue = exam.考试成绩?.成绩
      } else if (key.startsWith('考试成绩.')) {
        const nestedKey = key.split('.')[1]
        examValue = exam.考试成绩?.[nestedKey]
      }

      // 空值处理
      if (examValue === null || examValue === undefined) {
        examValue = ''
      }

      // 转换为小写用于不区分大小写的比较
      const examValueStr = String(examValue).toLowerCase()
      const conditionValueStr = String(value).toLowerCase()

      // 数值比较（如果可以转换为数字）
      const examValueNum = parseFloat(examValue)
      const conditionValueNum = parseFloat(value)
      const isNumeric = !isNaN(examValueNum) && !isNaN(conditionValueNum)

      switch (operator) {
        case '=':
          if (isNumeric) {
            return examValueNum === conditionValueNum
          }
          return examValueStr === conditionValueStr
        case '!=':
          if (isNumeric) {
            return examValueNum !== conditionValueNum
          }
          return examValueStr !== conditionValueStr
        case '>':
          return isNumeric && examValueNum > conditionValueNum
        case '>=':
          return isNumeric && examValueNum >= conditionValueNum
        case '<':
          return isNumeric && examValueNum < conditionValueNum
        case '<=':
          return isNumeric && examValueNum <= conditionValueNum
        case 'in':
          return examValueStr.includes(conditionValueStr)
        default:
          return true
      }
    })
  })
})

// 分数样式
const getScoreClass = (score) => {
  if (!score) return ''
  const numScore = Number(score)
  if (numScore != NaN){
    if (numScore >= 90) return 'score-excellent'
    if (numScore >= 80) return 'score-good'
    if (numScore >= 70) return 'score-average'
    if (numScore >= 60) return 'score-pass'
    if (numScore < 60) return 'score-fail'
  }
  if (score.includes("不及格")) return 'score-fail'
  if (score.includes("及格")) return 'score-pass'
  if (score.includes("中")) return 'score-average'
  if (score.includes("良")) return 'score-good'
  if (score.includes("优")) return 'score-excellent'
  if (score.includes("不合格")) return 'score-fail'
  if (score.includes("合格")) return 'score-excellent'
  return ''
}
</script>

<style scoped>
.m-exam-grades {
  border-radius: 12px;
}

/* #region 控制栏样式 */
.controls {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.term-filter,
.expression-filter {
  width: 100%;
  display: flex;
  flex-direction: row;
  gap: 10px;
  align-items: center;
  justify-content: stretch;
}

.term-select {
  padding: 10px 15px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 16px;
  background: white;
  min-width: 200px;
  outline: none;
  transition: border-color 0.3s;
}

.term-select:focus {
  border-color: #4e6ef2;
}

.search-box {
  flex: 1;
  position: relative;
  display: flex;
  align-items: center;
}

.search-box i {
  position: absolute;
  left: 15px;
  color: #9e9e9e;
  font-size: 16px;
}

.search-box input {
  width: 100%;
  padding: 10px 15px 10px 40px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 16px;
  transition: border-color 0.3s;
}

.search-box input:focus {
  border-color: #4e6ef2;
  box-shadow: 0 0 0 2px rgba(78, 110, 242, 0.2);
}

/* .debug-commit {
  height: 100%;
  background-color: white;
  border: 2px solid #ff66b3;
} */

/* #endregion 控制栏样式 */

/* #region 表格容器 */
.table-container {
  overflow-x: none;
  overflow-y: auto;
  border-radius: 8px;
  border: 1px solid #eee;
}

.table-container.scrollable {
  overflow-x: auto;
}

/* 简洁模式下的表格样式 */
.grades-table.compact-mode {
  table-layout: fixed;
  width: 100%;
}

.grades-table.compact-mode th,
.grades-table.compact-mode td {
  max-width: 60%;
  word-wrap: break-word;
  white-space: normal;
}

/* 完全模式下的表格样式 */
.grades-table:not(.compact-mode) {
  table-layout: auto;
  min-width: 100%;
}

.grades-table:not(.compact-mode) th,
.grades-table:not(.compact-mode) td {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 300px;
}

/* 调整特定列的宽度 */
.grades-table th:nth-child(1),
.grades-table td:nth-child(1) {
  min-width: 120px;
  max-width: 200px;
}

.grades-table th:nth-child(2),
.grades-table td:nth-child(2) {
  width: 80px;
}

.grades-table th:nth-child(3),
.grades-table td:nth-child(3) {
  width: 80px;
}

/* 完全模式下的列宽调整 */
.grades-table:not(.compact-mode) th:nth-child(1),
.grades-table:not(.compact-mode) td:nth-child(1) {
  max-width: none;
}

/* #endregion 表格容器 */

/* #region 表格样式 */
.grades-table {
  width: 100%;
  border-collapse: collapse;
}

.grades-table th {
  background: #428dff;
  padding: 16px 12px;
  text-align: left;
  font-weight: 600;
  color: #ffffff;
  border-bottom: 2px solid #e0e0e0;
  position: sticky;
  top: 0;
}

.grades-table td {
  padding: 2px 10px;
  border-bottom: 1px solid #ccc;
  color: #555;
  background-color: #f7fcffc0;
}

.grades-table tr:hover td {
  background-color: #f9fbfdc0;
}

/* 分数样式 */
.grades-table .score-excellent {
  color: #00c853;
}

.grades-table .score-good {
  color: #4caf50;
}

.grades-table .score-average {
  color: #ff9800;
}

.grades-table .score-pass {
  color: #f57c00;
}

.grades-table .score-fail {
  color: #f44336;
}
/* #endregion */

/* #region 其他小物件 */
/* 无数据提示 */
.no-data {
  text-align: center;
  padding: 50px 20px;
  color: #888;
  background-color: #fff7f7c0;
}

.no-data i {
  font-size: 48px;
  margin-bottom: 15px;
  color: #888;
}

.no-data p {
  font-size: 18px;
}

/* 筛选提示 */
.filter-tips-mask {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1000;
  pointer-events: none;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s;
}

.filter-tips-mask.mask-show {
  opacity: 1;
  pointer-events: auto;
  transition: opacity 0.3s;
}

.filter-tips {
  width: 80vw;
  line-height: 1.6;
  padding: 20px;
  background: #f9f9f9;
  border-radius: 8px;
  border-left: 3px solid #4e6ef2;
}

.tip-title {
  font-weight: 600;
  margin-bottom: 12px;
  color: #4e6ef2;
}

.filter-tips ul {
  padding-left: 20px;
  margin-top: 10px;
}

.filter-tips li {
  margin-bottom: 8px;
  color: #666;
  line-height: 1.6;
}

.filter-tips code {
  background: #eef2ff;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: monospace;
  color: #4e6ef2;
}

/* 调试器 */
@property --hue {
  syntax: "<number>";
  initial-value: 0;
  inherits: false;
}

@keyframes hueRotate {
  to {
    --hue: 360;
  }
}

@property --complement-hue {
  syntax: "<number>";
  initial-value: 180;
  inherits: false;
}

@keyframes complementHueRotate {
  to {
    --complement-hue: 540;
  }
}

.controls-debug {
  margin-bottom: 20px;
  gap: 20px
}

.search-box-debug input, .search-box-debug i {
  border-width: 2px;
  border-image: linear-gradient(
    to right,
    hsl(var(--hue), 100%, 75%),
    hsl(var(--complement-hue), 100%, 75%)
  ) 1;
  border-radius: 4px;
  color: hsl(var(--hue), 100%, 30%);
  animation: 
    hueRotate 3s linear infinite,
    complementHueRotate 3s linear infinite;
}

.debug-output-container {
  display: flex;
  max-height: 20rem;
  width: 100%;
  overflow: auto;
}

.debug-output {
  width: 100%;
  /* height: 3rem; */
  max-width: 100%;
  color: #fff;
  font-size: 14px;
  margin-top: 10px;
  padding: 5px 10px;
  background-image: linear-gradient(
    to right,
    hsl(var(--hue), 100%, 40%),
    hsl(var(--complement-hue), 100%, 40%)
  );
  animation: hueRotate 3s linear infinite;
  overflow: auto;
  white-space: normal;
  word-wrap: break-word;
  word-break: break-all;
}

/* .debug-output::before {
  content: ">>>";
  font-weight: 600;
  margin-right: 5px;
} */

/* #endregion */

</style>