<template>
  <div class="groups-list-page container py-5" dir="rtl">
    <div class="d-flex justify-content-between align-items-center mb-5">
      <div>
        <h3 class="fw-bold text-dark m-0">
          <i class="bi bi-collection-play-fill me-2 text-primary"></i> مدیریت گروه‌های کاربری
        </h3>
        <p class="text-muted small mt-1">لیست گروه‌ها، سطوح دسترسی و اعضای سیستم</p>
      </div>
      <button class="btn btn-primary-gradient rounded-pill px-4 py-2 shadow-sm fw-bold" @click="createGroup">
        <i class="bi bi-plus-lg me-1"></i> ایجاد گروه جدید
      </button>
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-grow text-primary" role="status"></div>
      <p class="mt-3 text-muted">در حال چیدمان گروه‌ها...</p>
    </div>

    <div v-if="!loading && groups.length" class="row g-4">
      <div v-for="group in groups" :key="group.id" class="col-xl-4 col-md-6">
        <div class="glass-group-card shadow-sm animate-in">
          <div class="card-content">
            <div class="d-flex justify-content-between align-items-start mb-3">
              <div class="group-icon-box">
                <i class="bi bi-people-fill"></i>
              </div>
              <div class="dropdown">
                <button class="btn btn-link text-muted p-0" data-bs-toggle="dropdown">
                  <i class="bi bi-three-dots-vertical"></i>
                </button>
                <ul class="dropdown-menu dropdown-menu-end shadow border-0">
                  <li><a class="dropdown-item small" @click="editGroup(group)"><i class="bi bi-pencil me-2"></i>ویرایش</a></li>
                  <li><a class="dropdown-item small text-danger" @click="deleteGroup(group)"><i class="bi bi-trash me-2"></i>حذف گروه</a></li>
                </ul>
              </div>
            </div>

            <h5 class="fw-bold text-dark mb-1">{{ group.name }}</h5>
            <div class="badge bg-soft-primary text-primary mb-4">شناسه: #{{ group.id }}</div>

            <div class="stats-row d-flex gap-3 mb-4">
              <div class="stat-item flex-fill">
                <span class="label">کاربران</span>
                <span class="value">{{ group.users_count }}</span>
              </div>
              <div class="stat-item flex-fill border-start ps-3">
                <span class="label">دسترسی‌ها</span>
                <span class="value text-warning-dark">{{ group.permissions_count }}</span>
              </div>
            </div>

            <button class="btn btn-outline-primary w-100 rounded-pill btn-sm fw-bold" @click="viewDetails(group)">
              مشاهده جزئیات و اعضا
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="!loading && groups.length === 0" class="empty-state text-center py-5 glass-group-card">
      <i class="bi bi-folder2-open display-1 text-muted opacity-25"></i>
      <h5 class="mt-3 text-muted">هنوز هیچ گروهی تعریف نشده است</h5>
      <button class="btn btn-link text-primary mt-2" @click="createGroup">اولین گروه را بسازید</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../api/axios'
import Swal from 'sweetalert2'
import { useRouter } from 'vue-router'

const router = useRouter()
const groups = ref([])
const loading = ref(false)

const fetchGroups = async () => {
  loading.value = true
  try {
    const res = await api.get('accounts/groups-list/')
    groups.value = res.data
  } catch (err) {
    Swal.fire('خطا', 'دریافت اطلاعات با شکست مواجه شد', 'error')
  } finally {
    loading.value = false
  }
}

const viewDetails = (group) => router.push({ name: 'GroupDetail', params: { group_id: group.id } })
const editGroup = (group) => router.push({ name: 'GroupUpdate', params: { group_id: group.id } })
const createGroup = () => router.push({ name: 'GroupCreate' })

const deleteGroup = async (group) => {
  const result = await Swal.fire({
    title: `حذف گروه "${group.name}"؟`,
    text: "این عمل قابل بازگشت نیست و دسترسی کاربران این گروه تغییر خواهد کرد.",
    icon: 'warning',
    showCancelButton: true,
    confirmButtonColor: '#dc3545',
    confirmButtonText: 'بله، حذف کن',
    cancelButtonText: 'انصراف'
  })

  if (result.isConfirmed) {
    try {
      await api.delete(`accounts/group-detail/${group.id}/`)
      groups.value = groups.value.filter(g => g.id !== group.id)
      Swal.fire('حذف شد', 'گروه با موفقیت از سیستم حذف شد.', 'success')
    } catch (err) {
      Swal.fire('خطا', 'مشکلی در حذف گروه پیش آمد.', 'error')
    }
  }
}

onMounted(fetchGroups)
</script>

<style scoped>
/* کارت شیشه‌ای مدرن */
.glass-group-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 24px;
  border: 1px solid rgba(255, 255, 255, 0.5);
  padding: 25px;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.glass-group-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1) !important;
  border-color: #0d6efd44;
}

/* باکس آیکون */
.group-icon-box {
  width: 50px;
  height: 50px;
  background: linear-gradient(135deg, #0d6efd 0%, #00d4ff 100%);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.5rem;
  box-shadow: 0 8px 15px rgba(13, 110, 253, 0.2);
}

/* آیتم‌های آماری */
.stat-item .label {
  display: block;
  font-size: 0.7rem;
  color: #94a3b8;
  text-transform: uppercase;
  font-weight: 800;
  margin-bottom: 2px;
}

.stat-item .value {
  font-size: 1.25rem;
  font-weight: 900;
  color: #1e293b;
}

/* رنگ‌های ملایم */
.bg-soft-primary { background-color: #e0f2fe; }
.text-warning-dark { color: #b45309; }

/* دکمه گرادینت */
.btn-primary-gradient {
  background: linear-gradient(135deg, #0d6efd 0%, #00d4ff 100%);
  border: none;
  color: white;
  transition: 0.3s;
}

.animate-in {
  animation: fadeInScale 0.4s ease-out forwards;
}

@keyframes fadeInScale {
  from { opacity: 0; transform: scale(0.9); }
  to { opacity: 1; transform: scale(1); }
}

.dropdown-item:active {
  background-color: #0d6efd;
}
</style>