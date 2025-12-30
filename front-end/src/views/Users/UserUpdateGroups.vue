<template>
  <div class="groups-management-page container py-5" dir="rtl">
    <div class="d-flex justify-content-between align-items-center mb-4 max-w-1000 mx-auto px-2">
      <h3 class="fw-bold text-dark m-0">
        <i class="bi bi-people-fill me-2 text-primary"></i> مدیریت گروه‌های کاربر
      </h3>
      <button class="btn btn-light border rounded-pill px-3 shadow-sm" @click="router.back()">
        <i class="bi bi-arrow-right me-1"></i> بازگشت
      </button>
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status"></div>
      <p class="mt-2 text-muted">در حال دریافت لیست گروه‌ها...</p>
    </div>

    <div v-if="!loading" class="max-w-1000 mx-auto">
      <div class="row g-4">
        
        <div class="col-md-6">
          <div class="glass-card shadow-sm h-100">
            <div class="card-header-custom bg-soft-success text-success">
              <i class="bi bi-plus-circle-fill me-2"></i> گروه‌های موجود
            </div>
            <div class="card-body-custom">
              <div v-if="availableGroups.length === 0" class="text-center py-4 text-muted small">
                گروه جدیدی برای اضافه کردن وجود ندارد.
              </div>
              <ul class="list-group list-group-flush">
                <li v-for="group in availableGroups" :key="group.id" class="list-group-item group-item animate-in">
                  <span class="fw-semibold text-secondary">{{ group.name }}</span>
                  <button class="btn-action-round add" @click="addGroup(group)" title="اضافه کردن">
                    <i class="bi bi-plus-lg"></i>
                  </button>
                </li>
              </ul>
            </div>
          </div>
        </div>

        <div class="col-md-6">
          <div class="glass-card shadow-sm h-100">
            <div class="card-header-custom bg-soft-primary text-primary">
              <i class="bi bi-check-circle-fill me-2"></i> گروه‌های فعلی کاربر
            </div>
            <div class="card-body-custom">
              <div v-if="userGroups.length === 0" class="text-center py-4 text-muted small">
                کاربر هنوز عضو هیچ گروهی نشده است.
              </div>
              <ul class="list-group list-group-flush">
                <li v-for="group in userGroups" :key="group.id" class="list-group-item group-item active-group animate-in">
                  <span class="fw-bold text-dark">{{ group.name }}</span>
                  <button class="btn-action-round remove" @click="removeGroup(group)" title="حذف">
                    <i class="bi bi-trash3-fill"></i>
                  </button>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      <div class="text-center mt-5">
        <button class="btn btn-primary-gradient shadow px-5 py-3 rounded-pill fw-bold" @click="saveGroups">
          <i class="bi bi-cloud-arrow-up-fill me-2"></i> ذخیره نهایی تغییرات
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../api/axios'
import { useRoute, useRouter } from 'vue-router'
import Swal from 'sweetalert2'

const router = useRouter()
const route = useRoute()
const userId = route.params.user_id

const loading = ref(false)
const allGroups = ref([])
const userGroups = ref([])
const availableGroups = ref([])

const fetchData = async () => {
  loading.value = true
  try {
    const [groupsRes, userRes] = await Promise.all([
      api.get('accounts/groups-list/'),
      api.get(`accounts/user-detail/${userId}/`)
    ])
    allGroups.value = groupsRes.data
    userGroups.value = userRes.data.groups

    availableGroups.value = allGroups.value.filter(
      g => !userGroups.value.find(ug => ug.id === g.id)
    )
  } catch (err) {
    Swal.fire('خطا', 'مشکلی در دریافت اطلاعات پیش آمد', 'error')
  } finally {
    loading.value = false
  }
}

const addGroup = (group) => {
  userGroups.value.push(group)
  availableGroups.value = availableGroups.value.filter(g => g.id !== group.id)
}

const removeGroup = (group) => {
  availableGroups.value.push(group)
  userGroups.value = userGroups.value.filter(g => g.id !== group.id)
}

const saveGroups = async () => {
  try {
    const ids = userGroups.value.map(g => g.id).filter(id => id != null)
    await api.patch(`accounts/change-group/${userId}/`, { group_ids: ids })
    
    await Swal.fire({
      icon: 'success',
      title: 'با موفقیت ذخیره شد',
      timer: 1500,
      showConfirmButton: false
    })
    router.push({ name: 'UserUpdate', params: { user_id: userId } })
  } catch (err) {
    Swal.fire('خطا در ذخیره', 'تغییرات اعمال نشد', 'error')
  }
}

onMounted(fetchData)
</script>

<style scoped>
.max-w-1000 { max-width: 1000px; }

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
  border-bottom: 1px solid rgba(0,0,0,0.05);
  font-size: 1rem;
}

.card-body-custom {
  max-height: 450px;
  overflow-y: auto;
  padding: 10px;
}

/* آیتم‌های لیست */
.group-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 15px;
  margin-bottom: 8px;
  border: 1px solid #f1f5f9;
  border-radius: 12px;
  transition: all 0.2s ease;
}

.group-item:hover {
  background-color: #f8fafc;
  transform: scale(1.01);
}

.active-group {
  background-color: #f0f7ff;
  border-color: #e0f2fe;
}

/* دکمه‌های دایره‌ای عملیات */
.btn-action-round {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  font-size: 1rem;
}

.btn-action-round.add { background: #dcfce7; color: #166534; }
.btn-action-round.add:hover { background: #166534; color: white; }

.btn-action-round.remove { background: #fee2e2; color: #991b1b; }
.btn-action-round.remove:hover { background: #991b1b; color: white; }

/* دکمه اصلی گرادینت */
.btn-primary-gradient {
  background: linear-gradient(135deg, #0d6efd 0%, #00d4ff 100%);
  border: none;
  color: white;
  transition: 0.3s;
}

.btn-primary-gradient:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 20px rgba(13, 110, 253, 0.3);
}

/* رنگ‌های ملایم */
.bg-soft-success { background-color: #ecfdf5; }
.bg-soft-primary { background-color: #eff6ff; }

/* انیمیشن ورود آیتم‌ها */
.animate-in {
  animation: slideUp 0.3s ease forwards;
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* اسکرول‌بار زیبا */
.card-body-custom::-webkit-scrollbar { width: 5px; }
.card-body-custom::-webkit-scrollbar-track { background: transparent; }
.card-body-custom::-webkit-scrollbar-thumb { background: #e2e8f0; border-radius: 10px; }
</style>