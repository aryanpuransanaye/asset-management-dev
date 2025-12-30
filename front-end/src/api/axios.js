import axios from 'axios'

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/'
})

// استفاده از interceptors تضمین می‌کند که توکنِ موجود در localStorage 
// دقیقاً قبل از شلیکِ درخواست خوانده شود
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      // دقت کن که کلمه Bearer و فاصله بعد از آن درست باشد
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

export default api