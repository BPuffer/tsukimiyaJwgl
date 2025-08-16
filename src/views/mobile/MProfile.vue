<template>
  <div class="profile-container">
    <!-- :style="{
      justifyContent: noUsers ? 'flex-end' : 'flex-start'
    }" -->
  
    <div class="user-grid">
      <!-- 用户卡片 -->
      <div v-for="(user, id) in dataModel.allLoginUsers" :key="id" 
           class="user-card" 
           :class="{ active: dataModel.currentLoginUser === id }">
        <div class="user-card-top">
          <div v-if="!user.profile?.icon" class="user-card-text-avatar">
            {{ user.profile?.学生姓名?.charAt(0) || '?' }}
          </div>
          <div v-else class="user-card-icon-avatar">
            <img :src="user.profile.icon" alt="头像">
          </div>
          <div class="user-card-ni">
            <p class="user-card-name">{{ user?.profile?.学生姓名 || '佚名' }}</p>
            <p class="user-card-id">{{ id }}</p>
          </div>
        </div>
        
        <div class="user-card-bottom">
          <p>{{ user?.profile?.所属院系 || '未知院系' }} · {{ user?.profile?.班级名称 || '未知班级' }}</p>
        </div>
        
        <div class="user-card-actions">
          <button class="user-card-action-login"
            v-if="dataModel.currentLoginUser !== id"
            @click="loadUser(id)" 
            :disabled="dataModel.currentLoginUser === id"
            :class="{ disabled: dataModel.currentLoginUser === id }"
          >
            <i class="fas fa-sign-in-alt"></i>
            加载
          </button>
          
          <button class="user-card-action-refresh"
            v-if="dataModel.currentLoginUser === id"
            @click="refreshUser" 
            :disabled="dataModel.currentLoginUser !== id"
            :class="{ disabled: dataModel.currentLoginUser !== id }"
          >
            <i class="fas fa-sync"></i>
            刷新
          </button>

          <button class="user-card-action-delete" @click="deleteUser(id, true)">
            <i class="fas" :class="{
              'fas-trash-alt': dataModel.currentLoginUser !== id,
              'fa-arrow-right-from-bracket': dataModel.currentLoginUser === id
            }"></i>
            <span>{{ dataModel.currentLoginUser === id ? "登出" : "删除" }}</span>
          </button>
        </div>
      </div>
      <MDialog :dialog="dialogPwd" title="输入 {{ dataModel.user.学生姓名 }} 的密码"></MDialog>
      <MDialog :dialog="dialogRefreshLicConfirm" title="刷新需要同意最新用户许可协议" confirmText="同意" cancelText="不同意">
        <iframe 
          src="/license-vlast.html" 
          frameborder="0"
          style="width:100%; height:400px"
        ></iframe>
        <p>不同意将无法使用登录功能</p>
      </MDialog>
      <MDialog :dialog="dialogRefreshLoad" title="加载中" :loadCancelable="false"></MDialog>
      <MDialog :dialog="dialogUpdateError" title="更新失败">{{ updateErrorMsg }}</MDialog>
      <MDialog :dialog="dialogLoadUserLoad" title="加载中" :loadCancelable="false"></MDialog>
      <MDialog :dialog="dialogLoadUserSuccess" title="加载完成"></MDialog>
      <MDialog :dialog="dialogLoadUserError" title="加载失败">{{ loadUserErrorMsg }}</MDialog>


      
      <!-- 添加账号卡片 -->
      <div class="user-card add-card" @click="showAddForm = true">
        <div class="no-account" v-if="noUsers">
          <p>暂无账号 前往添加</p>
          <p>↓  ↓  ↓</p>
        </div>
        <div class="add-icon">
          <i class="fas fa-plus"></i>
        </div>
      </div>

      <div class="user-card settings-card" @click="router.push({ name: 'mconfig' })">
        <div class="add-icon">
          <i class="fas fa-cog"></i>
        </div>
      </div>
    </div>

    <!-- 添加账号表单 -->
    <div v-if="showAddForm" class="add-form-mask">
      <div class="add-form">
        <div class="form-header">
          <h3>添加新账号</h3>
          <button @click="cancelAdd">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div class="form-group">
          <label for="username">学号</label>
          <div class="username-input-container">
            <input 
              type="text" 
              id="username" 
              v-model="newUsername" 
              placeholder="请输入学号"
            >
          </div>
        </div>
        
        <div class="form-group">
          <label for="password">密码</label>
          <div class="password-input-container">
            <input 
              :type="showPassword ? 'text' : 'password'" 
              id="password" 
              v-model="newPassword" 
              placeholder="请输入密码"
            >
            <i 
              class="fas toggle-password" 
              :class="showPassword ? 'fa-eye-slash' : 'fa-eye'" 
              @click="showPassword = !showPassword"
            ></i>
          </div>
        </div>

        <div v-if="!agreeLicense" class="form-group">
          <div class="license-input-container">
            <input 
              type="checkbox" 
              id="license" 
              v-model="checkedAgreeLicense"
              class="license-checkbox"
            >
            <label for="license" class="license-label">我已完整阅读并同意<u @click="openLicense">用户许可协议</u></label>
          </div>
        </div>

        
        <button 
          class="submit-btn" 
          @click="startLogin" 
          :disabled="loginInProgress"
        >
          <span v-if="loginInProgress" class="spinner"></span>
          <!-- 直接在按钮上显示状态 -->
          {{ loginInProgress ? (loginInProgressMessage || '登录中...') : '登录' }}
        </button>
        <div v-if="loginError" class="error-message">
          <p v-for="(para, _) in loginError.split('<br>')" class="error-message-line">
            {{ para }}
          </p>
        </div>
      </div>
      
      <MDialog :dialog="dialogLicense" title="许可协议" confirmText="同意" cancelText="不同意">
        <iframe 
          src="/license-vlast.html" 
          frameborder="0"
          style="width:100%; height:400px"
        ></iframe>
        <p>详情见[设置 > 许可协议]</p>
      </MDialog>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import DataModel from '@/models/DataModel'
import { useRouter } from 'vue-router';
import MDialog from '@/components/MDialog.vue';
import createDialog from '@/models/dialogs.js';
const router = useRouter();

// 创建响应式数据模型实例
const dataModel = reactive(DataModel);
const agreeLicense = ref(DataModel.checkoutLicense());
const noUsers = computed(() => {
  return Object.keys(dataModel.allLoginUsers).length === 0;
})

// 添加账号相关状态
const showAddForm = ref(false)
const newUsername = ref('')
const newPassword = ref('')
const loginInProgress = ref(false)
const showPassword = ref(false);

// **切换**加载用户
const dialogLoadUserLoad = createDialog()
const dialogLoadUserSuccess = createDialog()
const dialogLoadUserError = createDialog()
const loadUserErrorMsg = ref('')
async function loadUser(id) {
  dialogLoadUserLoad.load()
  try {
    // 登出当前用户（如果存在）
    if (dataModel.currentLoginUser) {
      await dataModel.logout(true)
    }
    
    // 获取用户信息并**切换**加载
    if (id in dataModel.allLoginUsers) {
      // 切换加载不刷新教务系统状态
      await dataModel.changeToLogin(id, false)
      console.log(dataModel.currentLoginUser)
    } else {
      dialogLoadUserLoad.loadCancel()
      loadUserErrorMsg.value = '不预期的错误：用户实际上不存在于本地，请刷新页面'
      console.error(loadUserErrorMsg.value)
      dialogLoadUserError.alert()
      return
    }
    dialogLoadUserSuccess.alert()
    
  } catch (error) {
    dialogLoadUserLoad.loadCancel()
    console.error('加载失败:', error)
    loadUserErrorMsg.value = `加载失败: ${error.message}\n当前加载的用户: ${dataModel.currentLoginUser || '无用户'}`
    dialogLoadUserError.alert()
  }
  console.log(dataModel.currentLoginUser)
}

// 刷新当前用户数据
const dialogPwd = createDialog()
const dialogUpdateError = createDialog()
const updateErrorMsg = ref('')
const dialogRefreshLoad = createDialog()
const dialogRefreshLicConfirm = createDialog()
async function refreshUser() {
  console.log(`agreeLicense=${agreeLicense.value}`)
  if (!agreeLicense.value) {
    const agree = await dialogRefreshLicConfirm.confirm()
    console.log(`agree=${agree}`)
    if (!agree) {
      return
    }
    agreeLicense.value = true
    DataModel.agreeLicense()
  }
  if (!dataModel.currentLoginUser) return
  const password = await dialogPwd.prompt("请输入密码")

  dialogRefreshLoad.load()
  try {
    
    if (!password) {
      throw new Error("请输入密码")
    }
    await dataModel.updateAll(false, password)
    dataModel.mergeCurrent()
    dataModel.saveAllToLocal()
    dialogRefreshLoad.loadComplete()
  } catch (error) {
    dialogRefreshLoad.loadCancel()
    console.error('刷新失败:', error)
    updateErrorMsg.value = error.message
    dialogUpdateError.alert()
  } finally {
    dialogRefreshLoad.loadCancel()
  }
}

// 删除/登出按钮
async function deleteUser(id) {
  try {
    // 如果点删除按钮的是当前用户，登出
    if (dataModel.currentLoginUser === id) {
      await dataModel.logout(true)
    } else {  // 删除用户
      dataModel.delete(id)
      dataModel.saveAllToLocal()
    }
  } catch (error) {
    console.error('删除失败:', error)
  }
}

// 开始添加账号流程
const loginError = ref('')
const loginInProgressMessage = ref('')

async function startLogin() {
  if (!newUsername.value) {
    loginError.value = "请输入学号"
    return
  }
  if (!newPassword.value) {
    loginError.value = "请输入密码"
    return
  }
  if (!(agreeLicense.value || checkedAgreeLicense.value)) {  // 勾选或历史同意均有效
    loginError.value = "如若不同意许可协议将无法使用教务系统登录功能"  // + `agreeLicense=${agreeLicense.value}, checkedAgreeLicense=${checkedAgreeLicense.value}`
    return
  }

  loginInProgress.value = true
  loginError.value = ''

  try {
    // 使用输入的用户名密码登录
    await dataModel.login(newUsername.value, newPassword.value, false)
    loginInProgressMessage.value = "登录成功！获取数据中"
    console.debug("登录成功！获取数据中")

    // 获取用户完整数据
    await dataModel.updateAll()
    
    // 保存到本地存储
    dataModel.mergeCurrent()
    DataModel.agreeLicense()
    agreeLicense.value = true
    dataModel.saveAllToLocal()

    // 关闭表单
    showAddForm.value = false
    resetFormState()
  } catch (error) {
    // 捕获并显示错误信息
    loginError.value = `登录失败: ${error.message}`
  } finally {
    loginInProgress.value = false
  }
}

// 取消添加表单
function cancelAdd() {
  showAddForm.value = false
  resetFormState()
}

// 重置表单状态
function resetFormState() {
  newUsername.value = ''
  newPassword.value = ''
  loginInProgress.value = false
  loginInProgressMessage.value = ''
}

// 许可协议
const checkedAgreeLicense = ref(false)
const dialogLicense = createDialog()
async function openLicense(event) {
  event.preventDefault()

  const confirmLicenseWindow = dialogLicense.confirm()
  if (await confirmLicenseWindow) {
    checkedAgreeLicense.value = true
  } else {
    checkedAgreeLicense.value = false
  }
}
</script>

<style scoped>

.profile-container {
  padding: 12px;
  max-width: 100vw;
  box-sizing: border-box;
}

.user-grid {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding-bottom: 20px;
}

/* #region 用户卡片 */

.user-card {
  background-color: #fff7f780;
  border-radius: 16px;
  padding: 8px 16px;
  display: flex;
  flex: 1;
  flex-direction: column;
  backdrop-filter: blur(4px);
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.user-card.active {
  border: 2px solid #4a90e2;
}

/* #region 顶部信息 */
.user-card-top {
  display: flex;
  align-items: center;
  justify-content: space-around;
  gap: 12px;
  margin-bottom: 12px;
}

.user-card-text-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 18px;
  flex-shrink: 0;
}

.user-card-icon-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
}

.user-card-icon-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.user-card-ni {
  display: flex;
  flex: 1;
  flex-direction: column;
  padding: 0px 16px;
  border-left: 2px #4a90e2c0 solid;
}

.user-card-name {
  flex: 1;
  font-weight: bold;
  margin: 0;
  box-sizing: border-box;
  font-size: 15px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.user-card-id {
  margin: 0;
  font-size: 12px;
  color: #666;
  opacity: 0.8;
}

.user-card-bottom {
  margin-top: auto;
  font-size: 13px;
  color: #555;
  opacity: 0.9;
  line-height: 1.4;
}

.user-card-bottom p {
  margin: 0;
}
/* #endregion */

/* #region 操作按钮 */
.user-card-actions {
  display: flex;
  margin-top: 14px;
  gap: 6px;
}

.user-card-actions button {
  flex: 1;
  border: none;
  border-radius: 8px;
  padding: 6px 4px;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.user-card-action-login {
  background-color: #4CAF50;
  color: white;
}

.user-card-action-login:disabled {
  background-color: #a5d6a7;
  cursor: not-allowed;
}

.user-card-action-refresh {
  background-color: #2196F3;
  color: white;
}

.user-card-action-refresh:disabled {
  background-color: #90caf9;
  cursor: not-allowed;
}

.user-card-action-delete {
  background-color: #f44336;
  color: white;
}
/* #endregion */

/* #endregion */

/* #region 卡片后面的东西 */
.add-card {
  background: rgba(255, 247, 247, 0.75) !important;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border: 2px dashed #bbb !important;
}

.add-icon {
  font-size: 32px;
  color: #888;
}

.no-account {
  text-align: center;
  padding: 20px;
  color: #666;
  font-size: 20px;
  background-color: #fff7f7c0;
  border-radius: 32px;
  border: 2px #222 solid;
  margin: 20px 0 0;
}

.no-account p {
  margin: 0;
}

.settings-card {
  background-color: #fff7f780;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border: 2px dashed #bbb !important;
}
/* #endregion */

/* #region 新登录表单 */
.add-form-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.add-form {
  width: 80vw;
  max-width: 400px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  overflow: hidden;
  animation: fadeIn 0.3s ease;
  padding: 24px;
}

.form-header {
  padding: 0 0 16px;
  font-size: 18px;
  font-weight: 600;
  color: #333;
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  border-bottom: 1px solid #eee;
  margin-bottom: 20px;
}

.form-header h3 {
  margin: 0;
  text-align: center;
  font-size: 18px;
}

.form-header button {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #666;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  color: #666;
}

.form-group input {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 15px;
  transition: all 0.2s;
}

.form-group input:focus {
  border-color: #1890ff;
  outline: none;
}

.submit-btn {
  width: 100%;
  padding: 14px;
  background-color: #1890ff;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.submit-btn:hover {
  background-color: #40a9ff;
}

.submit-btn:disabled {
  background-color: #d9d9d9;
  cursor: not-allowed;
}

.spinner {
  display: inline-block;
  width: 20px;
  height: 20px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 1s linear infinite;
  margin-right: 10px;
  vertical-align: middle;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* #region 密码 */
.username-input-container,
.password-input-container {

  position: relative;
  display: flex;
}

.password-input-container input {
  width: 100%;
  padding-right: 32px;
}

.toggle-password {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  cursor: pointer;
  color: #aaa;
  font-size: 16px;
}

.toggle-password:hover {
  color: #666;
}
/* #endregion */

/* #region 许可协议 */
/* 许可协议复选框样式 */
.license-input-container {
  display: flex;
  align-items: center;
  margin: 16px 0;
  padding: 0 24px;
}

.license-input-container .license-checkbox {
  /* 隐藏原生复选框 */
  position: absolute;
  opacity: 0;
  width: 1rem;
  height: 1rem;
  margin: 0;
  cursor: pointer;
}

.license-input-container .license-checkbox + .license-label {
  position: relative;
  padding-left: 32px;
  font-size: 15px;
  color: #333;
  cursor: pointer;
  user-select: none;
  line-height: 1.5;
  margin: 0;
}

/* 未选中状态图标 */
.license-input-container .license-checkbox + .license-label::before {
  content: "\f0c8"; /* FontAwesome square图标 */
  font-family: 'Font Awesome 6 Free';
  font-weight: 400;
  position: absolute;
  left: 0;
  top: 0;
  color: #999; /* 灰色未选中状态 */
  font-size: 1.2rem;
  transition: all 0.2s;
}

/* 选中状态图标 */
.license-input-container .license-checkbox:checked + .license-label::before {
  max-height: 100%;
  content: "\f14a"; /* FontAwesome check-square */
  font-weight: 900;
  color: #1890ff;
}

/* 禁用状态 */
.license-input-container .license-checkbox:disabled + .license-label {
  color: #999;
  cursor: not-allowed;
}
/* #endregion */

/* #region 错误信息 */

.error-message {
  margin-top: 16px;
  margin-bottom: 0;
  padding: 12px;
  border-radius: 8px;
  background-color: rgba(244, 67, 54, 0.2);
  color: #c62828;
  font-size: 14px;
  text-align: center;
}

.error-message-line {
  margin: 0;
}
/* #endregion */

/* #endregion */

/* #region 等待窗口 */
.showinfo-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(3px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  transition: opacity 0.3s ease;
}

.showinfo-window {
  position: relative;
  width: 60%;
  max-width: 400px;
  padding: 2.5rem 1.5rem;
  background-color: #fff;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  transform: translateY(0);
  animation: fadeIn 0.1s ease-out;
}

/* .info-icon {
  display: flex;
  align-items: center;
  justify-content: center;
}
*/
.info-icon i{
  font-size: 36px;
} 

.loading-icon {
  animation: spin 1s linear infinite;
}

.info-tip {
  margin: 0;
  color: #2f6dff;
  font-size: 20px;
}

.info-close-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  font-size: 20px;
  color: #666;
  cursor: pointer;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
  0% { transform: rotate(0deg); }
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-5px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* #endregion */

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

</style>