<template>
    <div class="profile-update-page container py-5" dir="rtl">
      <div class="max-w-700 mx-auto">
        <div class="d-flex align-items-center mb-4 px-2">
          <div class="profile-avatar-main me-3">
            {{ form.username ? form.username.charAt(0).toUpperCase() : 'U' }}
          </div>
          <div>
            <h3 class="fw-bold text-dark m-0">تنظیمات حساب کاربری</h3>
            <p class="text-muted small m-0">اطلاعات شخصی خود را مدیریت کنید</p>
          </div>
        </div>
  
        <div class="glass-card shadow-lg p-4 p-md-5">
          <form @submit.prevent="updateProfile">
            
            <div class="row">
              <div class="col-md-12 mb-4">
                <label class="form-label fw-bold small text-secondary">نام کاربری (غیرقابل تغییر)</label>
                <div class="input-group-modern disabled">
                  <span class="icon"><i class="bi bi-person-lock"></i></span>
                  <input v-model="form.username" type="text" class="form-control-modern" disabled />
                </div>
              </div>
  
              <div class="col-md-6 mb-4">
                <label class="form-label fw-bold small text-secondary">نام</label>
                <div class="input-group-modern">
                  <span class="icon"><i class="bi bi-person"></i></span>
                  <input v-model="form.first_name" type="text" class="form-control-modern" placeholder="نام شما" />
                </div>
              </div>
  
              <div class="col-md-6 mb-4">
                <label class="form-label fw-bold small text-secondary">نام خانوادگی</label>
                <div class="input-group-modern">
                  <span class="icon"><i class="bi bi-person"></i></span>
                  <input v-model="form.last_name" type="text" class="form-control-modern" placeholder="نام خانوادگی شما" />
                </div>
              </div>
  
              <div class="col-md-6 mb-4">
                <label class="form-label fw-bold small text-secondary">ایمیل</label>
                <div class="input-group-modern">
                  <span class="icon"><i class="bi bi-envelope"></i></span>
                  <input v-model="form.email" type="email" class="form-control-modern" placeholder="example@mail.com" />
                </div>
              </div>
  
              <div class="col-md-6 mb-4">
                <label class="form-label fw-bold small text-secondary">شماره تماس</label>
                <div class="input-group-modern">
                  <span class="icon"><i class="bi bi-telephone"></i></span>
                  <input v-model="form.phone_number" type="text" class="form-control-modern" placeholder="0912..." />
                </div>
              </div>
  
              <div class="col-md-12 mb-4">
                <label class="form-label fw-bold small text-secondary">جنسیت</label>
                <div class="input-group-modern">
                  <span class="icon"><i class="bi bi-gender-ambiguous"></i></span>
                  <select v-model="form.gender" class="form-control-modern select-custom">
                    <option value="" disabled>انتخاب جنسیت...</option>
                    <option value="male">مرد</option>
                    <option value="female">زن</option>
                    <option value="other">سایر</option>
                  </select>
                </div>
              </div>
            </div>
  
            <div class="mt-4">
              <button type="submit" class="btn btn-primary-gradient w-100 py-3 rounded-pill fw-bold shadow-sm" :disabled="saving">
                <span v-if="!saving">
                  <i class="bi bi-cloud-arrow-up-fill me-2"></i> ذخیره تغییرات پروفایل
                </span>
                <span v-else class="spinner-border spinner-border-sm" role="status"></span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue'
  import api from '@/api/axios'
  import Swal from 'sweetalert2'
  
  const saving = ref(false)
  const form = ref({
    username: '',
    first_name: '',
    last_name: '',
    email: '',
    phone_number: '',
    gender: ''
  })
  
  // دریافت اطلاعات فعلی کاربر لاگین شده
  const fetchProfile = async () => {
    try {
      const res = await api.get('accounts/user-profile/') // آدرس API پروفایل خودت را چک کن
      form.value = res.data
    } catch (err) {
      console.error("خطا در دریافت پروفایل:", err)
    }
  }
  
  const updateProfile = async () => {
    saving.value = true
    try {
      // ارسال داده‌ها به متد PUT که نوشتی
      const payload = {
        ...form.value,
        email: form.value.email?.trim() === '' ? null : form.value.email
      }
      
      await api.patch('accounts/user-profile/', payload) // آدرس متد PUT خودت
    
      Swal.fire({
          title: 'بروزرسانی موفق',
          text: 'اطلاعات پروفایل شما با موفقیت تغییر کرد',
          icon: 'success',
          confirmButtonText: 'عالیه'
        })
    } catch (err) {
        const errorMsg = err.response?.data?.email ? 'این ایمیل تکراری است' : 'مشکلی در بروزرسانی رخ داد'
        Swal.fire('خطا', errorMsg, 'error')
    } finally {
        saving.value = false
    }
}

  onMounted(fetchProfile)
  </script>
  
  <style scoped>
  .max-w-700 { max-width: 700px; }
  
  .glass-card {
    background: rgba(255, 255, 255, 0.9);
    backdrop-filter: blur(15px);
    border-radius: 24px;
    border: 1px solid rgba(255, 255, 255, 0.5);
  }
  
  .profile-avatar-main {
    width: 65px;
    height: 65px;
    background: linear-gradient(135deg, #0d6efd 0%, #00d4ff 100%);
    color: white;
    border-radius: 18px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.8rem;
    font-weight: bold;
    box-shadow: 0 8px 20px rgba(13, 110, 253, 0.2);
  }
  
  .input-group-modern {
    position: relative;
    display: flex;
    align-items: center;
  }
  
  .input-group-modern .icon {
    position: absolute;
    right: 15px;
    color: #0d6efd;
    font-size: 1.1rem;
    pointer-events: none;
  }
  
  .form-control-modern {
    width: 100%;
    padding: 12px 45px 12px 15px;
    border-radius: 12px;
    border: 1px solid #e2e8f0;
    background: #f8fafc;
    transition: all 0.3s ease;
  }
  
  .input-group-modern.disabled .form-control-modern {
    background: #e9ecef;
    color: #6c757d;
    cursor: not-allowed;
  }
  
  .select-custom {
    cursor: pointer;
    appearance: none;
    background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3e%3cpath fill='none' stroke='%23343a40' stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M2 5l6 6 6-6'/%3e%3c/svg%3e");
    background-repeat: no-repeat;
    background-position: left 0.75rem center;
    background-size: 16px 12px;
  }
  
  .btn-primary-gradient {
    background: linear-gradient(135deg, #0d6efd 0%, #00d4ff 100%);
    border: none;
    color: white;
    transition: all 0.3s ease;
  }
  
  .btn-primary-gradient:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(13, 110, 253, 0.3);
  }
  </style>