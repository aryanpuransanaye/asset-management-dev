<template>
  <div class="edit-group-page container py-5" dir="rtl">
    <div class="max-w-800 mx-auto mb-5 text-center">
      <div class="icon-box-header shadow-sm mb-3">
        <i class="bi bi-pencil-square text-primary"></i>
      </div>
      <h3 class="fw-bold text-dark">ویرایش تنظیمات گروه</h3>
      <p class="text-muted">مشخصات کلی، دسترسی‌ها و اعضای گروه را مدیریت کنید</p>
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status"></div>
      <p class="mt-3 text-muted">در حال دریافت اطلاعات...</p>
    </div>

    <div v-else class="max-w-800 mx-auto">
      <div class="row g-4">
        <div class="col-12">
          <div class="glass-card shadow-sm p-4 p-md-5 border-0">
            <h5 class="fw-bold mb-4 d-flex align-items-center">
              <span class="dot-indicator me-2"></span>
              اطلاعات پایه
            </h5>
            
            <form @submit.prevent="updateGroup">
              <div class="mb-4">
                <label class="form-label fw-bold small text-secondary">نام گروه</label>
                <div class="input-group-modern">
                  <i class="bi bi-tag"></i>
                  <input
                    v-model="form.name"
                    type="text"
                    class="form-control-custom"
                    placeholder="مثلاً: مدیران ارشد، تیم فنی..."
                    required
                  />
                </div>
              </div>

              <div class="d-flex justify-content-between align-items-center mt-5">
                <button type="button" class="btn btn-light-modern px-4" @click="goBack">
                  انصراف
                </button>
                <button type="submit" class="btn btn-save-gradient px-5 shadow-sm" :disabled="saving">
                  <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
                  {{ saving ? 'در حال ثبت...' : 'ذخیره تغییرات' }}
                </button>
              </div>
            </form>
          </div>
        </div>

        <div class="col-md-6">
          <div class="action-card shadow-sm h-100" @click="goToPermissions">
            <div class="action-icon bg-soft-primary">
              <i class="bi bi-shield-lock-fill"></i>
            </div>
            <div class="ms-3">
              <h6 class="fw-bold m-0">مدیریت دسترسی‌ها</h6>
              <p class="text-muted small m-0">تعیین سطوح دسترسی گروه</p>
            </div>
            <i class="bi bi-chevron-left ms-auto text-muted"></i>
          </div>
        </div>

        <div class="col-md-6">
          <div class="action-card shadow-sm h-100" @click="goToUsers">
            <div class="action-icon bg-soft-success">
              <i class="bi bi-people-fill"></i>
            </div>
            <div class="ms-3">
              <h6 class="fw-bold m-0">مدیریت کاربران</h6>
              <p class="text-muted small m-0">افزودن یا حذف اعضا</p>
            </div>
            <i class="bi bi-chevron-left ms-auto text-muted"></i>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/api/axios'
import Swal from 'sweetalert2'

const route = useRoute()
const router = useRouter()

const groupID = route.params.group_id
const loading = ref(true)
const saving = ref(false)

const form = ref({
  name: ''
})

const fetchGroup = async () => {
  try {
    const res = await api.get(`accounts/group-detail/${groupID}/`)
    form.value.name = res.data.name
  } catch (err) {
    Swal.fire('خطا', 'اطلاعات گروه یافت نشد.', 'error')
  }
}

const updateGroup = async () => {
  saving.value = true
  try {
    await api.put(`accounts/group-detail/${groupID}/`, {
      name: form.value.name
    })
    Swal.fire({
      icon: 'success',
      title: 'بروزرسانی شد',
      text: 'نام گروه با موفقیت تغییر کرد.',
      timer: 2000,
      showConfirmButton: false
    })
  } catch (err) {
    Swal.fire('خطا', 'بروزرسانی با مشکل مواجه شد.', 'error')
  } finally {
    saving.value = false
  }
}

const goToPermissions = () => router.push({ name: 'GroupPermissionsUpdate', params: { group_id: groupID } })
const goToUsers = () => router.push({ name: 'GroupUsersUpdate', params: { group_id: groupID } })
const goBack = () => router.back()

onMounted(async () => {
  loading.value = true
  await fetchGroup()
  loading.value = false
})
</script>

<style scoped>
.max-w-800 { max-width: 800px; }

/* هدر */
.icon-box-header {
  width: 70px; height: 70px;
  background: white;
  border-radius: 20px;
  display: flex; align-items: center; justify-content: center;
  font-size: 2rem; margin: 0 auto;
}

/* کارت اصلی */
.glass-card {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border-radius: 24px;
  border: 1px solid #f1f5f9 !important;
}

.dot-indicator {
  width: 10px; height: 10px;
  background: #0061ff;
  border-radius: 50%;
  display: inline-block;
}

/* اینپوت مدرن */
.input-group-modern {
  position: relative;
  display: flex; align-items: center;
}
.input-group-modern i {
  position: absolute; right: 15px; color: #94a3b8;
}
.form-control-custom {
  width: 100%;
  padding: 12px 45px 12px 15px;
  border-radius: 14px;
  border: 2px solid #f1f5f9;
  background: #f8fafc;
  transition: 0.3s;
}
.form-control-custom:focus {
  outline: none;
  border-color: #0061ff;
  background: white;
  box-shadow: 0 0 0 4px rgba(0, 97, 255, 0.1);
}

/* کارت‌های عملیات */
.action-card {
  background: white;
  padding: 20px;
  border-radius: 20px;
  display: flex; align-items: center;
  cursor: pointer;
  transition: 0.3s;
  border: 1px solid #f1f5f9;
}
.action-card:hover {
  transform: translateY(-5px);
  border-color: #0061ff;
  box-shadow: 0 10px 20px rgba(0,0,0,0.05) !important;
}

.action-icon {
  width: 50px; height: 50px;
  border-radius: 15px;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.4rem;
}
.bg-soft-primary { background: #eef2ff; color: #4338ca; }
.bg-soft-success { background: #ecfdf5; color: #059669; }

/* دکمه‌ها */
.btn-save-gradient {
  background: linear-gradient(135deg, #0061ff 0%, #60a5fa 100%);
  color: white; border: none;
  border-radius: 12px; font-weight: bold;
}
.btn-light-modern {
  background: #f1f5f9;
  color: #475569;
  border: none;
  border-radius: 12px;
}
</style>