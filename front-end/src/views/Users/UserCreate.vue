<template>
  <div class="user-create-page container py-5" dir="rtl">
    <div class="d-flex justify-content-between align-items-center mb-4 max-w-800 mx-auto px-2">
      <h3 class="fw-bold text-dark m-0">
        <i class="bi bi-person-plus-fill me-2 text-primary"></i> ایجاد کاربر جدید
      </h3>
      <button class="btn btn-light border rounded-pill px-3 shadow-sm" @click="router.push({ name: 'UsersList' })">
        <i class="bi bi-arrow-right me-1"></i> بازگشت
      </button>
    </div>

    <div class="glass-form-card shadow-lg p-4 p-md-5">
      <form @submit.prevent="createUser">
        
        <div class="row">
          <div class="col-md-6 mb-4">
            <label class="form-label fw-bold small text-secondary">نام کاربری</label>
            <div class="input-group-modern">
              <span class="icon"><i class="bi bi-person"></i></span>
              <input v-model="form.username" type="text" class="form-control-modern" placeholder="نام کاربری" required />
            </div>
          </div>

          <div class="col-md-6 mb-4">
            <label class="form-label fw-bold small text-secondary">ایمیل (اختیاری)</label>
            <div class="input-group-modern">
              <span class="icon"><i class="bi bi-envelope"></i></span>
              <input v-model="form.email" type="email" class="form-control-modern" placeholder="example@mail.com"/>
            </div>
          </div>
        </div>

        <div class="row">
          <div class="col-md-6 mb-4">
            <label class="form-label fw-bold small text-secondary">نام</label>
            <div class="input-group-modern">
              <span class="icon"><i class="bi bi-alphabet"></i></span>
              <input v-model="form.first_name" type="text" class="form-control-modern" placeholder="نام" />
            </div>
          </div>

          <div class="col-md-6 mb-4">
            <label class="form-label fw-bold small text-secondary">نام خانوادگی</label>
            <div class="input-group-modern">
              <span class="icon"><i class="bi bi-alphabet"></i></span>
              <input v-model="form.last_name" type="text" class="form-control-modern" placeholder="نام خانوادگی" />
            </div>
          </div>
        </div>

        <div class="row">
          <div class="col-md-6 mb-4">
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

          <div class="col-md-6 mb-4">
            <label class="form-label fw-bold small text-secondary">رمز عبور</label>
            <div class="input-group-modern">
              <span class="icon"><i class="bi bi-lock"></i></span>
              <input v-model="form.password" type="password" class="form-control-modern" placeholder="حداقل ۶ کاراکتر" required minlength="6" />
            </div>
          </div>
        </div>

        <hr class="my-4 opacity-25">

        <div class="row">
          <div class="col-md-6 mb-4">
            <label class="form-label fw-bold small text-secondary">انتخاب گروه‌ها</label>
            <Multiselect
              v-model="form.groups"
              :options="groupsList"
              label="name"
              track-by="id"
              placeholder="گروه‌ها..."
              :multiple="true"
              :searchable="true"
              class="custom-multiselect"
            />
          </div>

          <div class="col-md-6 mb-4">
            <label class="form-label fw-bold small text-secondary">انتخاب مجوزها</label>
            <Multiselect
              v-model="form.user_permissions"
              :options="permissionsList"
              label="name"
              track-by="id"
              placeholder="مجوزها..."
              :multiple="true"
              :searchable="true"
              class="custom-multiselect"
            />
          </div>
        </div>

        <div class="mt-4">
          <button type="submit" class="btn btn-primary-gradient w-100 py-3 rounded-pill fw-bold shadow-sm" :disabled="loading">
            <span v-if="!loading">
              <i class="bi bi-check-circle-fill me-2"></i> تایید و ایجاد کاربر
            </span>
            <span v-else class="spinner-border spinner-border-sm" role="status"></span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api/axios'
import Multiselect from 'vue-multiselect'
import 'vue-multiselect/dist/vue-multiselect.min.css'
import Swal from 'sweetalert2'

const router = useRouter()
const loading = ref(false)
const groupsList = ref([])
const permissionsList = ref([])

const form = ref({
  username: '',
  email: '',
  first_name: '',
  last_name: '',
  gender: '', // فیلد جدید
  password: '',
  groups: [],
  user_permissions: []
})

const fetchInitialData = async () => {
  try {
    const [groupsRes, permsRes] = await Promise.all([
      api.get('accounts/groups-list/'),
      api.get('accounts/permissions-list/')
    ])
    groupsList.value = groupsRes.data
    permissionsList.value = permsRes.data
  } catch (err) {
    console.error(err)
  }
}

const createUser = async () => {
  loading.value = true
  try {
    // اصلاح داده‌ها قبل از ارسال
    const payload = {
      ...form.value,
      // اگر ایمیل خالی بود null بفرست تا مشکل Unique در دیتابیس حل شود
      email: form.value.email.trim() === '' ? null : form.value.email,
      groups: form.value.groups.map(g => g.id),
      user_permissions: form.value.user_permissions.map(p => p.id)
    }

    await api.post('accounts/user-detail/', payload)
    
    await Swal.fire({
      title: 'موفقیت‌آمیز',
      text: 'کاربر جدید با موفقیت ایجاد شد',
      icon: 'success',
      confirmButtonText: 'تایید'
    })
    
    router.push({ name: 'UsersList' })
  } catch (err) {
    const errorMsg = err.response?.data?.email ? 'این ایمیل قبلاً ثبت شده است' : 'مشکلی در ایجاد کاربر رخ داد';
    Swal.fire('خطا', errorMsg, 'error')
  } finally {
    loading.value = false
  }
}

onMounted(fetchInitialData)
</script>

<style scoped>
.max-w-800 { max-width: 800px; }

.glass-form-card {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(15px);
  border-radius: 24px;
  border: 1px solid rgba(255, 255, 255, 0.5);
  margin: auto;
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
  z-index: 5;
}

.form-control-modern {
  width: 100%;
  padding: 12px 45px 12px 15px;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  background: #f8fafc;
  transition: all 0.3s ease;
}

.select-custom {
  cursor: pointer;
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3e%3cpath fill='none' stroke='%23343a40' stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M2 5l6 6 6-6'/%3e%3c/svg%3e");
  background-repeat: no-repeat;
  background-position: left 0.75rem center;
  background-size: 16px 12px;
}

.form-control-modern:focus {
  outline: none;
  background: white;
  border-color: #0d6efd;
  box-shadow: 0 0 0 4px rgba(13, 110, 253, 0.1);
}

.btn-primary-gradient {
  background: linear-gradient(135deg, #0d6efd 0%, #00d4ff 100%);
  border: none;
  color: white;
  transition: all 0.3s ease;
}

.btn-primary-gradient:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(13, 110, 253, 0.3);
}

/* استایل Multiselect برای سازگاری با تم */
.custom-multiselect :deep(.multiselect__tags) {
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  background: #f8fafc;
  padding: 8px 10px 0 40px;
}

.custom-multiselect :deep(.multiselect__select) {
  left: 1px;
  right: auto;
}
</style>