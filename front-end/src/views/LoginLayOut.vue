<script setup>
  import { ref } from 'vue'
  import api from '../api/axios'
  import { useRouter } from 'vue-router'
  import { useAuthStore } from '@/stores/auth' 
  
  const router = useRouter()
  const auth = useAuthStore() 
  
  const username = ref('')
  const password = ref('')
  const loading = ref(false)
  const error = ref('')
  
  const login = async () => {
    loading.value = true
    error.value = ''
  
    try {
      const res = await api.post('api/token/', {
        username: username.value,
        password: password.value
      })
  
      // ۱. استخراج دیتا از پاسخ سریالایزر جدید جنگو
      // حالا res.data شامل permissions، is_superuser و ... هست
      const { access, refresh, permissions, ...userInfo } = res.data
  
      // ۲. ذخیره در استور پینیا
      // تمام اطلاعات کاربر (username, email, is_superuser, is_staff) در userInfo هست
      auth.saveLoginData(access, permissions, userInfo)
      
      // ۳. ذخیره ریفرش توکن برای استفاده‌های بعدی
      localStorage.setItem('refresh_token', refresh)
  
      // ۴. هدایت به پنل اصلی
      router.replace({ name: 'MainLayout' })
      
    } catch (err) {
      console.error(err)
      // مدیریت بهتر خطاها
      if (err.response && err.response.status === 401) {
        error.value = 'نام کاربری یا رمز عبور اشتباه است'
      } else {
        error.value = 'خطا در برقراری ارتباط با سرور'
      }
    } finally {
      loading.value = false
    }
  }
</script>

<template>
  <div class="login-wrapper">
    <div class="login-card shadow-lg">
      <div class="text-center mb-4">
        <img src="@/assets/logo.svg" alt="Logo" class="logo mb-3" />
        <h2 class="fw-bold">ورود به پنل</h2>
        <p class="text-muted">خوش آمدید، لطفاً وارد شوید</p>
      </div>

      <form @submit.prevent="login">
        <div class="mb-3">
          <label class="form-label fw-semibold">نام کاربری</label>
          <input
            type="text"
            class="form-control form-control-lg"
            v-model.trim="username"
            placeholder="Username"
            required
          />
        </div>

        <div class="mb-4">
          <label class="form-label fw-semibold">رمز عبور</label>
          <input
            type="password"
            class="form-control form-control-lg"
            v-model="password"
            placeholder="Password"
            required
          />
        </div>

        <button
          type="submit"
          class="btn btn-primary w-100 btn-lg"
          :disabled="loading"
        >
          <span
            v-if="loading"
            class="spinner-border spinner-border-sm me-2"
          ></span>
          {{ loading ? 'در حال پردازش...' : 'ورود به سیستم' }}
        </button>

        <transition name="fade">
          <p class="text-danger text-center mt-3" v-if="error">
            {{ error }}
          </p>
        </transition>
      </form>

      <div class="text-center mt-4">
        <small class="text-muted">© 2026 سیستم مدیریت دارایی آرین</small>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* انیمیشن برای نمایش خطا */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.5s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

/* بقیه استایل‌های قشنگی که خودت نوشتی اینجا بمونه... */
.login-wrapper {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(120deg, #667eea, #764ba2, #4facfe, #00f2fe);
  background-size: 300% 300%;
  animation: gradientBG 8s ease infinite;
}

.login-card {
  width: 100%;
  max-width: 420px;
  padding: 2.5rem;
  border-radius: 1.2rem;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(10px);
}

@keyframes gradientBG {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}
</style>