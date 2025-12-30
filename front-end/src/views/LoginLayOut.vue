<template>
  <div class="login-wrapper">
    <div class="login-card shadow-lg">
      <div class="text-center mb-4">
        <img src="./assets/logo.svg" alt="Logo" class="logo mb-3" />
        <h2 class="fw-bold">ورود به پنل</h2>
        <p class="text-muted">نام کاربری و رمز عبور خود را وارد کنید</p>
      </div>

      <form @submit.prevent="login">
        <div class="mb-3">
          <label class="form-label fw-semibold">نام کاربری</label>
          <input
            type="text"
            class="form-control form-control-lg"
            v-model="username"
            placeholder="نام کاربری"
            required
          />
        </div>

        <div class="mb-4">
          <label class="form-label fw-semibold">رمز عبور</label>
          <input
            type="password"
            class="form-control form-control-lg"
            v-model="password"
            placeholder="رمز عبور"
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
          {{ loading ? 'در حال ورود...' : 'ورود' }}
        </button>

        <p class="text-danger text-center mt-3" v-if="error">
          {{ error }}
        </p>
      </form>

      <div class="text-center mt-4">
        <small class="text-muted">© 2025 سیستم مدیریت پنل</small>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '../api/axios'
import { useRouter } from 'vue-router'

const router = useRouter()
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

    localStorage.setItem('access_token', res.data.access)
    localStorage.setItem('refresh_token', res.data.refresh)

    router.replace({ name: 'MainLayout' })
  } catch (err) {
    error.value = 'نام کاربری یا رمز عبور اشتباه است'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* 🌈 Background */
.login-wrapper {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(
    120deg,
    #667eea,
    #764ba2,
    #4facfe,
    #00f2fe
  );
  background-size: 300% 300%;
  animation: gradientBG 8s ease infinite;
}

/* 💎 Card */
.login-card {
  width: 100%;
  max-width: 420px;
  padding: 2.5rem;
  border-radius: 1.2rem;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(10px);
}

/* 🔵 Inputs */
.form-control {
  border-radius: 0.75rem;
  transition: all 0.3s ease;
}

.form-control:focus {
  border-color: #4a90e2;
  box-shadow: 0 0 0 0.15rem rgba(74, 144, 226, 0.25);
}

/* 🔘 Button */
.btn-primary {
  border-radius: 0.75rem;
  background: linear-gradient(90deg, #4a90e2, #357abd);
  border: none;
}

.btn-primary:hover {
  background: linear-gradient(90deg, #357abd, #4a90e2);
}

/* 🌀 Animation */
@keyframes gradientBG {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

/* 🖼 Logo */
.logo {
  width: 80px;
  height: 80px;
}
</style>
