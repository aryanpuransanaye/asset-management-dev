<template>
  <div class="group-permissions-page container py-5" dir="rtl">
    <div class="d-flex justify-content-between align-items-center mb-5 max-w-1100 mx-auto px-2">
      <div>
        <h3 class="fw-bold text-dark m-0">
          <i class="bi bi-shield-lock-fill me-2 text-warning"></i> مدیریت دسترسی‌های گروه
        </h3>
        <p class="text-muted small mt-1">تنظیم سطوح دسترسی برای گروه: <span class="text-primary fw-bold">{{ groupName }}</span></p>
      </div>
      <button class="btn btn-light border rounded-pill px-4 shadow-sm" @click="goBack">
        <i class="bi bi-arrow-right me-1"></i> بازگشت
      </button>
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" style="width: 3rem; height: 3rem;"></div>
      <p class="mt-3 text-muted">در حال بارگذاری لیست مجوزها...</p>
    </div>

    <div v-else class="max-w-1100 mx-auto">
      <div class="row g-4">
        <div class="col-lg-6">
          <div class="glass-card shadow-sm border-0 h-100">
            <div class="p-4 border-bottom d-flex justify-content-between align-items-center bg-light-subtle">
              <h6 class="fw-bold m-0"><i class="bi bi-globe2 me-2 text-primary"></i> مخزن کل دسترسی‌ها</h6>
              <span class="badge bg-soft-primary text-primary">{{ filteredAvailable.length }} مورد</span>
            </div>
            
            <div class="p-3">
              <div class="search-input-group">
                <i class="bi bi-search"></i>
                <input v-model="searchQuery" type="text" placeholder="جستجو در مجوزها..." class="form-control-clean">
              </div>
            </div>

            <div class="card-body-scrollable custom-scrollbar px-3">
              <transition-group name="list" tag="div" class="list-container">
                <div v-for="perm in filteredAvailable" :key="perm.id" class="perm-item available mb-2">
                  <div class="perm-info">
                    <span class="perm-name">{{ perm.name }}</span>
                    <span class="perm-code text-muted">{{ perm.codename || 'system_perm' }}</span>
                  </div>
                  <button class="btn-action add" @click="addPermission(perm)">
                    <i class="bi bi-plus-circle-fill"></i>
                  </button>
                </div>
              </transition-group>
              <div v-if="filteredAvailable.length === 0" class="empty-state">موردی یافت نشد.</div>
            </div>
          </div>
        </div>

        <div class="col-lg-6">
          <div class="glass-card shadow-sm border-0 h-100 active-perms-border">
            <div class="p-4 border-bottom d-flex justify-content-between align-items-center bg-gold-subtle">
              <h6 class="fw-bold m-0 text-dark"><i class="bi bi-key-fill me-2 text-warning"></i> مجوزهای فعال این گروه</h6>
              <span class="badge bg-warning text-dark">{{ groupPermissions.length }} مورد</span>
            </div>

            <div class="card-body-scrollable custom-scrollbar p-3">
              <transition-group name="list" tag="div" class="list-container">
                <div v-for="perm in groupPermissions" :key="perm.id" class="perm-item active mb-2">
                  <button class="btn-action remove me-3" @click="removePermission(perm)">
                    <i class="bi bi-dash-circle-fill"></i>
                  </button>
                  <div class="perm-info text-end">
                    <span class="perm-name fw-bold">{{ perm.name }}</span>
                    <span class="perm-code text-muted small">دسترسی فعال</span>
                  </div>
                </div>
              </transition-group>
              <div v-if="groupPermissions.length === 0" class="empty-state py-5">
                <i class="bi bi-shield-slash display-4 opacity-25"></i>
                <p class="mt-2">هیچ مجوزی برای این گروه ثبت نشده است.</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="mt-5 text-center action-area p-4 glass-card shadow">
        <p class="text-muted small mb-3"><i class="bi bi-info-circle me-1"></i> با کلیک بر روی ذخیره، تمامی تغییرات فوق بر روی گروه اعمال خواهد شد.</p>
        <div class="d-flex justify-content-center gap-3">
          <button class="btn btn-primary-gradient px-5 py-2 rounded-pill shadow" @click="saveChanges" :disabled="saving">
            <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
            {{ saving ? 'در حال ذخیره‌سازی...' : 'ذخیره نهایی تغییرات' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/api/axios'
import Swal from 'sweetalert2'

const route = useRoute()
const router = useRouter()
const groupID = route.params.group_id

const loading = ref(true)
const saving = ref(false)
const searchQuery = ref('')
const groupName = ref('')
const availablePermissions = ref([])
const groupPermissions = ref([])

const fetchData = async () => {
  loading.value = true
  try {
    const [groupRes, allPermsRes] = await Promise.all([
      api.get(`accounts/group-detail/${groupID}/`),
      api.get('accounts/permissions-list/')
    ])

    groupName.value = groupRes.data.name
    groupPermissions.value = groupRes.data.group_permissions || []

    availablePermissions.value = allPermsRes.data.filter(
      p => !groupPermissions.value.some(gp => gp.id === p.id)
    )
  } catch (err) {
    Swal.fire('خطا', 'دریافت اطلاعات با شکست مواجه شد', 'error')
  } finally {
    loading.value = false
  }
}

const filteredAvailable = computed(() => {
  const query = searchQuery.value.toLowerCase().trim()
  if (!query) return availablePermissions.value
  return availablePermissions.value.filter(p => p.name.toLowerCase().includes(query))
})

const addPermission = (perm) => {
  groupPermissions.value.unshift(perm)
  availablePermissions.value = availablePermissions.value.filter(p => p.id !== perm.id)
}

const removePermission = (perm) => {
  availablePermissions.value.unshift(perm)
  groupPermissions.value = groupPermissions.value.filter(p => p.id !== perm.id)
}

const saveChanges = async () => {
  saving.value = true
  try {
    const payload = {
      name: groupName.value,
      permissions: groupPermissions.value.map(p => p.id) 
    }
    await api.put(`accounts/group-detail/${groupID}/`, payload)
    Swal.fire('موفقیت', 'دسترسی‌ها با موفقیت به‌روزرسانی شدند.', 'success')
  } catch (err) {
    Swal.fire('خطا', 'ثبت تغییرات انجام نشد.', 'error')
  } finally {
    saving.value = false
  }
}

const goBack = () => router.back()
onMounted(fetchData)
</script>

<style scoped>
.max-w-1100 { max-width: 1100px; }

/* کارت شیشه‌ای */
.glass-card {
  background: white;
  border-radius: 20px;
  overflow: hidden;
  border: 1px solid #f1f5f9;
}

.active-perms-border { border-top: 5px solid #ffc107 !important; }

/* اسکرول */
.card-body-scrollable {
  height: 450px;
  overflow-y: auto;
}

/* آیتم‌های لیست */
.perm-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 18px;
  border-radius: 12px;
  background: #f8fafc;
  border: 1px solid #edf2f7;
  transition: 0.2s;
}

.perm-item:hover {
  background: #f1f5f9;
  transform: translateX(3px);
}

.perm-item.active {
  background: #fffdf5;
  border-right: 4px solid #ffc107 !important;
}

.perm-info { display: flex; flex-direction: column; }
.perm-name { font-size: 0.9rem; font-weight: 600; color: #334155; }
.perm-code { font-size: 0.7rem; color: #94a3b8; }

/* دکمه‌های عملیات */
.btn-action {
  background: none;
  border: none;
  font-size: 1.4rem;
  line-height: 1;
  transition: 0.2s;
  padding: 0;
}
.btn-action.add { color: #10b981; }
.btn-action.remove { color: #ef4444; }
.btn-action:hover { transform: scale(1.2); }

/* جستجو */
.search-input-group { position: relative; }
.search-input-group i { position: absolute; right: 12px; top: 10px; color: #94a3b8; }
.form-control-clean {
  width: 100%;
  padding: 8px 35px 8px 15px;
  border-radius: 10px;
  border: 1px solid #e2e8f0;
  background: #f8fafc;
  font-size: 0.85rem;
}

/* انیمیشن */
.list-enter-active, .list-leave-active { transition: all 0.3s ease; }
.list-enter-from, .list-leave-to { opacity: 0; transform: translateY(10px); }

/* دکمه ذخیره */
.btn-primary-gradient {
  background: linear-gradient(135deg, #0d6efd 0%, #00d4ff 100%);
  border: none;
  color: white;
  font-weight: bold;
}

.bg-soft-primary { background: #e0f2fe; }
.bg-gold-subtle { background: #fffcf0; }
.empty-state { text-align: center; color: #cbd5e1; padding: 40px 0; }

.custom-scrollbar::-webkit-scrollbar { width: 5px; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #e2e8f0; border-radius: 10px; }
</style>