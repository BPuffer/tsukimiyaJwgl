import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  // #region: 电脑端
  {
    path: '/',
    name: 'home',
    component: () => import('@/views/desktop/Home.vue'),
    meta: { title: '首页' }
  },
  {
    path: '/profile',
    name: 'profile',
    component: () => import('@/views/desktop/Profile.vue'),
    meta: { title: '我的' }
  },
  {
    path: '/schedule',
    name: 'schedule',
    component: () => import('@/views/desktop/Schedule.vue'),
    meta: { title: '课程表' }
  },
  {
    path: '/exams',
    name: 'exams',
    component: () => import('@/views/desktop/Exams.vue'),
    meta: { title: '考试安排' }
  },
  {
    path: '/scores',
    name: 'scores',
    component: () => import('@/views/desktop/Scores.vue'),
    meta: { title: '考试成绩' }
  },
  {
    path: '/second-class',
    name: 'second-class',
    component: () => import('@/views/desktop/SecondClass.vue'),
    meta: { title: '第二课堂' }
  },
  {
    path: '/campus-query',
    name: 'campus-query',
    component: () => import('@/views/desktop/CampusQuery.vue'),
    meta: { title: '校园查询' }
  },
  {
    path: '/bonus',
    name: 'bonus',
    component: () => import('@/views/desktop/Bonus.vue'),
    meta: { title: '我要加分' }
  },
  // #endregion

  // #region: 移动端
  {
    path: '/m',
    name: 'm',
    component: () => import('@/views/mobile/MHome.vue'),
    meta: { title: '移动端首页' }
  },
  {
    path: '/m/profile',
    name: 'mprofile',
    component: () => import('@/views/mobile/MProfile.vue'),
    meta: { title: '我的' }
  },
  {
    path: '/m/schedule',
    name: 'mschedule',
    component: () => import('@/views/mobile/MSchedule.vue'),
    meta: { title: '课程表' }
  },
  {
    path: '/m/exams',
    name: 'mexams',
    component: () => import('@/views/mobile/MExams.vue'),
    meta: { title: '考试安排' }
  },
  {
    path: '/m/bonus',
    name: 'mbonus',
    component: () => import('@/views/mobile/MBonus.vue'),
    meta: { title: '我要加分' }
  },
  {
    path: '/m/config',
    name: 'mconfig',
    component: () => import('@/views/mobile/MConfig.vue'),
    meta: { title: '设置' }
  },
  {
    path: '/m/sherbet-lemon',
    name: 'madmin',
    component: () => import('@/views/mobile/MAdmin.vue'),
    meta: { title: '管理员' }
  },

  // #endregion

  // 404 页面
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('@/views/NotFound.vue'),
    meta: { title: '页面未找到' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.afterEach((to) => {
  document.title = `${to.meta.title} | 教务系统`
})

export default router