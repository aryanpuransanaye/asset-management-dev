<template>
  <div class="group-management-page container py-5" dir="rtl">
    <div class="d-flex justify-content-between align-items-center mb-5 max-w-1100 mx-auto px-2">
      <div>
        <h3 class="fw-bold text-dark m-0">
          <i class="bi bi-person-gear me-2 text-primary"></i> مدیریت اعضای گروه
        </h3>
        <p class="text-muted small mt-1">
          گروه: <span class="text-primary fw-bold">{{ groupName }}</span>
        </p>
      </div>
      <div v-if="!loading" class="stats-badge shadow-sm border">
        <span class="label">تعداد فعلی اعضا:</span>
        <span class="value text-primary fw-bold">{{ groupUsers.length }} نفر</span>
      </div>
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-grow text-primary" role="status"></div>
      <p class="mt-3 text-muted">در حال فراخوانی لیست کاربران...</p>
    </div>

    <div v-else class="max-w-1100 mx-auto">
      <div class="row g-4">
        
        <div class="col-lg-6">
          <div class="glass-card shadow-sm h-100 border-0">
            <div class="card-header-custom bg-soft-primary">
              <div class="d-flex justify-content-between align-items-center">
                <span class="fw-bold"><i class="bi bi-search me-2"></i> جستجو و انتخاب</span>
                <span class="badge bg-primary rounded-pill">{{ filteredAvailable.length }} کاربر</span>
              </div>
            </div>
            
            <div class="p-3">
              <div class="search-box-modern">
                <i class="bi bi-filter"></i>
                <input 
                  v-model="searchQuery" 
                  type="text" 
                  class="form-input-clean" 
                  placeholder="جستجوی نام یا ایمیل..."
                >
              </div>
            </div>

            <div class="card-body-scrollable custom-scrollbar">
              <transition-group name="list" tag="ul" class="list-group list-group-flush px-2">
                <li 
                  v-for="user in filteredAvailable" 
                  :key="user.id" 
                  class="list-group-item user-card-item mb-2"
                >
                  <div class="d-flex align-items-center w-100">
                    <div class="user-avatar-sm me-3">{{ user.username.charAt(0).toUpperCase() }}</div>
                    <div class="flex-grow-1 text-end">
                      <div class="fw-bold text-dark small text-start">{{ user.username }}</div>
                      <div class="text-muted x-small text-start">{{ user.email || 'بدون ایمیل' }}</div>
                    </div>
                    <button class="btn-transfer add ms-2" @click="addUser(user)" title="افزودن به گروه">
                      <i class="bi bi-chevron-left"></i>
                    </button>
                  </div>
                </li>
              </transition-group>
              <div v-if="filteredAvailable.length === 0" class="text-center py-5 opacity-50 small">
                موردی یافت نشد
              </div>
            </div>
          </div>
        </div>

        <div class="col-lg-6">
          <div class="glass-card shadow-sm h-100 border-0 border-top-emerald">
            <div class="card-header-custom bg-emerald text-white">
              <div class="d-flex justify-content-between align-items-center">
                <span class="fw-bold"><i class="bi bi-person-check-fill me-2"></i> اعضای این گروه</span>
                <i class="bi bi-shield-shaded"></i>
              </div>
            </div>

            <div class="card-body-scrollable custom-scrollbar p-3 mt-2">
              <transition-group name="list" tag="ul" class="list-group list-group-flush px-2">
                <li 
                  v-for="user in groupUsers" 
                  :key="user.id" 
                  class="list-group-item user-card-item member mb-2"
                >
                  <div class="d-flex align-items-center w-100">
                    <button class="btn-transfer remove me-3" @click="removeUser(user)" title="حذف از گروه">
                      <i class="bi bi-chevron-right"></i>
                    </button>
                    <div class="flex-grow-1">
                      <div class="fw-bold text-dark small">{{ user.username }}</div>
                      <div class="text-muted x-small">عضو گروه</div>
                    </div>
                    <div class="user-avatar-sm member-bg ms-2">{{ user.username.charAt(0).toUpperCase() }}</div>
                  </div>
                </li>
              </transition-group>
              <div v-if="groupUsers.length === 0" class="text-center py-5 opacity-50">
                <i class="bi bi-people display-4 d-block mb-3"></i>
                <p class="small">این گروه هنوز عضوی ندارد</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="action-bar-floating shadow-lg">
        <div class="d-flex align-items-center gap-3">
          <button 
            class="btn btn-save-gradient px-5 rounded-pill shadow-sm" 
            @click="saveChanges" 
            :disabled="saving || loading"
          >
            <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
            {{ saving ? 'در حال ثبت...' : 'ذخیره نهایی تغییرات' }}
          </button>
          <button class="btn btn-cancel-modern px-4 rounded-pill" @click="goBack">
            انصراف
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

// وضعیت‌ها
const loading = ref(true)
const saving = ref(false)
const searchQuery = ref('')

// داده‌ها
const groupName = ref('')
const availableUsers = ref([]) 
const groupUsers = ref([])     

// دریافت اطلاعات
const fetchData = async () => {
  loading.value = true
  try {
    const [groupRes, allUsersRes] = await Promise.all([
      api.get(`accounts/group-detail/${groupID}/`),
      api.get('accounts/users-list/')
    ])

    groupName.value = groupRes.data.name
    groupUsers.value = groupRes.data.custom_user_set || []

    // فیلتر کردن لیست (کاربرانی که در حال حاضر عضو نیستند)
    availableUsers.value = allUsersRes.data.filter(
      systemUser => !groupUsers.value.some(member => member.id === systemUser.id)
    )
  } catch (err) {
    console.error("Error:", err)
    Swal.fire('خطا', 'مشکلی در بارگذاری داده‌ها پیش آمد.', 'error')
  } finally {
    loading.value = false
  }
}

// فیلتر جستجو
const filteredAvailable = computed(() => {
  const query = searchQuery.value.toLowerCase().trim()
  if (!query) return availableUsers.value
  
  return availableUsers.value.filter(u => 
    u.username.toLowerCase().includes(query) || 
    (u.email && u.email.toLowerCase().includes(query))
  )
})

// عملیات جابه‌جایی
const addUser = (user) => {
  groupUsers.value.unshift(user) // اضافه به ابتدای لیست اعضا
  availableUsers.value = availableUsers.value.filter(u => u.id !== user.id)
}

const removeUser = (user) => {
  availableUsers.value.unshift(user) // بازگشت به مخزن کاربران
  groupUsers.value = groupUsers.value.filter(u => u.id !== user.id)
}

// ذخیره‌سازی
const saveChanges = async () => {
  if (saving.value) return
  
  saving.value = true
  try {
    const payload = {
      users: groupUsers.value.map(u => u.id)
    }
    
    await api.patch(`accounts/group-detail/${groupID}/`, payload)
    
    await Swal.fire({
      icon: 'success',
      title: 'ذخیره شد',
      text: 'لیست اعضای گروه با موفقیت به‌روزرسانی شد.',
      confirmButtonText: 'عالی'
    })
    
    router.push({ name: 'GroupsList' })
  } catch (err) {
    Swal.fire('خطا', 'ثبت تغییرات با مشکل مواجه شد.', 'error')
  } finally {
    saving.value = false
  }
}

const goBack = () => router.back()

onMounted(fetchData)
</script>

<style scoped>
.max-w-1100 { max-width: 1100px; }
.x-small { font-size: 0.75rem; }

/* کارت شیشه‌ای */
.glass-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  overflow: hidden;
  border: 1px solid #edf2f7;
  display: flex;
  flex-direction: column;
}

.border-top-emerald { border-top: 5px solid #10b981 !important; }

.card-header-custom {
  padding: 18px 25px;
}
.bg-soft-primary { background: #f0f7ff; color: #0061ff; }
.bg-emerald { background: #10b981; }

/* بخش اسکرول */
.card-body-scrollable {
  height: 500px;
  overflow-y: auto;
}

.search-box-modern {
  position: relative;
  display: flex;
  align-items: center;
}
.search-box-modern i {
  position: absolute;
  right: 15px;
  color: #a0aec0;
}
.form-input-clean {
  width: 100%;
  padding: 10px 45px 10px 15px;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  background: #f8fafc;
  font-size: 0.85rem;
  transition: 0.3s;
}
.form-input-clean:focus {
  outline: none;
  border-color: #0061ff;
  background: #fff;
}

/* آیتم‌های کاربر */
.user-card-item {
  border: 1px solid #f1f5f9 !important;
  border-radius: 15px !important;
  padding: 12px 15px;
  transition: all 0.2s;
  background: #fff;
}
.user-card-item:hover {
  background: #f8fafc;
  transform: translateX(4px);
}
.user-card-item.member:hover {
  transform: translateX(-4px);
}

.user-avatar-sm {
  width: 36px;
  height: 36px;
  background: #e0e7ff;
  color: #4338ca;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  flex-shrink: 0;
}
.member-bg { background: #dcfce7; color: #059669; }

/* دکمه‌های جابه‌جایی */
.btn-transfer {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: 0.2s;
}
.btn-transfer.add { background: #f0fdf4; color: #16a34a; }
.btn-transfer.remove { background: #fef2f2; color: #dc2626; }
.btn-transfer:hover { transform: scale(1.15); }

/* نوار شناور */
.action-bar-floating {
  position: sticky;
  bottom: 20px;
  margin-top: 40px;
  background: white;
  padding: 15px 40px;
  border-radius: 100px;
  display: inline-block;
  left: 50%;
  transform: translateX(-50%);
  border: 1px solid #e2e8f0;
}

.btn-save-gradient {
  background: linear-gradient(135deg, #059669 0%, #10b981 100%);
  color: white;
  border: none;
  font-weight: bold;
}

.btn-cancel-modern {
  background: #f1f5f9;
  border: none;
  color: #64748b;
}

.stats-badge {
  background: white;
  padding: 8px 20px;
  border-radius: 12px;
}

/* انیمیشن لیست */
.list-move, .list-enter-active, .list-leave-active {
  transition: all 0.4s ease;
}
.list-enter-from, .list-leave-to {
  opacity: 0;
  transform: scale(0.6);
}

.custom-scrollbar::-webkit-scrollbar { width: 5px; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }
</style>