<template>
  <div class="user-update-page container py-5" dir="rtl">
    <div class="d-flex justify-content-between align-items-center mb-4 max-w-900 mx-auto px-2">
      <h3 class="fw-bold text-dark m-0">
        <i class="bi bi-person-gear me-2 text-primary"></i> ویرایش و مدیریت کاربر
      </h3>
      <button class="btn btn-light border rounded-pill px-3 shadow-sm" @click="cancelEdit">
        <i class="bi bi-arrow-right me-1"></i> بازگشت
      </button>
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status"></div>
      <p class="mt-2 text-muted">در حال فراخوانی اطلاعات...</p>
    </div>

    <div v-else class="max-w-900 mx-auto">
      <div class="glass-card shadow-lg p-4 p-md-5 mb-4">
        <h5 class="fw-bold mb-4 text-primary border-bottom pb-2">
          <i class="bi bi-info-circle me-2"></i> اطلاعات اصلی
        </h5>
        
        <form @submit.prevent="updateUser">
          <div class="row">
            <div class="col-md-6 mb-4">
              <label class="form-label fw-bold small text-secondary">نام کاربری</label>
              <div class="input-group-modern">
                <span class="icon"><i class="bi bi-person"></i></span>
                <input v-model="user.username" type="text" class="form-control-modern" required />
              </div>
            </div>

            <div class="col-md-6 mb-4">
              <label class="form-label fw-bold small text-secondary">ایمیل (اختیاری)</label>
              <div class="input-group-modern">
                <span class="icon"><i class="bi bi-envelope"></i></span>
                <input v-model="user.email" type="email" class="form-control-modern" />
              </div>
            </div>

            <div class="col-md-6 mb-4">
              <label class="form-label fw-bold small text-secondary">نام</label>
              <div class="input-group-modern">
                <span class="icon"><i class="bi bi-type"></i></span>
                <input v-model="user.first_name" type="text" class="form-control-modern" />
              </div>
            </div>

            <div class="col-md-6 mb-4">
              <label class="form-label fw-bold small text-secondary">نام خانوادگی</label>
              <div class="input-group-modern">
                <span class="icon"><i class="bi bi-type"></i></span>
                <input v-model="user.last_name" type="text" class="form-control-modern" />
              </div>
            </div>

            <div class="col-md-6 mb-4">
              <label class="form-label fw-bold small text-secondary">جنسیت</label>
              <div class="input-group-modern">
                <span class="icon"><i class="bi bi-gender-ambiguous"></i></span>
                <select v-model="user.gender" class="form-control-modern select-custom">
                  <option value="" disabled>انتخاب جنسیت...</option>
                  <option value="male">مرد</option>
                  <option value="female">زن</option>
                  <option value="other">سایر</option>
                </select>
              </div>
            </div>

            <div class="col-md-6 mb-4">
              <label class="form-label fw-bold small text-secondary">شماره تماس</label>
              <div class="input-group-modern">
                <span class="icon"><i class="bi bi-phone"></i></span>
                <input v-model="user.phone_number" type="text" class="form-control-modern" />
              </div>
            </div>
          </div>

          <div class="d-flex gap-2 mt-2">
            <button type="submit" class="btn btn-primary-gradient rounded-pill px-4 shadow-sm">
              <i class="bi bi-cloud-check me-1"></i> ذخیره تغییرات اصلی
            </button>
            <button type="button" class="btn btn-outline-secondary rounded-pill px-4" @click="cancelEdit">
              لغو
            </button>
          </div>
        </form>
      </div>

      <div class="row g-4">
        <div class="col-md-6">
          <div class="glass-card shadow-sm p-4 h-100">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <h6 class="fw-bold m-0"><i class="bi bi-people text-success me-2"></i> عضویت در گروه‌ها</h6>
              <button class="btn btn-sm btn-soft-success rounded-circle" @click="goEditGroups" title="ویرایش گروه‌ها">
                <i class="bi bi-pencil"></i>
              </button>
            </div>
            <div class="d-flex flex-wrap gap-2">
              <span v-for="g in user.groups" :key="g.id" class="badge bg-soft-success text-success p-2 px-3 rounded-pill">
                {{ g.name }}
              </span>
              <span v-if="!user.groups?.length" class="text-muted small">بدون گروه</span>
            </div>
          </div>
        </div>

        <div class="col-md-6">
          <div class="glass-card shadow-sm p-4 h-100">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <h6 class="fw-bold m-0"><i class="bi bi-shield-lock text-warning me-2"></i> مجوزهای اختصاصی</h6>
              <button class="btn btn-sm btn-soft-warning rounded-circle" @click="goEditPermissions" title="ویرایش مجوزها">
                <i class="bi bi-pencil"></i>
              </button>
            </div>
            <div class="d-flex flex-wrap gap-2">
              <span v-for="p in user.user_permissions" :key="p.id" class="badge bg-soft-warning text-warning-dark p-2 px-3 rounded-pill">
                {{ p.name }}
              </span>
              <span v-if="!user.user_permissions?.length" class="text-muted small">بدون مجوز اختصاصی</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../../api/axios'
import Swal from 'sweetalert2'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const userId = route.params.user_id

const user = ref({
  username: '',
  email: '',
  first_name: '',
  last_name: '',
  gender: '', // اضافه شدن فیلد جنسیت
  phone_number: '',
  groups: [],
  user_permissions: []
})

const fetchUser = async () => {
  loading.value = true
  try {
    const res = await api.get(`accounts/user-detail/${userId}/`)
    user.value = res.data
  } catch (err) {
    Swal.fire('خطا', 'اطلاعات کاربر دریافت نشد', 'error')
  } finally {
    loading.value = false
  }
}

const updateUser = async () => {
  try {
    // اصلاح ایمیل قبل از ارسال برای جلوگیری از خطای UNIQUE
    const payload = {
      ...user.value,
      email: user.value.email && user.value.email.trim() === '' ? null : user.value.email,
      // جدا کردن آی‌دی‌ها در صورتی که بک‌اِند فقط ID می‌خواهد
      groups: user.value.groups.map(g => g.id),
      user_permissions: user.value.user_permissions.map(p => p.id)
    }

    await api.patch(`accounts/user-detail/${userId}/`, payload)
    Swal.fire({
      icon: 'success',
      title: 'ذخیره شد',
      text: 'تغییرات با موفقیت اعمال گردید',
      timer: 2000,
      showConfirmButton: false
    })
  } catch (err) {
    Swal.fire('خطا', 'مشکلی در ذخیره اطلاعات رخ داد', 'error')
  }
}

const cancelEdit = () => router.back()
const goEditGroups = () => router.push({ name: 'UserGroupsUpdate', params: { user_id: userId } })
const goEditPermissions = () => router.push({ name: 'UserPermissionsUpdate', params: { user_id: userId } })

onMounted(fetchUser)
</script>

<style scoped>
.max-w-900 { max-width: 900px; }

.glass-card {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.5);
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
  transition: 0.3s;
}

.select-custom {
  cursor: pointer;
  appearance: none;
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

.btn-soft-success { background: #ecfdf5; color: #059669; border: none; }
.btn-soft-warning { background: #fffbeb; color: #b45309; border: none; }
.bg-soft-success { background: #ecfdf5; }
.bg-soft-warning { background: #fffbeb; }
.text-warning-dark { color: #b45309; }

.btn-primary-gradient {
  background: linear-gradient(135deg, #0d6efd 0%, #00d4ff 100%);
  border: none;
  color: white;
  transition: 0.3s;
}

.btn-primary-gradient:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 15px rgba(13, 110, 253, 0.2);
}
</style>