<template>
  <div class="admin-container">
    <div class="section admin-header">
      <p style="color: red;">如果您在不知情的情况下被其他人引导至此，请立即离开本页面。您不仅不可能达成目标，还可能被泄露隐私。</p>
    </div>
    
    <!-- 认证区域 -->
    <div class="section">
      <form class="form-group">
        <div class="auth-section">
          <div class="form-group" style="width: 30%;">
            <input type="text" class="form-input adminname" v-model="adminname" placeholder="输入用户名">
          </div>
          
          <div class="form-group" style="width: 70%;">
            <input type="password" class="form-input adminpass" v-model="adminpass" placeholder="输入token" autocomplete="none">
          </div>
        </div>

        <select class="selector-dropdown" v-model="selectedOperation" @change="selectedOperationChange">
          <option v-for="(value, op) in operations" :key="op" :value="op">{{ value }}</option>
        </select>
      </form>
    </div>
    
    <!-- 操作面板 -->
    <div class="section operation-panel" v-if="selectedOperation">
      <!-- 添加超级用户 -->
      <div v-if="selectedOperation === 'addsu'">
        <form>
          <div class="form-group">
            <input type="text" class="form-input" v-model="addsuFormData.username" placeholder="要添加的用户名">
            <input type="text" class="form-input" v-model="addsuFormData.level" placeholder="用户权限(1/2/3)">
            <input type="text" class="form-input" v-model="addsuFormData.comment" placeholder="注释">
          </div>
        </form>
        
        <button class="btn btn-primary btn-submit" @click="addsuSubmit">确认添加</button>
        <MDialog :dialog="addsuDialogCompleteHint" title="添加成功">
          <p>用户名：{{ addsuFormData.username }}</p>
          <p>Token：{{ addsuResp.data.token }}</p>
          <p>Level：{{ addsuResp.data.level }}</p>
          <p>Token已经复制到剪贴板</p>
        </MDialog>
      </div>

      <!-- 查询超级用户 -->
      <div v-else-if="selectedOperation === 'lstsu'">
        <button class="btn btn-primary btn-submit" @click="lstsuSubmit">确认查询</button>
        <MDialog :dialog="lstsuDialogCompleteHint" title="查询超级用户">
          <table>
            <thead>
              <tr>
                <th>用户名</th>
                <th>Level</th>
                <th>注释</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in lstsuResp.data" :key="user.username">
                <td>{{ user.username }}</td>
                <td>{{ user.level }}</td>
                <td>{{ user.comment }}</td>
              </tr>
            </tbody>
          </table>

        </MDialog>
      </div>
      
      <!-- 删除超级用户 -->
      <div v-else-if="selectedOperation === 'delsu'">
        <form>
          <div class="form-group">
            <input type="text" class="form-input" v-model="delsuFormData.username" placeholder="要删除的用户名">
          </div>
        </form>
        <button class="btn btn-primary btn-submit" @click="delsuSubmit">确认删除</button>
      </div>
      
      <!-- 添加公告 -->
      <div v-else-if="selectedOperation === 'addan'">
        <form>
          <div class="form-group">
            <input type="text" class="form-input" v-model="addanFormData.title" placeholder="公告标题">
            <textarea class="form-input" v-model="addanFormData.content" placeholder="公告内容"></textarea>
            <input type="text" class="form-input" v-model="addanFormData.date" placeholder="公告日期">
            <input type="text" class="form-input" v-model="addanFormData.tag" placeholder="公告标签">
            <div class="rflex-container">
              <input type="range" class="form-input hue-slider" v-model="addanFormData.hue" min="0" max="360" step="30" placeholder="色调值(0-360)">
              <select class="form-input" :style="{
                'border': '2px solid hsl(var(--hue), 100%, 80%)',
                '--hue': addanFormData.hue
              }" v-model="addanFormData.category">
                <option value="normal">普通 / {{ addanFormData.hue }}</option>
                <option value="important">重要 / {{ addanFormData.hue }}</option>
                <option value="hidden">隐藏 / {{ addanFormData.hue }}</option>
              </select>
            </div>
          </div>
        </form>
        <button class="btn btn-primary btn-submit" @click="addanSubmit">确认添加</button>
      </div>
      
      <!-- 删除公告 -->
      <div v-else-if="selectedOperation === 'delan'">
        <div v-if="dmIsReady">
          <form>
            <div class="form-group">
              <select class="form-input" v-model="selectedAnnouncementId" @change="loadAnnouncementDetails" :ref="(el) => { if (el) delanSelRef = el }">
                <option disabled value="">选择要删除的公告</option>
                <option 
                  v-for="announcement in announcements" 
                  :key="announcement.id"
                  :value="announcement.id"
                >
                  #{{ announcement.id }} {{ announcement.title }}
                </option>
              </select>
            </div>
          </form>
          <button class="btn btn-danger btn-submit" @click="delanSubmit">确认删除</button>
        </div>
        <div v-else>
          等待数据加载…………
        </div>
      </div>
      
      <!-- 修改公告 -->
      <div v-else-if="selectedOperation === 'modan'">
        <div v-if="dmIsReady">
          <form>
            <div class="form-group">
              <select class="form-input" 
                v-model="selectedAnnouncementId" 
                @change="loadAnnouncementDetails" 
                :ref="(el) => { if (el) modanSelRef = el }"
              >
                <option disabled value="">选择要修改的公告</option>
                <option 
                  v-for="announcement in announcements" 
                  :key="announcement.id"
                  :value="announcement.id"
                >
                  #{{ announcement.id }} {{ announcement.title }}
                </option>
              </select>
              <div :ref="(el) => { if (el) modanFormRef = el }" style="display: none;">
                <input type="text" class="form-input" v-model="modanFormData.title" placeholder="新标题">
                <textarea class="form-input" v-model="modanFormData.content" placeholder="新内容"></textarea>
                <input type="text" class="form-input" v-model="modanFormData.date" placeholder="新日期">
                <input type="text" class="form-input" v-model="modanFormData.tag" placeholder="新标签">
                <div class="rflex-container">
                  <input type="range" class="form-input hue-slider" 
                    v-model="modanFormData.hue" 
                    min="0" max="360" step="30">
                  <select class="form-input" v-model="modanFormData.category"
                    :style="{ 'border': '2px solid hsl(var(--hue), 100%, 80%)', '--hue': modanFormData.hue }">
                    <option value="normal">普通</option>
                    <option value="important">重要</option>
                    <option value="hidden">隐藏</option>
                  </select>
                </div>
              </div>
            </div>
          </form>
          <button class="btn btn-primary btn-submit" @click="modanSubmit">确认修改</button>
        </div>
        <div v-else>
          等待数据加载…………
        </div>
      </div>
      
      <!-- 添加活动 -->
      <div v-else-if="selectedOperation === 'addev'">
        <form>
          <div class="form-group">
            <input type="text" class="form-input" v-model="addevFormData.title" placeholder="活动标题">
            <textarea class="form-input" v-model="addevFormData.description" placeholder="活动内容(支持Markdown)"></textarea>
            <input type="text" class="form-input" v-model="addevFormData.date_tag" placeholder="YYYY.MM.DD报名, YYYY.MM.DD - YYYY.MM.DD">
            <input type="number" class="form-input" v-model="addevFormData.timestamp" placeholder="排序时间戳">
            <input type="url" class="form-input" v-model="addevFormData.prevImg" placeholder="thumb URL">
          </div>
        </form>
        <button class="btn btn-primary btn-submit" @click="addevSubmit">确认添加</button>
      </div>
      
      <!-- 删除活动 -->
      <div v-else-if="selectedOperation === 'delev'">
        <div v-if="dmIsReady">
          <form>
            <div class="form-group">
              <select class="form-input" v-model="selectedEventId" @change="loadEventDetails" :ref="(el) => { if (el) delevSelRef = el }">
                <option disabled value="">选择要删除的活动</option>
                <option 
                  v-for="[key, event] in Object.entries(events)" 
                  :key="key"
                  :value="key"
                  :disabled="key === '_placeholder'"
                >
                  #{{ event.id }} {{ event.title }}
                </option>
              </select>
            </div>
          </form>
          <button class="btn btn-danger btn-submit" @click="delevSubmit">确认删除</button>
        </div>
        <div v-else>
          等待数据加载…………
        </div>
      </div>
      
      <!-- 修改活动 -->
      <div v-else-if="selectedOperation === 'modev'">
        <div v-if="dmIsReady">
          <form>
            <div class="form-group">
              <select class="form-input" 
                v-model="selectedEventId" 
                @change="loadEventDetails" 
                :ref="(el) => { if (el) modevSelRef = el }"
              >
                <option disabled value="">选择要修改的活动</option>
                <option 
                  v-for="[key, event] in Object.entries(events)" 
                  :key="key"
                  :value="key"
                  :disabled="key === '_placeholder'"
                >
                  #{{ event.id }} {{ event.title }}
                </option>
              </select>
              <div :ref="(el) => { if (el) modevFormRef = el }" style="display: none;">
                <input type="text" class="form-input" v-model="modevFormData.title" placeholder="新标题">
                <textarea class="form-input" v-model="modevFormData.description" placeholder="新内容(md+格式)"></textarea>
                <input type="text" class="form-input" v-model="modevFormData.date_tag" placeholder="新日期">
                <input type="number" class="form-input" v-model="modevFormData.timestamp" placeholder="新时间戳">
                <input type="url" class="form-input" v-model="modevFormData.prevImg" placeholder="新预览图URL">
              </div>
            </div>
          </form>
          <button class="btn btn-primary btn-submit" @click="modevSubmit">确认修改</button>
        </div>
        <div v-else>
          等待数据加载…………
        </div>
      </div>
    </div>

    <MDialog :dialog="globalDialogLoad" title="加载中......"></MDialog>
    <MDialog :dialog="globalDialogAlert" :title="globalDialogAlertMsg">{{ globalDialogAlertContent }}</MDialog>
    <!-- 公告预览 -->
    <MDialog :dialog="announcementDialogPreview" title="公告预览" confirmText="提交">
      <div class="preview-background-mask">
        <MAnnouncement :announcement="announcementPreview" is-static />
      </div>
    </MDialog>
    <!-- 活动预览 -->
    <MDialog :dialog="eventDialogPreview" title="活动预览" confirmText="提交">
      <div class="preview-background-mask">
        <MEvent :event="eventPreview" />
        <p>{{ eventPreview }}</p>
      </div>
    </MDialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import clipboard from 'clipboard'
import MDialog from '@/components/MDialog.vue'
import createDialog from '@/models/dialogs.js'
import DataModel from '@/models/DataModel.js'
import MAnnouncement from '@/components/MAnnouncement.vue';
import MEvent from '@/components/MEvent.vue';


// #region 公共操作
const dmIsReady = ref(false)
const announcements = ref([]);
const events = ref({})
const loadEvent = () => {
  if (Object.keys(DataModel.server?.events).length === 0) {
    events.value = {
      "_placeholder": {
        "title": "暂无活动",
        "description": "暂无活动",
        "date_tag": "-",
        "timestamp": "0",
        "prevImg": "/img/exam_unknown_thumb.png"
      }
    }
  } else {
    events.value = {
      ...DataModel.server?.events,
    }
  }
}
onMounted(() => {
  nextTick(() => {
    if (!DataModel.serverUpdating) {
      dmIsReady.value = true;
      announcements.value = DataModel.server?.announcements?.normal || [];
      loadEvent()
    } else {
      (async () => {
        await DataModel.serverUpdatePromise;
        dmIsReady.value = true;
        announcements.value = DataModel.server?.announcements?.normal || [];
        loadEvent()
      })()
    }
  });
});

// 认证数据
const adminname = ref('')
const adminpass = ref('')
const bearerToken = computed(() => {
  return `${adminname.value}+${adminpass.value}`
})
const apiBase = window.location.protocol + "//" + DataModel.proxy

// 操作
const globalDialogLoad = createDialog('load')
const globalDialogAlert = createDialog('alert')
const globalDialogAlertMsg = ref('')
const globalDialogAlertContent = ref('')
async function dialogAlert(msg, content) {
  globalDialogAlertMsg.value = msg
  globalDialogAlertContent.value = content
  await globalDialogAlert.alert()
}
const requestOp = async (endpoint, formData) => {
  globalDialogLoad.load()

  try {
    let response;
    let respjson;
    if (formData){
      response = await fetch(apiBase + endpoint, {
        method: 'POST',
        body: JSON.stringify(formData),
        headers: {
          'Authorization': bearerToken.value,
          'Content-Type': 'application/json'
        }
      })
    } else {
      response = await fetch(apiBase + endpoint, {
        method: 'GET',
        headers: {
          'Authorization': bearerToken.value,
        }
      })
    }
    respjson = await response.json()
    if (respjson.error !== 0) {
      throw new Error(respjson.message)
    }
    return respjson
  } catch (error) {
    console.error(endpoint, error)
    globalDialogLoad.loadCancel()
    dialogAlert('请求失败', error.message)
    return respjson;
  } finally {
    globalDialogLoad.loadCancel()
  }
}

const selectedOperation = ref('')
const operations = ref({
  addsu: '添加超级用户',
  lstsu: '查询超级用户',
  delsu: '删除超级用户',
  addan: '添加公告',
  delan: '删除公告',
  modan: '修改公告',
  addev: '添加活动',
  delev: '删除活动',
  modev: '修改活动'
})

const selectedOperationChange = () => {
  if (selectedOperation.value === 'modan') {
    modanSelRef.value.style.display = 'block'
    modanFormData.value = modanFormDataInit
    selectedAnnouncementId.value = ''
  } else if (selectedOperation.value === 'delan') {
    selectedAnnouncementId.value = ''
  } else if (selectedOperation.value === 'modev') {
    modevSelRef.value.style.display = 'block'
    modevFormData.value = modevFormDataInit
    selectedEventId.value = ''
  } else if (selectedOperation.value === 'delev') {
    selectedEventId.value = ''
  }

}
// #endregion

// #region 超级用户

// #region 添加超级用户 addsu
const addsuFormData = ref({
  username: '',
  level: ''
})
const addsuDialogCompleteHint = createDialog('alert')
const addsuResp = ref({
  error: 0,
  message: '',
  data: {
    username: '',
    token: '',
    level: ''
  }
})
const addsuSubmit = async () => {
  const respjson = await requestOp('/api/addsu', addsuFormData.value)
  if (!respjson) {
    return;
  }
  addsuResp.value = respjson
  clipboard.copy(respjson.data.token)
  addsuDialogCompleteHint.alert()
}
// #endregion

// #region 查询超级用户 lstsu
const lstsuResp = ref({
  error: 0,
  message: '',
  data: []
})
const lstsuDialogCompleteHint = createDialog('alert')
const lstsuSubmit = async () => {
  const respjson = await requestOp('/api/lstsu')
  if (!respjson) {
    return;
  }
  lstsuResp.value = respjson
  if (lstsuResp.value.error == 0) {
    lstsuDialogCompleteHint.alert()
  } else {
    dialogAlert('查询失败', lstsuResp.value.message)
  }
}
// #endregion

// #region 删除超级用户 delsu
const delsuFormData = ref({
  username: ''
})
const delsuResp = ref({
  error: 0,
  message: ''
})
const delsuSubmit = async () => {
  const respjson = await requestOp('/api/delsu', delsuFormData.value)
  if (!respjson) {
    return;
  }
  delsuResp.value = respjson
  if (delsuResp.value.error == 0) {
    dialogAlert('删除成功', delsuResp.value.message)
  } else {
    dialogAlert('删除失败', delsuResp.value.message)
  }
}
// #endregion

// #endregion

// #region 公告

const announcementPreview = ref({})
const announcementDialogPreview = createDialog('confirm')
const selectedAnnouncementId = ref('');

// #region 添加公告 addan
const addanFormData = ref({
  title: '',
  content: '',
  date: new Date()
    .toLocaleString('sv', { timeZone: 'Asia/Shanghai' })
    .replace('T', ' ').slice(0, 16),  // YYYY-mm-DD HH:MM
  timestamp: Math.floor(Date.now() / 1000),
  tag: '',
  hue: 210,
  category: 'normal'
})
const addanResp = ref({
  error: 0,
  message: '',
  data: {
    id: ''
  }
})
const addanSubmit = async () => {
  announcementPreview.value = addanFormData.value
  if (!await announcementDialogPreview.confirm()) {
    return
  }

  const respjson = await requestOp('/api/addan', { announcement: addanFormData.value })
  if (!respjson) {
    return;
  }
  addanResp.value = respjson
  dialogAlert('添加成功', `公告ID: ${respjson.data.id}`)
}
// #endregion

// #region 删除公告 delan
const delanFormData = ref({
  id: ''
})
const delanResp = ref({
  error: 0,
  message: ''
})
const delanSubmit = async () => {
  if (!selectedAnnouncementId.value) {
    dialogAlert('请先选择公告')
    return
  }
  delanFormData.value.id = selectedAnnouncementId.value
  const respjson = await requestOp('/api/delan', delanFormData.value)
  if (!respjson) {
    return;
  }
  delanResp.value = respjson
  dialogAlert('删除成功')
}
// #endregion

// #region 修改公告 modan
const modanSelRef = ref(null)
const modanFormRef = ref(null)
const modanFormDataInit = {
  id: '',
  title: '',
  content: '',
  date: '',
  tag: '',
  hue: '',
  category: ''
}
const modanFormData = ref(modanFormDataInit)
const modanResp = ref({
  error: 0,
  message: ''
})
const loadAnnouncementDetails = async () => {
  modanSelRef.value.style.display = 'none'
  modanFormRef.value.style.display = 'block'
  const announcement = announcements.value.find(a => a.id === selectedAnnouncementId.value);
  if (announcement) {
    modanFormData.value = {
      id: announcement.id,
      title: announcement.title,
      content: announcement.content,
      date: announcement.date,
      tag: announcement.tag,
      hue: announcement.hue,
      category: announcement.category || 'normal'
    };
  }
};
const modanSubmit = async () => {
  if (!modanFormData.value.id) {
    dialogAlert('请先选择公告')
    return
  }

  const formData = {
    id: modanFormData.value.id,
    announcement: {
      title: modanFormData.value.title,
      content: modanFormData.value.content,
      date: modanFormData.value.date,
      tag: modanFormData.value.tag,
      hue: modanFormData.value.hue,
      category: modanFormData.value.category
    }
  }
  console.debug("modanSubmit", formData)
  announcementPreview.value = modanFormData.value
  if (!await announcementDialogPreview.confirm()) {
    return
  }
  const respjson = await requestOp('/api/modan', formData)
  if (!respjson) {
    return;
  }
  modanResp.value = respjson
  dialogAlert('修改成功')
}
// #endregion

// #endregion

// #region 活动

const eventPreview = ref({})
const eventDialogPreview = createDialog('confirm')
const selectedEventId = ref('');

// #region 添加活动 addev
const addevFormData = ref({
  title: '',
  description: '',
  date_tag: '',
  timestamp: Math.floor(Date.now() / 1000),
  prevImg: '/img/exam_unknown_thumb.png'
})
const addevResp = ref({
  error: 0,
  message: '',
  data: {
    id: ''
  }
})
const addevSubmit = async () => {
  eventPreview.value = addevFormData.value
  if (!await eventDialogPreview.confirm()) {
    return
  }

  const respjson = await requestOp('/api/addev', { event: addevFormData.value })
  if (!respjson) {
    return;
  }
  addevResp.value = respjson
  dialogAlert('添加成功', `活动ID: ${respjson.data.id}`)
}
// #endregion

// #region 删除活动 delev
const delevSelRef = ref(null)
const delevFormData = ref({
  id: ''
})
const delevResp = ref({
  error: 0,
  message: ''
})
const delevSubmit = async () => {
  if (!selectedEventId.value) {
    dialogAlert('请先选择活动')
    return
  }
  delevFormData.value.id = selectedEventId.value
  const respjson = await requestOp('/api/delev', delevFormData.value)
  if (!respjson) {
    return;
  }
  delevResp.value = respjson
  dialogAlert('删除成功')
}
// #endregion

// #region 修改活动 modev
const modevSelRef = ref(null)
const modevFormRef = ref(null)
const modevFormDataInit = {
  id: '',
  title: '',
  description: '',
  date_tag: '',
  timestamp: 0,
  prevImg: ''
}
const modevFormData = ref(modevFormDataInit)
const modevResp = ref({
  error: 0,
  message: ''
})
const loadEventDetails = async () => {
  modevSelRef.value.style.display = 'none'
  modevFormRef.value.style.display = 'block'
  const event = Object.values(events.value).find(e => e.id === selectedEventId.value);
  if (event) {
    modevFormData.value = {
      id: event.id,
      title: event.title,
      description: event.description,
      date_tag: event.date_tag,
      timestamp: event.timestamp,
      prevImg: event.prevImg
    };
  }
};
const modevSubmit = async () => {
  if (!modevFormData.value.id) {
    dialogAlert('请先选择活动')
    return
  }

  const formData = {
    id: modevFormData.value.id,
    event: {
      title: modevFormData.value.title,
      description: modevFormData.value.description,
      date_tag: modevFormData.value.date_tag,
      timestamp: modevFormData.value.timestamp,
      prevImg: modevFormData.value.prevImg
    }
  }
  
  eventPreview.value = modevFormData.value
  if (!await eventDialogPreview.confirm()) {
    return
  }
  
  const respjson = await requestOp('/api/modev', formData)
  if (!respjson) {
    return;
  }
  modevResp.value = respjson
  dialogAlert('修改成功')
}
// #endregion

// #endregion
</script>

<style scoped>
/* #region 管理界面主框架 */
.admin-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
  background-color: #fff7f7c0;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  margin-top: 20px;
}

.section {
  border-bottom: 1px solid #888c;
  margin-bottom: 8px;
  padding-bottom: 8px;
}
/* #endregion */

/* #region 块格式 */
.admin-header {
  text-align: center;
}

.auth-section {
  display: flex;
  flex-direction: row;
  gap: 8px;
}

.selector-label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  color: #212121;
}

.selector-dropdown {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  background-color: #fff;
}

.operation-panel {
  /* background-color: #fff; */
  padding-bottom: 8px;
  margin-bottom: 8px;
}
/* #endregion */

/* #region 表单 */
.form-label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  color: #212121;
}

.form-input {
  font-family: 'Noto Sans SC', sans-serif;
  box-sizing: border-box;
  background-color: #fff;
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  margin-bottom: 8px;
}

.form-input:focus {
  outline: none;
  border-color: #888;
}
/* #endregion */

/* #region 按钮 */
.btn {
  padding: 12px 20px;
  background-color: #888;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn:hover {
  background-color: #666;
}

.btn-primary {
  background-color: #4a6ee0;
}

.btn-primary:hover {
  background-color: #3a5ec0;
}

.btn-danger {
  background-color: #e04a4a;
}

.btn-danger:hover {
  background-color: #c03a3a;
}


.btn-submit {
  width: 100%;
}
/* #endregion */

/* #region 自定义的一些小东西 */
.rflex-container {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 8px;
}

.hue-slider {
  -webkit-appearance: none;
  width: 100%;
  height: 3px;
  background: linear-gradient(to right, red, yellow, lime, cyan, blue, magenta, red);
  outline: none;
  padding: 0;
  box-sizing: border-box;
  border: none;
}

.hue-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 18px;
  height: 18px;
  background: #fff;
  border-radius: 50%;
  border: 2px solid #333;
  cursor: pointer;
}
/* 预览 */
.preview-background-mask {
  background: repeating-linear-gradient(45deg,
      #f5f5f5,
      #f5f5f5 10px,
      #e0e0e0 10px,
      #e0e0e0 20px);

  padding: 20px 5px;
  text-align: left;
}

/* #endregion */

</style>