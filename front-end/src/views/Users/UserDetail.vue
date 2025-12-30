<template>
  <div class="user-detail-page container py-5" dir="rtl">
    <div class="d-flex justify-content-between align-items-center mb-4 max-w-800 mx-auto px-2">
      <h3 class="fw-bold text-dark m-0">
        <i class="bi bi-person-lines-fill me-2 text-primary"></i> شناسنامه کاربر
      </h3>
      <button class="btn btn-light border rounded-pill px-3 shadow-sm" @click="$router.back()">
        <i class="bi bi-arrow-right me-1"></i> بازگشت
      </button>
    </div>

    <div class="glass-profile-card shadow-lg mx-auto overflow-hidden">
      <div class="profile-header-bg"></div>
      
      <div class="p-4 p-md-5 position-relative">
        <div class="text-center mb-5 mt-n5">
          <div class="avatar-large shadow-lg mx-auto mb-3">
            {{ user.username ? user.username.charAt(0).toUpperCase() : '?' }}
          </div>
          <h4 class="fw-bold mb-1 text-dark">{{ user.first_name }} {{ user.last_name }}</h4>
          <span class="badge bg-soft-primary text-primary px-3 py-2 rounded-pill fw-bold">
            @{{ user.username }}
          </span>
        </div>

        <div class="info-grid">
          <div class="info-item">
            <div class="info-icon"><i class="bi bi-envelope-at-fill"></i></div>
            <div class="info-content">
              <label>پست الکترونیک</label>
              <div>{{ user.email }}</div>
            </div>
          </div>

          <div class="info-item">
            <div class="info-icon"><i class="bi bi-telephone-fill"></i></div>
            <div class="info-content">
              <label>شماره تماس</label>
              <div>{{ user.phone_number || 'ثبت نشده' }}</div>
            </div>
          </div>

          <div class="info-item full-width mt-3">
            <div class="info-icon bg-soft-success text-success">
              <i class="bi bi-collection-fill"></i>
            </div>
            <div class="info-content w-100">
              <label class="mb-2 text-success fw-bold">گروه‌های کاربری</label>
              <div class="d-flex flex-wrap gap-2">
                <span v-for="group in user.groups" :key="group.id" class="modern-badge group-badge">
                  <i class="bi bi-people-fill me-1"></i> {{ group.name }}
                </span>
                <span v-if="!user.groups?.length" class="text-muted small italic">این کاربر عضو هیچ گروهی نیست.</span>
              </div>
            </div>
          </div>

          <div class="info-item full-width mt-3">
            <div class="info-icon bg-soft-warning text-warning-dark">
              <i class="bi bi-shield-lock-fill"></i>
            </div>
            <div class="info-content w-100">
              <label class="mb-2 text-warning-dark fw-bold">مجوزهای دسترسی مستقیم</label>
              <div class="d-flex flex-wrap gap-2">
                <span v-for="perm in user.user_permissions" :key="perm.id" class="modern-badge perm-badge">
                  <i class="bi bi-key-fill me-1"></i> {{ perm.name }}
                </span>
                <span v-if="!user.user_permissions?.length" class="text-muted small italic">مجوز اختصاصی برای این کاربر ثبت نشده است.</span>
              </div>
            </div>
          </div>
        </div>

        <div class="mt-5 pt-4 border-top text-center">
          <button class="btn btn-primary-gradient rounded-pill px-5 py-2 shadow" @click="editUser">
            <i class="bi bi-pencil-square me-2"></i> ویرایش پروفایل کاربر
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/api/axios'

const route = useRoute()
const router = useRouter()
const user = ref({})
const userId = route.params.user_id

const fetchUser = async () => {
  try {
    const response = await api.get(`accounts/user-detail/${userId}/`)
    user.value = response.data
  } catch (err) {
    console.error('Error fetching user:', err)
  }
}

const editUser = () => {
  router.push({ name: 'UserUpdate', params: { user_id: userId } })
}

onMounted(fetchUser)
</script>

<style scoped>
.max-w-800 { max-width: 800px; }

/* کارت شیشه‌ای پروفایل */
.glass-profile-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(15px);
  border-radius: 30px;
  border: 1px solid rgba(255, 255, 255, 0.4);
  max-width: 800px;
  position: relative;
}

.profile-header-bg {
  height: 120px;
  background: linear-gradient(135deg, #0d6efd 0%, #6610f2 100%);
  opacity: 0.9;
}

/* آواتار */
.avatar-large {
  width: 100px;
  height: 100px;
  background: white;
  color: #0d6efd;
  border-radius: 25px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2.5rem;
  font-weight: 900;
  margin-top: -50px;
  border: 5px solid white;
}

/* گرید اطلاعات */
.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 25px;
}

.info-item {
  display: flex;
  align-items: flex-start;
  gap: 15px;
}

.info-item.full-width { grid-column: span 2; }

.info-icon {
  width: 44px;
  height: 44px;
  background: #f0f7ff;
  color: #0d6efd;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  flex-shrink: 0;
}

.info-content label {
  display: block;
  font-size: 0.75rem;
  font-weight: 800;
  color: #94a3b8;
  text-transform: uppercase;
  margin-bottom: 4px;
}

.info-content div {
  font-weight: 600;
  color: #334155;
}

/* استایل نشان‌ها (Badges) */
.modern-badge {
  padding: 8px 16px;
  border-radius: 10px;
  font-size: 0.85rem;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  border: 1px solid transparent;
}

.group-badge {
  background-color: #ecfdf5;
  color: #059669;
  border-color: #d1fae5;
}

.perm-badge {
  background-color: #fffbeb;
  color: #b45309;
  border-color: #fef3c7;
}

/* رنگ‌های کمکی */
.bg-soft-primary { background-color: #e0f2fe; }
.bg-soft-success { background-color: #ecfdf5; }
.bg-soft-warning { background-color: #fffbeb; }
.text-warning-dark { color: #b45309; }

/* دکمه با گرادینت */
.btn-primary-gradient {
  background: linear-gradient(135deg, #0d6efd 0%, #00d4ff 100%);
  border: none;
  color: white;
  transition: all 0.3s ease;
}

.btn-primary-gradient:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(13, 110, 253, 0.2);
}

.italic { font-style: italic; opacity: 0.6; }

/* ریسپانسیو */
@media (max-width: 768px) {
  .info-grid { grid-template-columns: 1fr; }
  .info-item.full-width { grid-column: span 1; }
}
</style>