<template>
  <div class="dashboard-layout d-flex flex-column vh-100" dir="rtl">
    <nav class="navbar navbar-expand-lg navbar-dark glass-navbar shadow-sm z-index-top">
      <div class="container-fluid d-flex justify-content-between align-items-center px-4">
        <router-link class="navbar-brand fw-bold d-flex align-items-center" :to="{ name: 'MainLayout' }">
          <div class="logo-box me-2">
            <i class="bi bi-shield-lock-fill"></i>
          </div>
          <span class="brand-text text-white">مدیریت دارایی‌ها</span>
        </router-link>

        <div class="position-relative overflow-visible" ref="dropdownRef">
          <div class="user-profile-trigger d-flex align-items-center" @click="toggleUserDropdown">
            <div class="avatar-circle">
              {{ user.username.charAt(0).toUpperCase() }}
            </div>
            <div class="user-info-text d-none d-md-block">
              <span class="username text-white fw-bold">{{ user.username }}</span>
            </div>
            <i :class="userDropdownOpen ? 'bi bi-chevron-up ms-2' : 'bi bi-chevron-down ms-2'" class="small text-white"></i>
          </div>

          <transition name="fade">
            <div v-if="userDropdownOpen" class="dropdown-menu-modern shadow-lg">
              <div class="dropdown-header-custom p-3 border-bottom bg-light text-dark">
                <p class="m-0 small text-muted">خوش آمدید،</p>
                <p class="m-0 fw-bold">{{ user.username }}</p>
              </div>
              <a class="dropdown-item py-2 fw-bold" @click="goToProfile">
                <i class="bi bi-person me-2 text-primary"></i> پروفایل کاربری
              </a>
              <div class="dropdown-divider m-0"></div>
              <a class="dropdown-item text-danger py-2 fw-bold" @click="logout">
                <i class="bi bi-box-arrow-right me-2"></i> خروج از حساب
              </a>
            </div>
          </transition>
        </div>
      </div>
    </nav>

    <div class="d-flex flex-grow-1 overflow-hidden">
      <aside class="glass-sidebar text-white p-3 sidebar-fixed">
        <div class="sidebar-section-label mb-3 fw-bold">منوی اصلی</div>
        
        <ul class="nav flex-column gap-2">
          <li class="nav-item">
            <div 
              class="nav-link-custom d-flex justify-content-between align-items-center" 
              @click="toggleUserMenu"
            >
              <span class="fw-bold"><i class="bi bi-people-fill me-2 icon-gradient"></i> مدیریت کاربران</span>
              <i :class="userMenuOpen ? 'bi bi-chevron-up' : 'bi bi-chevron-down'" class="small"></i>
            </div>
            
            <transition name="slide-fade">
              <ul v-show="userMenuOpen" class="nav flex-column ms-3 mt-1 submenu-list">
                <li class="nav-item">
                  <router-link class="nav-link submenu-link" :to="{ name: 'UsersList' }">
                    <i class="bi bi-dot me-1"></i> لیست کاربران
                  </router-link>
                </li>
                <li class="nav-item">
                  <router-link class="nav-link submenu-link" :to="{ name: 'GroupsList' }">
                    <i class="bi bi-dot me-1"></i> گروه‌های کاربری
                  </router-link>
                </li>
              </ul>
            </transition>
          </li>

          <li class="nav-item">
            <div 
              class="nav-link-custom d-flex justify-content-between align-items-center" 
              @click="toggleAssetsMenu"
            >
              <span class="fw-bold"><i class="bi bi-box-seam-fill me-2 icon-gradient"></i> مدیریت دارایی‌ها</span>
              <i :class="assetsMenuOpen ? 'bi bi-chevron-up' : 'bi bi-chevron-down'" class="small"></i>
            </div>
            
            <transition name="slide-fade">
              <ul v-show="assetsMenuOpen" class="nav flex-column ms-3 mt-1 submenu-list">
                <li class="nav-item">
                  <router-link 
                    class="nav-link submenu-link"
                    :to="{ name: 'DataInformationList', query: { api: 'asset/data-and-information' } }"
                  >
                    <i class="bi bi-dot me-1"></i> داده و اطلاعات
                  </router-link>
                </li>

                <li class="nav-item">
                  <router-link 
                    class="nav-link submenu-link"
                    :to="{ name: 'DataInformationList', query: { api: 'asset/hardware' } }"
                  >
                    <i class="bi bi-dot me-1"></i> سخت‌افزار
                  </router-link>
                </li>
              </ul>
            </transition>
          </li>
          
          <li class="nav-item">
            <router-link class="nav-link-custom fw-bold" to="/reports">
              <i class="bi bi-pie-chart-fill me-2 icon-gradient"></i> گزارشات تحلیلی
            </router-link>
          </li>
        </ul>

        <div class="sidebar-footer mt-auto p-3 text-center opacity-75 small">
          نسخه ۱.۰.۲
        </div>
      </aside>

      <main class="flex-grow-1 p-4 overflow-auto content-area">
        <div class="content-wrapper">
          <router-view v-slot="{ Component }">
            <transition name="page-fade" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api/axios'

const router = useRouter()
const userMenuOpen = ref(false)
const assetsMenuOpen = ref(true) // به صورت پیش‌فرض باز باشد
const userDropdownOpen = ref(false)
const dropdownRef = ref(null)
const user = ref({ username: 'کاربر' })

const toggleUserMenu = () => { userMenuOpen.value = !userMenuOpen.value }
const toggleAssetsMenu = () => { assetsMenuOpen.value = !assetsMenuOpen.value }
const toggleUserDropdown = () => { userDropdownOpen.value = !userDropdownOpen.value }

const fetchUser = async () => {
  try {
    const res = await api.get('accounts/user-profile/')
    user.value = res.data
  } catch (err) { console.error(err) }
}

const logout = async () => {
  try {
    const refreshToken = localStorage.getItem('refresh_token')
    if (refreshToken) await api.post('accounts/logout/', { refresh_token: refreshToken })
  } finally {
    localStorage.clear()
    router.push({ name: 'Login' })
  }
}

const goToProfile = () => { userDropdownOpen.value = false; router.push({ name: 'UserProfile' }) }

const handleClickOutside = (e) => {
  if (dropdownRef.value && !dropdownRef.value.contains(e.target)) userDropdownOpen.value = false
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  fetchUser()
})
onUnmounted(() => document.removeEventListener('click', handleClickOutside))
</script>

<style scoped>
/* پس‌زمینه متحرک */
.dashboard-layout {
  background: linear-gradient(-45deg, #f3f4f6, #e5e7eb, #d1d5db, #f3f4f6);
  background-size: 400% 400%;
  animation: gradientBG 15s ease infinite;
}

@keyframes gradientBG {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

/* Navbar */
.z-index-top { z-index: 1050 !important; }
.glass-navbar {
  background: rgba(25, 28, 31, 0.98) !important;
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  height: 70px;
}
.logo-box {
  width: 35px; height: 35px;
  background: linear-gradient(135deg, #0d6efd, #00d4ff);
  border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  color: white;
}

/* Sidebar */
.glass-sidebar {
  width: 260px;
  background: rgba(25, 28, 31, 0.98);
  backdrop-filter: blur(15px);
  border-left: 1px solid rgba(255, 255, 255, 0.05);
  display: flex;
  flex-direction: column;
  z-index: 1000;
}

.sidebar-section-label {
  font-size: 0.75rem;
  text-transform: uppercase;
  color: #0dcaf0;
  letter-spacing: 1px;
}

/* Nav Links */
.nav-link-custom {
  color: #ffffff !important;
  padding: 12px 15px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s;
  text-decoration: none;
  display: flex;
  align-items: center;
}

.nav-link-custom:hover { background: rgba(255, 255, 255, 0.05); }

.router-link-active {
  color: #0dcaf0 !important;
  background: rgba(13, 202, 240, 0.1) !important;
}

.submenu-link {
  color: rgba(255, 255, 255, 0.85) !important;
  font-size: 0.9rem;
  padding: 10px 15px;
  text-decoration: none;
  display: flex;
  align-items: center;
  border-radius: 8px;
  margin-bottom: 2px;
}

.submenu-link:hover, .submenu-link.router-link-active {
  color: #0dcaf0 !important;
  background: rgba(255, 255, 255, 0.03);
}

.icon-gradient { color: #0dcaf0; }

/* Profile Avatar & Dropdown */
.user-profile-trigger {
  cursor: pointer;
  padding: 5px 12px;
  border-radius: 50px;
  background: rgba(255, 255, 255, 0.1);
}

.avatar-circle {
  width: 32px; height: 32px;
  background: #0d6efd;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-weight: bold; font-size: 0.8rem;
  color: white;
  margin-left: 10px;
}

.dropdown-menu-modern {
  position: absolute;
  top: 110%; left: 0;
  background: #ffffff;
  border-radius: 12px;
  min-width: 200px;
  z-index: 9999 !important;
  border: 1px solid rgba(0,0,0,0.1);
  overflow: visible;
}

.dropdown-item {
  font-size: 0.85rem;
  color: #212529 !important;
  padding: 10px 15px;
  cursor: pointer;
}

.dropdown-item:hover { background-color: #f8fafc; color: #0d6efd !important; }

/* Animations */
.slide-fade-enter-active, .slide-fade-leave-active { transition: all 0.3s ease; }
.slide-fade-enter-from, .slide-fade-leave-to { opacity: 0; transform: translateY(-10px); }
.page-fade-enter-active, .page-fade-leave-active { transition: opacity 0.3s ease; }
.page-fade-enter-from, .page-fade-leave-to { opacity: 0; }
</style>