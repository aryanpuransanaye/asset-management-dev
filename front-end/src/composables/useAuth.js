import { ref } from 'vue'
import api from '../api/axios'

// این متغیرها بیرون از تابع می‌مانند تا در کل برنامه یکسان باشند
const isAuthenticated = ref(false)
const user = ref({})
const isAuthLoading = ref(true)

export function useAuth() {
  
  const checkAuth = async () => {
    const token = localStorage.getItem('access_token')
    
    // ۱. اگر توکن اصلاً وجود ندارد، بی‌دلیل تلاش نکن و لودینگ را ببند
    if (!token) {
      isAuthenticated.value = false
      isAuthLoading.value = false
      return
    }

    try {
      // ۲. قبل از درخواست، وضعیت لودینگ را مطمئن شو که true است
      isAuthLoading.value = true
      
      const res = await api.get('accounts/profile/')
      
      user.value = res.data
      isAuthenticated.value = true
    } catch (error) {
      console.error("Auth error details:", error.response || error)
      
      // ۳. خیلی مهم: فقط اگر سرور صراحتاً گفت توکن نامعتبر است (401 یا 403) پاکش کن
      // اگر مشکل شبکه یا خطای 500 بود، توکن را پاک نکن تا کاربر نپرد بیرون
      if (error.response && (error.response.status === 401 || error.response.status === 403)) {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        isAuthenticated.value = false
      }
    } finally {
      // ۴. در نهایت لودینگ را متوقف کن
      isAuthLoading.value = false
    }
  }

  return { isAuthenticated, user, checkAuth, isAuthLoading }
}