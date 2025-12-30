<template>
    <div class="group-create-page container py-5" dir="rtl">
      <div class="d-flex justify-content-between align-items-center mb-4 max-w-700 mx-auto px-2">
        <h3 class="fw-bold text-dark m-0">
          <i class="bi bi-collection-fill me-2 text-primary"></i> ایجاد گروه کاربری جدید
        </h3>
        <button class="btn btn-light border rounded-pill px-3 shadow-sm" @click="goBack">
          <i class="bi bi-arrow-right me-1"></i> بازگشت
        </button>
      </div>
  
      <div class="glass-form-card shadow-lg p-4 p-md-5 mx-auto">
        <div v-if="loading" class="text-center py-4">
          <div class="spinner-border text-primary" role="status"></div>
          <p class="mt-2 text-muted small">در حال پردازش...</p>
        </div>
  
        <form v-else @submit.prevent="createGroup">
          <div class="mb-4">
            <label class="form-label fw-bold small text-secondary">نام گروه</label>
            <div class="input-group-modern">
              <span class="icon"><i class="bi bi-tags"></i></span>
              <input
                v-model="form.name"
                type="text"
                class="form-control-modern"
                placeholder="مثلاً: مدیران ارشد، تیم فنی..."
                required
              />
            </div>
          </div>
  
          <hr class="my-4 opacity-25">
  
          <div class="mb-4">
            <label class="form-label fw-bold small text-secondary">اعضای گروه</label>
            <div class="multiselect-wrapper">
              <Multiselect
                v-model="form.user"
                :options="usersList"
                label="username"
                track-by="id"
                placeholder="کاربران مورد نظر را انتخاب کنید..."
                :multiple="true"
                :searchable="true"
                class="custom-multiselect"
              />
            </div>
            <div class="form-text x-small text-muted mt-2">
              <i class="bi bi-info-circle me-1"></i> کاربران انتخاب شده به صورت خودکار عضو این گروه می‌شوند.
            </div>
          </div>
  
          <div class="mb-5">
            <label class="form-label fw-bold small text-secondary">مجوزهای سطح گروه</label>
            <div class="multiselect-wrapper">
              <Multiselect
                v-model="form.permissions"
                :options="permissionsList"
                label="name"
                track-by="id"
                placeholder="دسترسی‌های این گروه را تعیین کنید..."
                :multiple="true"
                :searchable="true"
                class="custom-multiselect warning-mode"
              />
            </div>
          </div>
  
          <div class="mt-4 pt-2">
            <button type="submit" class="btn btn-primary-gradient w-100 py-3 rounded-pill fw-bold shadow-sm mb-3">
              <i class="bi bi-plus-circle-fill me-2"></i> ثبت و ایجاد گروه جدید
            </button>
            <button type="button" class="btn btn-link w-100 text-decoration-none text-secondary small" @click="goBack">
              انصراف و بازگشت
            </button>
          </div>
        </form>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue'
  import { useRouter } from 'vue-router'
  import api from '../../api/axios'
  import Multiselect from 'vue-multiselect'
  import 'vue-multiselect/dist/vue-multiselect.min.css'
  import Swal from 'sweetalert2'
  
  const router = useRouter()
  const loading = ref(false)
  
  const form = ref({
    name: '',
    user: [],
    permissions: []
  })
  
  const usersList = ref([])
  const permissionsList = ref([])
  
  const fetchData = async () => {
    try {
      const [usersRes, permsRes] = await Promise.all([
        api.get('accounts/users-list/'),
        api.get('accounts/permissions-list/')
      ])
      usersList.value = usersRes.data
      permissionsList.value = permsRes.data
    } catch (err) {
      console.error(err)
    }
  }
  
  const createGroup = async () => {
    loading.value = true
    try {
      const payload = {
        name: form.value.name,
        user: form.value.user.map(u => u.id),
        permissions: form.value.permissions.map(p => p.id)
      }
      await api.post('accounts/group-detail/', payload)
      
      await Swal.fire({
        icon: 'success',
        title: 'موفقیت‌آمیز',
        text: `گروه "${form.value.name}" با موفقیت ایجاد شد`,
        confirmButtonText: 'متوجه شدم'
      })
      
      router.push({ name: 'GroupsList' })
    } catch (err) {
      Swal.fire('خطا', 'مشکلی در ایجاد گروه پیش آمد', 'error')
    } finally {
      loading.value = false
    }
  }
  
  const goBack = () => router.back()
  
  onMounted(fetchData)
  </script>
  
  <style scoped>
  .max-w-700 { max-width: 700px; }
  .x-small { font-size: 0.75rem; }
  
  /* کارت شیشه‌ای */
  .glass-form-card {
    background: rgba(255, 255, 255, 0.9);
    backdrop-filter: blur(15px);
    border-radius: 24px;
    border: 1px solid rgba(255, 255, 255, 0.5);
    max-width: 700px;
  }
  
  /* ورودی نام گروه */
  .input-group-modern {
    position: relative;
    display: flex;
    align-items: center;
  }
  .input-group-modern .icon {
    position: absolute;
    right: 15px;
    color: #0d6efd;
    z-index: 5;
  }
  .form-control-modern {
    width: 100%;
    padding: 12px 45px 12px 15px;
    border-radius: 12px;
    border: 1px solid #e2e8f0;
    background: #f8fafc;
    transition: all 0.3s;
  }
  .form-control-modern:focus {
    outline: none;
    background: white;
    border-color: #0d6efd;
    box-shadow: 0 0 0 4px rgba(13, 110, 253, 0.1);
  }
  
  /* سفارشی‌سازی Multiselect */
  .custom-multiselect :deep(.multiselect__tags) {
    border-radius: 12px;
    border: 1px solid #e2e8f0;
    background: #f8fafc;
    padding-top: 8px;
    min-height: 50px;
  }
  
  .custom-multiselect :deep(.multiselect__option--highlight) {
    background: #0d6efd;
  }
  
  .warning-mode :deep(.multiselect__tag) {
    background: #fbbf24;
    color: #000;
  }
  
  .custom-multiselect :deep(.multiselect__placeholder) {
    margin-bottom: 8px;
    padding-top: 2px;
  }
  
  /* دکمه گرادینت */
  .btn-primary-gradient {
    background: linear-gradient(135deg, #0d6efd 0%, #00d4ff 100%);
    border: none;
    color: white;
    transition: all 0.3s;
  }
  .btn-primary-gradient:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(13, 110, 253, 0.3);
  }
  
  /* تنظیم جهت باز شدن برای RTL */
  .custom-multiselect :deep(.multiselect__select) {
    left: 1px;
    right: auto;
  }
  </style>