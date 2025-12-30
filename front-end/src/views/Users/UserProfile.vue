<template>
  <div class="container py-5">
    <div v-if="loading" class="loading-overlay">
      <div class="spinner-grow text-primary" role="status"></div>
      <p class="mt-3 fw-bold">در حال بارگذاری اطلاعات...</p>
    </div>

    <div v-else class="profile-card shadow-lg border-0 overflow-hidden">
      <div class="profile-header-bg"></div>

      <div class="card-body p-4 pt-0">
        <div class="text-center avatar-section">
          <div class="avatar-wrapper shadow">
            <i class="bi bi-person-fill text-white"></i>
          </div>
          <h3 class="mt-3 mb-1 fw-bold text-dark">{{ user.username }}</h3>
          <span class="badge rounded-pill bg-soft-primary text-primary px-3">کاربر سیستم</span>
        </div>

        <div class="row g-4 mt-4">
          <div class="col-md-6">
            <div class="info-box">
              <label class="text-muted small">نام و نام خانوادگی</label>
              <p class="mb-0 fw-semibold">{{ user.first_name || '---' }} {{ user.last_name || '---' }}</p>
            </div>
          </div>
          <div class="col-md-6">
            <div class="info-box">
              <label class="text-muted small">پست الکترونیک</label>
              <p class="mb-0 fw-semibold">{{ user.email }}</p>
            </div>
          </div>
          <div class="col-md-6">
            <div class="info-box">
              <label class="text-muted small">شماره تماس</label>
              <p class="mb-0 fw-semibold">{{ user.phone_number || 'ثبت نشده' }}</p>
            </div>
          </div>
          <div class="col-md-6">
            <div class="info-box">
              <label class="text-muted small">وضعیت حساب</label>
              <p class="mb-0 text-success fw-bold">فعال</p>
            </div>
          </div>
        </div>

        <div class="d-flex justify-content-between mt-5">
          <button class="btn btn-outline-secondary px-4 rounded-pill" @click="goBack">
            <i class="bi bi-arrow-right me-1"></i> بازگشت
          </button>
          <button class="btn btn-primary px-4 rounded-pill shadow-sm" @click="updateProfile">
            <i class="bi bi-pencil-square me-1"></i> ویرایش پروفایل
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../api/axios'

const router = useRouter()
const loading = ref(true)
const user = ref({
  username: '',
  first_name: '',
  last_name: '',
  email: '',
  phone_number: ''
})

const fetchProfile = async () => {
  try {
    const res = await api.get('accounts/user-profile/')
    user.value = res.data
  } catch (err) {
    console.error('Error:', err)
  } finally {
    loading.value = false
  }
}

const goBack = () => router.back()

const updateProfile = () => {
  router.push({ name: 'UserProfileUpdate' })
}

onMounted(fetchProfile)
</script>

<style scoped>
/* استایل‌های مدرن */
.profile-card {
  background: #ffffff;
  border-radius: 20px;
  max-width: 800px;
  margin: 0 auto;
  position: relative;
}

.profile-header-bg {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  height: 120px;
  width: 100%;
}

.avatar-section {
  margin-top: -60px;
}

.avatar-wrapper {
  width: 120px;
  height: 120px;
  background: #764ba2;
  border: 5px solid #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
  font-size: 3.5rem;
}

.info-box {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 12px;
  border-right: 4px solid #764ba2; /* خط رنگی در سمت راست (برای RTL) */ transition: 0.3s;
}

.info-box:hover {
  background: #f1f3f5;
  transform: translateY(-2px);
}

.bg-soft-primary {
  background-color: #e0e7ff;
}

.loading-overlay {
  height: 60vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

/* دکمه‌های گرد مدرن */
.rounded-pill {
  border-radius: 50px !important;
}
</style>