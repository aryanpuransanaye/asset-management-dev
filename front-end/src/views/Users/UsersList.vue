<template>
  <div class="user-management-page container-fluid py-4" dir="rtl">
    <div class="d-flex justify-content-between align-items-center mb-4 px-2">
      <h3 class="fw-bold text-dark m-0">
        <i class="bi bi-people-fill me-2 text-primary"></i> مدیریت کاربران
      </h3>
      <button class="btn btn-primary rounded-pill px-4 shadow" @click="addUser">
        <i class="bi bi-plus-lg me-1"></i> ایجاد کاربر جدید
      </button>
    </div>

    <div class="glass-filter-card p-3 mb-4 shadow-sm">
      <div class="row g-3">
        <div class="col-lg-4 col-md-12">
          <div class="input-group">
            <span class="input-group-text bg-white border-0"><i class="bi bi-search"></i></span>
            <input v-model="search" @input="fetchUsers" class="form-control border-0 ps-0" placeholder="جستجو نام کاربری، ایمیل..."/>
          </div>
        </div>
        <div class="col-lg-2 col-md-4">
          <select v-model="sortBy" @change="fetchUsers" class="form-select border-0 shadow-none">
            <option value="">مرتب‌سازی</option>
            <option value="created_at">جدیدترین</option>
            <option value="-created_at">قدیمی‌ترین</option>
          </select>
        </div>
        <div class="col-lg-2 col-md-4">
          <select v-model="group" @change="fetchUsers" class="form-select border-0 shadow-none">
            <option value="">گروه: همه</option>
            <option v-for="g in groupsList" :key="g.id" :value="g.id">{{ g.name }}</option>
          </select>
        </div>
        <div class="col-lg-2 col-md-4">
          <select v-model="permission" @change="fetchUsers" class="form-select border-0 shadow-none">
            <option value="">مجوز: همه</option>
            <option v-for="p in permissionsList" :key="p.id" :value="p.id">{{ p.name }}</option>
          </select>
        </div>
        <div class="col-lg-2 col-md-12">
          <button class="btn btn-light w-100 border text-secondary" @click="resetFilters">
            پاکسازی فیلتر
          </button>
        </div>
      </div>
    </div>

    <div class="glass-table-card shadow-sm">
      <div class="table-responsive">
        <table class="table table-hover align-middle mb-0">
          <thead>
            <tr>
              <th class="text-center">#</th>
              <th>اطلاعات کاربر</th>
              <th>جنسیت</th>
              <th>تماس</th>
              <th>گروه‌ها</th>
              <th class="text-center">عملیات</th>
            </tr>
          </thead>
          <tbody v-if="!loading">
            <tr v-for="(user, index) in users" :key="user.id" class="user-row">
              <td class="text-center text-muted fw-bold">{{ index + 1 }}</td>
              <td>
                <div class="d-flex align-items-center">
                  <div class="avatar-box">
                    {{ user.username.charAt(0).toUpperCase() }}
                  </div>
                  <div class="user-info-text">
                    <div class="fw-bold text-dark">{{ user.username }}</div>
                    <small class="text-muted">{{ user.first_name }} {{ user.last_name }}</small>
                  </div>
                </div>
              </td>
              <td>
                <span v-if="user.gender === 'male'" class="badge-gender male">
                  <i class="bi bi-gender-male"></i> مرد
                </span>
                <span v-else-if="user.gender === 'female'" class="badge-gender female">
                  <i class="bi bi-gender-female"></i> زن
                </span>
                <span v-else-if="user.gender === 'other'" class="badge-gender other">
                  <i class="bi bi-gender-ambiguous"></i> سایر
                </span>
                <span v-else class="text-muted small">---</span>
              </td>
              <td>
                <div class="small fw-semibold text-dark">{{ user.email || 'بدون ایمیل' }}</div>
                <div class="small text-muted">{{ user.phone_number || 'بدون شماره' }}</div>
              </td>
              <td>
                <div class="badge-container">
                  <span v-for="g in user.groups" :key="g.id" class="badge bg-soft-primary me-1">{{ g.name }}</span>
                  <span v-if="!user.groups?.length" class="text-muted small">---</span>
                </div>
              </td>
              <td>
                <div class="d-flex justify-content-center gap-2">
                  <button class="btn-action edit" @click="editUser(user)" title="ویرایش">
                    <i class="bi bi-pencil-fill"></i>
                  </button>
                  <button class="btn-action info" @click="viewDetails(user)" title="جزئیات">
                    <i class="bi bi-eye-fill"></i>
                  </button>
                  <button class="btn-action delete" @click="deleteUser(user)" title="حذف">
                    <i class="bi bi-trash-fill"></i>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status"></div>
        <p class="mt-2 text-muted fw-bold">در حال دریافت اطلاعات...</p>
      </div>

      <div v-if="!loading && users.length === 0" class="text-center py-5 text-muted">
        <i class="bi bi-person-x fs-1 opacity-25"></i>
        <p class="mt-2">کاربری با این مشخصات پیدا نشد.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../api/axios'
import Swal from 'sweetalert2'
import { useRouter } from 'vue-router'

const router = useRouter()
const users = ref([])
const loading = ref(false)
const search = ref('')
const sortBy = ref('')
const group = ref('')
const permission = ref('')
const groupsList = ref([])
const permissionsList = ref([])

const fetchGroups = async () => {
  try {
    const res = await api.get('accounts/groups-list/')
    groupsList.value = res.data
  } catch (err) { console.error(err) }
}

const fetchPermissionsList = async () => {
  try {
    const res = await api.get('accounts/permissions-list/')
    permissionsList.value = res.data
  } catch (err) { console.error(err) }
}

const fetchUsers = async () => {
  loading.value = true
  try {
    const response = await api.get('accounts/users-list/', {
      params: { q: search.value, sort_by: sortBy.value, group: group.value || null, permission: permission.value || null }
    })
    users.value = response.data
  } catch (err) { console.error(err) } finally { loading.value = false }
}

const resetFilters = () => {
  search.value = ''; sortBy.value = ''; group.value = ''; permission.value = '';
  fetchUsers()
}

const addUser = () => router.push({ name: 'UserCreate' })
const editUser = (user) => router.push({ name: 'UserUpdate', params: { user_id: user.id } })
const viewDetails = (user) => router.push({ name: 'UserDetail', params: { user_id: user.id } })

const deleteUser = async (user) => {
  const result = await Swal.fire({
    title: 'حذف کاربر',
    text: `آیا از حذف "${user.username}" مطمئن هستید؟`,
    icon: 'warning',
    showCancelButton: true,
    confirmButtonColor: '#d33',
    confirmButtonText: 'بله، حذف شود',
    cancelButtonText: 'انصراف'
  })
  if (result.isConfirmed) {
    try {
      await api.delete(`accounts/user-detail/${user.id}/`)
      users.value = users.value.filter(u => u.id !== user.id)
      Swal.fire('موفق', 'کاربر با موفقیت حذف شد', 'success')
    } catch (err) { Swal.fire('خطا', 'مشکلی پیش آمد', 'error') }
  }
}

onMounted(async () => {
  await Promise.all([fetchGroups(), fetchPermissionsList()])
  fetchUsers()
})
</script>

<style scoped>
.glass-filter-card {
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.4);
}

.glass-table-card {
  background: white;
  border-radius: 20px;
  overflow: hidden;
  border: 1px solid rgba(0, 0, 0, 0.05);
}

thead th {
  background-color: #f8f9fa;
  color: #6c757d;
  font-size: 0.85rem;
  padding: 18px;
  border-bottom: 2px solid #f1f1f1;
}

.user-row:hover { background-color: #fcfdfe; }

/* آواتار */
.avatar-box {
  width: 42px;
  height: 42px;
  background: linear-gradient(135deg, #0d6efd, #0dcaf0);
  color: white;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  box-shadow: 0 4px 10px rgba(13, 110, 253, 0.2);
  margin-left: 15px; /* فاصله از متن سمت چپ در حالت RTL */
}

/* استایل جدید Badge جنسیت */
.badge-gender {
  padding: 5px 12px;
  border-radius: 50px;
  font-size: 0.75rem;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 5px;
}
.badge-gender.male { background: #e0f2fe; color: #0369a1; }
.badge-gender.female { background: #fdf2f8; color: #be185d; }
.badge-gender.other { background: #f1f5f9; color: #475569; }

/* دکمه‌های عملیات */
.btn-action {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: 0.3s;
}
.btn-action.edit { background: #eef2ff; color: #4338ca; }
.btn-action.info { background: #ecfdf5; color: #059669; }
.btn-action.delete { background: #fef2f2; color: #dc2626; }
.btn-action:hover { transform: translateY(-3px); box-shadow: 0 4px 8px rgba(0,0,0,0.1); }

.bg-soft-primary { background-color: #e0e7ff; color: #4338ca; }
.badge { padding: 6px 10px; border-radius: 6px; }
</style>