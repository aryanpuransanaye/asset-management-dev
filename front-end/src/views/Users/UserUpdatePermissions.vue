<template>
  <div class="permissions-management-page container py-5" dir="rtl">
    <div class="d-flex justify-content-between align-items-center mb-4 max-w-1000 mx-auto px-2">
      <h3 class="fw-bold text-dark m-0">
        <i class="bi bi-shield-lock-fill me-2 text-warning"></i> مدیریت مجوزهای اختصاصی
      </h3>
      <button class="btn btn-light border rounded-pill px-3 shadow-sm" @click="router.back()">
        <i class="bi bi-arrow-right me-1"></i> بازگشت
      </button>
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-warning" role="status"></div>
      <p class="mt-2 text-muted small">در حال فراخوانی لیست مجوزها...</p>
    </div>

    <div v-else class="max-w-1000 mx-auto">
      <div class="row g-4">
        
        <div class="col-md-6">
          <div class="glass-card shadow-sm h-100">
            <div class="card-header-custom bg-soft-warning text-warning-dark">
              <i class="bi bi-search me-2"></i> انتخاب مجوز جدید
            </div>
            <div class="p-3 bg-light-subtle">
              <div class="input-group-search">
                <i class="bi bi-filter"></i>
                <input v-model="searchQuery" class="form-control-modern-sm" placeholder="جستجوی نام یا کد مجوز..." />
              </div>
            </div>
            <div class="card-body-custom">
              <ul class="list-group list-group-flush">
                <li v-for="perm in filteredAvailable" :key="perm.id" class="list-group-item perm-item animate-in">
                  <div class="d-flex flex-column">
                    <span class="fw-semibold text-dark small">{{ perm.name }}</span>
                    <code class="x-small text-muted">{{ perm.codename }}</code>
                  </div>
                  <button class="btn-action-round add" @click="addPermission(perm)" title="اضافه کردن">
                    <i class="bi bi-plus-lg"></i>
                  </button>
                </li>
                <li v-if="filteredAvailable.length === 0" class="text-center py-4 text-muted small italic">
                  مجوزی یافت نشد
                </li>
              </ul>
            </div>
          </div>
        </div>

        <div class="col-md-6">
          <div class="glass-card shadow-sm h-100 border-warning-subtle">
            <div class="card-header-custom bg-warning text-white">
              <i class="bi bi-key-fill me-2"></i> مجوزهای فعال این کاربر
            </div>
            <div class="card-body-custom">
              <ul class="list-group list-group-flush">
                <li v-for="perm in userPermissions" :key="perm.id" class="list-group-item perm-item active-perm animate-in">
                  <div class="d-flex flex-column">
                    <span class="fw-bold text-dark small">{{ perm.name }}</span>
                    <code class="x-small text-warning-dark">{{ perm.codename }}</code>
                  </div>
                  <button class="btn-action-round remove" @click="removePermission(perm)" title="حذف دسترسی">
                    <i class="bi bi-trash3-fill"></i>
                  </button>
                </li>
                <li v-if="userPermissions.length === 0" class="text-center py-5 text-muted small">
                   کاربر فعلاً هیچ مجوز اختصاصی ندارد.
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      <div class="text-center mt-5">
        <div class="save-bar p-3 glass-card d-inline-block px-5 shadow">
          <button class="btn btn-warning-gradient shadow px-5 py-2 rounded-pill fw-bold text-white" @click="savePermissions" :disabled="loading">
            <i class="bi bi-shield-check me-2"></i> ثبت و به‌روزرسانی نهایی
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../../api/axios'
import Swal from 'sweetalert2'

const router = useRouter()
const route = useRoute()
const userId = route.params.user_id

const loading = ref(false)
const searchQuery = ref('')

const allPermissions = ref([])
const userPermissions = ref([])
const availablePermissions = ref([])

const fetchData = async () => {
  loading.value = true
  try {
    const [allRes, userRes] = await Promise.all([
      api.get('accounts/permissions-list/'),
      api.get(`accounts/user-detail/${userId}/`)
    ])

    allPermissions.value = allRes.data
    userPermissions.value = userRes.data.user_permissions || []

    availablePermissions.value = allPermissions.value.filter(
      p => !userPermissions.value.some(up => up.id === p.id)
    )
  } catch (err) {
    Swal.fire('خطا', 'فراخوانی مجوزها ناموفق بود', 'error')
  } finally {
    loading.value = false
  }
}

const filteredAvailable = computed(() => {
  if (!searchQuery.value) return availablePermissions.value
  const q = searchQuery.value.toLowerCase()
  return availablePermissions.value.filter(p =>
    p.name.toLowerCase().includes(q) || p.codename.toLowerCase().includes(q)
  )
})

const addPermission = (perm) => {
  userPermissions.value.push(perm)
  availablePermissions.value = availablePermissions.value.filter(p => p.id !== perm.id)
}

const removePermission = (perm) => {
  availablePermissions.value.push(perm)
  userPermissions.value = userPermissions.value.filter(p => p.id !== perm.id)
}

const savePermissions = async () => {
  try {
    const ids = userPermissions.value.map(p => p.id)
    await api.patch(`accounts/change-permissions/${userId}/`, { permission_ids: ids })
    
    await Swal.fire({
      icon: 'success',
      title: 'انجام شد',
      text: 'سطح دسترسی کاربر با موفقیت تغییر کرد',
      timer: 2000,
      showConfirmButton: false
    })
    router.push({ name: 'UserUpdate', params: { user_id: userId } })
  } catch (err) {
    Swal.fire('خطا در ذخیره', 'اعمال تغییرات با خطا مواجه شد', 'error')
  }
}

onMounted(fetchData)
</script>

<style scoped>
.max-w-1000 { max-width: 1000px; }
.x-small { font-size: 0.7rem; }

/* کارت شیشه‌ای */
.glass-card {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.5);
  overflow: hidden;
}

.card-header-custom {
  padding: 15px 20px;
  font-weight: bold;
  font-size: 0.95rem;
}

.card-body-custom {
  max-height: 480px;
  overflow-y: auto;
  padding: 15px;
}

/* فیلد جستجو مدرن */
.input-group-search {
  position: relative;
  display: flex;
  align-items: center;
}
.input-group-search i {
  position: absolute;
  right: 12px;
  color: #fbbf24;
}
.form-control-modern-sm {
  width: 100%;
  padding: 8px 35px 8px 12px;
  border-radius: 10px;
  border: 1px solid #e2e8f0;
  font-size: 0.85rem;
  background: white;
}

/* آیتم‌های مجوز */
.perm-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 15px;
  margin-bottom: 6px;
  border: 1px solid #f1f5f9;
  border-radius: 12px;
  transition: all 0.2s;
}

.active-perm {
  background-color: #fffbeb;
  border-color: #fef3c7;
}

/* دکمه‌های دایره‌ای عملیات */
.btn-action-round {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.9rem;
  flex-shrink: 0;
}
.btn-action-round.add { background: #dcfce7; color: #166534; }
.btn-action-round.remove { background: #fee2e2; color: #991b1b; }

/* دکمه با گرادینت نارنجی */
.btn-warning-gradient {
  background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%);
  border: none;
}

.animate-in {
  animation: slideIn 0.25s ease-out;
}

@keyframes slideIn {
  from { opacity: 0; transform: translateX(-10px); }
  to { opacity: 1; transform: translateX(0); }
}

.italic { font-style: italic; }
.text-warning-dark { color: #92400e; }
.bg-soft-warning { background-color: #fffbeb; }

/* اسکرول‌بار */
.card-body-custom::-webkit-scrollbar { width: 4px; }
.card-body-custom::-webkit-scrollbar-thumb { background: #fbbf24; border-radius: 10px; }
</style>