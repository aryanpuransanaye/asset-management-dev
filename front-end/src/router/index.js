import { createRouter, createWebHistory } from 'vue-router'
import { useAuth } from '@/composables/useAuth' // ۱. ایمپورت کردن سرویس Auth

import MainLayOut from '@/components/MainLayOut.vue'
import LoginLayOut from '@/views/LoginLayOut.vue'
import UsersList from '@/views/Users/UsersList.vue'
import UserDetail from '@/views/Users/UserDetail.vue'
import UserUpdate from '@/views/Users/UserUpdate.vue'
import UserUpdateGroups from '@/views/Users/UserUpdateGroups.vue'
import UserUpdatePermissions from '@/views/Users/UserUpdatePermissions.vue'
import UserProfile from '@/views/Users/UserProfile.vue'
import GroupsList from '@/views/Groups/GroupsList.vue'
import GroupDetail from '@/views/Groups/GroupDetail.vue'
import GroupUpdate from '@/views/Groups/GroupUpdate.vue'
import GroupUpdatePermissions from '@/views/Groups/GroupUpdatePermissions.vue'
import GroupsUpdateUsers from '@/views/Groups/GroupsUpdateUsers.vue'
import GroupCreate from '@/views/Groups/GroupCreate.vue'
import UserCreate from '@/views/Users/UserCreate.vue'
import UserProfileUpdate from '@/views/Users/UserProfileUpdate.vue'
import OrganizationLayOut from '@/views/OrganizationLayOut.vue'


const routes = [

  {
    path: '/home',
    name: 'MainLayout',
    component: MainLayOut,
    meta: { requiresAuth: true },
    children:[
      {
        path:'users-list',
        name: 'UsersList',
        component: UsersList
      },
      {
        path:'user-detail/:user_id',
        name: 'UserDetail',
        component: UserDetail
      },
      {
        path:'user-update/:user_id',
        name: 'UserUpdate',
        component: UserUpdate
      },
      {
        path:'user-groups-update/:user_id',
        name: 'UserGroupsUpdate',
        component: UserUpdateGroups
      },
      {
        path:'user-permissions-update/:user_id',
        name: 'UserPermissionsUpdate',
        component: UserUpdatePermissions
      },
      {
        path:'user-profile',
        name: 'UserProfile',
        component: UserProfile
      },
      {
        path:'user-profile-update',
        name: 'UserProfileUpdate',
        component: UserProfileUpdate
      },
      {
        path:'user-create',
        name: 'UserCreate',
        component: UserCreate
      },



      {
        path:'groups-list',
        name: 'GroupsList',
        component: GroupsList
      },
      {
        path:'group-detail/:group_id',
        name: 'GroupDetail',
        component: GroupDetail
      },
      {
        path:'group-update/:group_id',
        name: 'GroupUpdate',
        component: GroupUpdate
      },
      {
        path:'group-permissions-update/:group_id',
        name: 'GroupPermissionsUpdate',
        component: GroupUpdatePermissions
      },
      {
        path:'group-users-update/:group_id',
        name: 'GroupUsersUpdate',
        component: GroupsUpdateUsers
      },
      {
        path:'group-create',
        name: 'GroupCreate',
        component: GroupCreate
      },
    ]
  },


  {
    path:'/login',
    name:'Login',
    component: LoginLayOut,
    meta: { requiresGuest: true }
  },
  {
    path:'/organization',
    name:'Organization',
    component: OrganizationLayOut,
    meta: { requiresGuest: true }
  },
  
]


const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access_token')

  if (to.meta.requiresAuth && !token) {
    next({ name: 'Login' })
  } else if (to.name === 'Login' && token) {
    next({ name: 'MainLayout' })
  } else {
    next()
  }
})

export default router
