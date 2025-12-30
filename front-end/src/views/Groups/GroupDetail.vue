<template>
  <div class="group-detail-page container py-5" dir="rtl">
    <div class="d-flex justify-content-between align-items-center mb-4 max-w-900 mx-auto px-2">
      <h3 class="fw-bold text-dark m-0">
        <i class="bi bi-info-square-fill me-2 text-primary"></i> شناسنامه گروه
      </h3>
      <div class="d-flex gap-2">
        <button class="btn btn-warning border-0 rounded-pill px-3 shadow-sm fw-bold text-dark" 
                @click="$router.push({ name: 'GroupUpdate', params: { group_id: groupID } })">
          <i class="bi bi-pencil-square me-1"></i> ویرایش
        </button>
        
        <button class="btn btn-light border rounded-pill px-3 shadow-sm" @click="$router.back()">
          <i class="bi bi-arrow-right me-1"></i> بازگشت
        </button>
      </div>
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" style="width: 3rem; height: 3rem;"></div>
      <p class="mt-3 text-muted">در حال فراخوانی اطلاعات گروه...</p>
    </div>

    <div v-else class="max-w-900 mx-auto">
      <div class="glass-card info-banner shadow-sm mb-4 overflow-hidden">
        <div class="d-flex align-items-center p-4">
          <div class="group-avatar-box me-4">
            <i class="bi bi-collection"></i>
          </div>
          <div class="flex-grow-1">
            <h2 class="fw-black text-dark mb-1">{{ group.name }}</h2>
            <div class="d-flex gap-3 mt-2">
              <span class="badge bg-soft-primary text-primary rounded-pill px-3">
                <i class="bi bi-people me-1"></i> {{ group.custom_user_set?.length || 0 }} کاربر عضو
              </span>
              <span class="badge bg-soft-warning text-warning-dark rounded-pill px-3">
                <i class="bi bi-shield-check me-1"></i> {{ group.group_permissions?.length || 0 }} مجوز فعال
              </span>
            </div>
          </div>
        </div>
      </div>

      <div class="glass-card shadow-sm mb-4 p-4">
        <h5 class="fw-bold mb-3 text-secondary">
          <i class="bi bi-shield-lock-fill me-2 text-warning"></i> مجوزهای سطح گروه
        </h5>
        <div v-if="group.group_permissions?.length" class="d-flex flex-wrap gap-2">
          <span v-for="perm in group.group_permissions" :key="perm.id" class="modern-tag">
            <i class="bi bi-key-fill me-1 opacity-50"></i> {{ perm.name }}
          </span>
        </div>
        <div v-else class="text-muted small italic p-2 bg-light rounded">
          هیچ مجوز مستقیمی برای این گروه تعریف نشده است.
        </div>
      </div>

      <div class="glass-card shadow-lg border-0">
        <div class="p-4 border-bottom d-flex justify-content-between align-items-center bg-light-subtle">
          <h5 class="fw-bold m-0 text-secondary">
            <i class="bi bi-person-badge me-2"></i> لیست کاربران این گروه
          </h5>
        </div>

        <div class="card-body p-0">
          <div v-if="group.custom_user_set?.length" class="table-responsive">
            <table class="table table-hover mb-0 align-middle">
              <thead>
                <tr>
                  <th class="py-3 text-muted small fw-bold text-center">#</th>
                  <th class="py-3 text-muted small fw-bold text-end px-4">نام کاربری</th>
                  <th class="py-3 text-muted small fw-bold text-center">پست الکترونیک</th>
                  <th class="py-3 text-muted small fw-bold text-center">عملیات</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(user, index) in group.custom_user_set" :key="user.id" class="animate-in">
                  <td class="text-muted small text-center">{{ index + 1 }}</td>
                  <td class="text-end px-4">
                    <div class="d-inline-flex align-items-center flex-row-reverse">
                      <div class="user-meta text-end">
                        <span class="fw-bold text-dark d-block">{{ user.username }}</span>
                        <small class="text-muted x-small d-block">شناسه: {{ user.id }}</small>
                      </div>
                      <div class="mini-avatar me-3">
                        {{ user.username.charAt(0).toUpperCase() }}
                      </div>
                    </div>
                  </td>
                  <td class="text-center">
                    <span class="text-secondary small">{{ user.email || '---' }}</span>
                  </td>
                  <td class="text-center">
                    <button class="btn btn-sm btn-light border rounded-pill px-3" @click="goToUser(user.id)">
                      مشاهده پروفایل
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div v-else class="empty-state text-center py-5">
            <div class="empty-icon mb-3">
              <i class="bi bi-person-x display-4 text-muted opacity-25"></i>
            </div>
            <p class="text-muted">هیچ کاربری هنوز عضو این گروه نشده است.</p>
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

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const group = ref({
  id: null,
  name: '',
  custom_user_set: [],
  permissions: [] // اضافه شدن فیلد پرمیشن‌ها
})

const groupID = route.params.group_id

const fetchGroupDetail = async () => {
  loading.value = true
  try {
    const res = await api.get(`accounts/group-detail/${groupID}/`)
    group.value = res.data
  } catch (err) {
    console.error('Error:', err)
  } finally {
    loading.value = false
  }
}

const goToUser = (userId) => {
  router.push({ name: 'UserDetail', params: { user_id: userId } })
}

onMounted(fetchGroupDetail)
</script>

<style scoped>
.max-w-900 { max-width: 900px; }
.fw-black { font-weight: 900; }
.x-small { font-size: 0.7rem; }

/* کارت شیشه‌ای */
.glass-card {
  background: white;
  border-radius: 20px;
  border: 1px solid #f1f5f9;
}

.info-banner {
  background: linear-gradient(to left, #ffffff, #f8fafc);
  border-right: 5px solid #0d6efd;
}

/* آیکون گروه */
.group-avatar-box {
  width: 70px;
  height: 70px;
  background: #f0f7ff;
  color: #0d6efd;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
}

/* تگ‌های مدرن برای مجوزها */
.modern-tag {
  background: #fff9eb;
  color: #b45309;
  border: 1px solid #fef3c7;
  padding: 6px 12px;
  border-radius: 10px;
  font-size: 0.85rem;
  font-weight: 600;
}

/* آواتار کوچک کاربر */
.mini-avatar {
  width: 32px;
  height: 32px;
  background: #e2e8f0;
  color: #64748b;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  font-weight: bold;
  margin-left: 10px;
}

/* استایل جدول */
.table thead th {
  background-color: #f8fafc;
}

.table tbody tr:hover {
  background-color: #f1f7ff;
}

.animate-in {
  animation: slideIn 0.3s ease forwards;
}

@keyframes slideIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.bg-soft-primary { background-color: #e0f2fe; }
.bg-soft-warning { background-color: #fffbeb; }
.text-warning-dark { color: #b45309; }
.italic { font-style: italic; }
</style>