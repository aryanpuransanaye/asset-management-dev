<template>
  <div class="p-4" dir="rtl">
    <div class="card shadow-sm border-0 mb-4 bg-light">
      <div class="card-body">
        <h6 class="mb-3 fw-bold text-secondary text-end">
          <i class="bi bi-funnel-fill"></i> فیلترهای جستجو و عملیات
        </h6>
        
        <div class="row g-3">
          <div class="col-md-4">
            <div class="input-group">
              <span class="input-group-text bg-white border-end-0">
                <i class="bi bi-search text-muted"></i>
              </span>
              <input 
                v-model="queryParams.q" 
                type="text" 
                class="form-control border-start-0" 
                :placeholder="(metadata.display_names?.q || 'جستجو...') + '...'"
              />
            </div>
          </div>

          <template v-for="(label, key) in metadata.display_names" :key="key">
            <div 
              v-if="!['q', 'organization', 'sub_organization', 'id', 'created_at', 'updated_at'].includes(key)" 
              class="col-md-2"
            >
              <select v-model="queryParams[key]" class="form-select" @change="handleFilterChange">
                <option :value="null">{{ label }} (همه)</option>
                <template v-if="metadata[key] && Array.isArray(metadata[key])">
                  <option 
                    v-for="item in metadata[key].filter(i => i && (i.id || i.value || i.name || i.label))" 
                    :key="item?.id || item?.value || item" 
                    :value="item?.id !== undefined ? item?.id : (item?.value !== undefined ? item?.value : item)"
                  >
                    {{ item?.name || item?.label || item }}
                  </option>
                </template>
              </select>
            </div>
          </template>

          <div class="col-md-2" v-if="metadata.display_names?.organization">
            <select v-model="queryParams.organization" class="form-select" @change="handleOrgChange">
              <option :value="null">{{ metadata.display_names.organization }} (همه)</option>
              <option v-for="item in (metadata.organization || [])" :key="item?.id" :value="item?.id">
                {{ item?.name }}
              </option>
            </select>
          </div>

          <div class="col-md-2" v-if="metadata.display_names?.sub_organization">
            <select 
              v-model="queryParams.sub_organization" 
              class="form-select" 
              @change="handleFilterChange"
              :disabled="!queryParams.organization"
            >
              <option :value="null">{{ metadata.display_names.sub_organization }} (همه)</option>
              <option v-for="item in filteredSubOrgs" :key="item?.id" :value="item?.id">
                {{ item?.name }}
              </option>
            </select>
          </div>
        </div>

        <div class="d-flex justify-content-between align-items-center mt-4">
          <div class="d-flex gap-2">
            <button v-if="crud" @click="goToCreatePage" class="btn btn-primary btn-sm px-3 shadow-sm">
              <i class="bi bi-plus-lg"></i> افزودن رکورد جدید
            </button>
            <button v-if="crud && selectedIds.length > 0" @click="handleDelete()" class="btn btn-danger btn-sm px-3 shadow-sm">
              <i class="bi bi-trash-fill"></i> حذف گروهی ({{ selectedIds.length }})
            </button>
          </div>
          <div class="d-flex gap-2">
            <button @click="exportData" class="btn btn-outline-success btn-sm px-3 shadow-sm" :disabled="loading">
              <i class="bi bi-file-earmark-excel-fill"></i> خروجی اکسل
            </button>
            <button @click="resetFilters" class="btn btn-outline-secondary btn-sm px-3">حذف فیلترها</button>
          </div>
        </div>
      </div>
    </div>

    <div class="table-responsive shadow-sm rounded border bg-white" style="max-height: 65vh;">
      <table class="table table-hover mb-0 text-end">
        <thead class="table-light text-nowrap sticky-top">
          <tr>
            <th class="text-center align-middle" style="width: 45px;">
              <input type="checkbox" class="form-check-input" :checked="isAllSelected" @change="toggleSelectAll" />
            </th>
            <th 
              v-for="col in columns.filter(c => c.key !== 'id')" 
              :key="col.key" 
              class="py-3 text-secondary small fw-bold"
              style="cursor: pointer; user-select: none;"
              @click="handleSort(col.key)"
            >
              <div class="d-flex align-items-center gap-1">
                {{ metadata.display_names?.[col.key] || col.label || col.key }}
                <span v-if="sortState.key === col.key" class="text-primary">
                  <i :class="sortState.order === 'asc' ? 'bi bi-sort-up' : 'bi bi-sort-down'"></i>
                </span>
              </div>
            </th>
            <th v-if="crud" class="text-center text-secondary small fw-bold">عملیات</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td :colspan="columns.length + 2" class="text-center py-5">
              <div class="spinner-border spinner-border-sm text-primary"></div>
              <span class="ms-2 text-primary">در حال بروزرسانی لیست...</span>
            </td>
          </tr>

          <template v-else>
            <tr v-for="row in items" :key="row.id" :class="{'table-active': selectedIds.includes(row.id)}">
              <td class="text-center align-middle">
                <input type="checkbox" class="form-check-input" :value="row.id" v-model="selectedIds" />
              </td>
              <td v-for="col in columns.filter(c => c.key !== 'id')" :key="col.key" class="small align-middle text-nowrap">
                {{ (row[col.key] != null && String(row[col.key]).toLowerCase() !== 'none') ? row[col.key] : '-' }}
              </td>
              <td v-if="crud" class="text-center align-middle">
                <div class="d-flex justify-content-center gap-3">
                  <button class="btn btn-sm btn-link text-primary p-0 text-decoration-none" @click="goToUpdatePage(row.id)">ویرایش</button>
                  <button class="btn btn-sm btn-link text-danger p-0 text-decoration-none" @click="handleDelete(row.id)">حذف</button>
                </div>
              </td>
            </tr>
            <tr v-if="items.length === 0">
              <td :colspan="columns.length + 2" class="text-center py-5 text-muted small">اطلاعاتی یافت نشد.</td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>

    <div class="d-flex justify-content-between align-items-center mt-3">
      <div class="text-muted small">
        صفحه {{ queryParams.page }} از {{ totalPages }} (کل: {{ totalItems }})
      </div>
      <nav v-if="totalPages > 1">
        <ul class="pagination pagination-sm mb-0">
          <li class="page-item" :class="{ disabled: queryParams.page === 1 }">
            <button class="page-link" @click="changePage(queryParams.page - 1)">قبلی</button>
          </li>
          <li v-for="p in totalPages" :key="p" class="page-item" :class="{ active: p === queryParams.page }">
            <button class="page-link" @click="changePage(p)">{{ p }}</button>
          </li>
          <li class="page-item" :class="{ disabled: queryParams.page === totalPages }">
            <button class="page-link" @click="changePage(queryParams.page + 1)">بعدی</button>
          </li>
        </ul>
      </nav>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, watch } from 'vue';
import api from '@/api/axios';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();

const props = defineProps({
  apiEndpoint: { type: String, default: '' }
});

// --- منطق دسترسی‌ها ---
const modelPermissionKey = computed(() => {
  const nameFromQuery = route.query.permission_name;
  if (nameFromQuery) return nameFromQuery;
  const path = props.apiEndpoint || route.query.api || 'asset/data-and-information';
  return path.split('/').pop().replace(/-/g, '_'); 
});

const crud = computed(() => auth.hasPermission(`accounts.${modelPermissionKey.value}_crud`) || auth.isAdmin);

// --- متغیرها ---
const items = ref([]); 
const columns = ref([]);
const loading = ref(false);
const metadata = ref({ display_names: {} });
const selectedIds = ref([]);
const totalPages = ref(1);
const totalItems = ref(0);
let searchTimeout = null;

const queryParams = reactive({
  page: 1,
  q: '',
  sort_by: '-created_at'
});

const sortState = reactive({ key: null, order: 'asc' });

// --- توابع کمکی ---
const getCurrentApi = () => props.apiEndpoint || route.query.api;

const goToCreatePage = () => {
  router.push({ name: 'CreateAsset', query: { api: getCurrentApi() } });
};

const goToUpdatePage = (id) => {
  router.push({ name: 'CreateAsset', query: { api: getCurrentApi(), id: id } });
};

// --- مدیریت داده‌ها ---
const fetchData = async () => {
  loading.value = true;
  try {
    const params = {};
    Object.keys(queryParams).forEach(key => {
      if (queryParams[key] !== null && queryParams[key] !== '') params[key] = queryParams[key];
    });
    const response = await api.get(`${getCurrentApi()}/list/`, { params });
    items.value = response.data.results || [];
    columns.value = response.data.columns || [];
    totalPages.value = response.data.total_pages || 1;
    totalItems.value = response.data.total_items || 0;
  } catch (error) {
    console.error("Fetch error:", error);
  } finally {
    loading.value = false;
  }
};

const fetchMetadata = async () => {
  try {
    const response = await api.get(`${getCurrentApi()}/metadata/`);
    metadata.value = response.data || { display_names: {} };
    Object.keys(metadata.value.display_names || {}).forEach(key => {
      if (!(key in queryParams)) queryParams[key] = key === 'q' ? '' : null;
    });
  } catch (error) {
    console.error("Metadata error:", error);
  }
};

const handleDelete = async (id = null) => {
  const idsToDelete = id ? [id] : selectedIds.value;
  if (!idsToDelete.length || !confirm(id ? "حذف شود؟" : `${idsToDelete.length} مورد حذف شوند؟`)) return;

  try {
    await api.delete(`${getCurrentApi()}/`, { data: { ids: idsToDelete } });
    selectedIds.value = [];
    fetchData();
  } catch (error) {
    alert("خطا در حذف.");
  }
};

// --- واچرز و فیلترها ---
watch(() => [props.apiEndpoint, route.query.api], () => {
  resetFilters();
  fetchMetadata();
  fetchData();
});

watch(() => queryParams.q, () => {
  if (searchTimeout) clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => handleFilterChange(), 500);
});

const filteredSubOrgs = computed(() => {
  if (!queryParams.organization || !metadata.value.sub_organization) return [];
  return metadata.value.sub_organization.filter(sub => sub.organization_id === queryParams.organization);
});

const isAllSelected = computed(() => items.value.length > 0 && selectedIds.value.length === items.value.length);

const handleFilterChange = () => { queryParams.page = 1; fetchData(); };
const handleOrgChange = () => { queryParams.sub_organization = null; handleFilterChange(); };
const changePage = (p) => { queryParams.page = p; fetchData(); };
const toggleSelectAll = (e) => { selectedIds.value = e.target.checked ? items.value.map(i => i.id) : []; };

const handleSort = (key) => {
  sortState.order = (sortState.key === key && sortState.order === 'asc') ? 'desc' : 'asc';
  sortState.key = key;
  queryParams.sort_by = sortState.order === 'desc' ? `-${key}` : key;
  handleFilterChange();
};

const resetFilters = () => {
  // ۱. پاک کردن متن جستجو
  queryParams.q = '';

  // ۲. نال کردن تمام فیلترهای داینامیک (به جز صفحه و جستجو)
  Object.keys(queryParams).forEach(key => { 
    if (!['page', 'q'].includes(key)) queryParams[key] = null; 
  });

  // ۳. برگرداندن مرتب‌سازی به حالت پیش‌فرض (اختیاری اما توصیه می‌شود)
  queryParams.sort_by = '-created_at';
  sortState.key = null;
  sortState.order = 'asc';

  // ۴. مهم‌ترین بخش: برگرداندن به صفحه ۱ و فراخوانی مجدد داده‌ها
  queryParams.page = 1;
  fetchData(); 
};

const exportData = async () => {
  try {
    loading.value = true;
    const params = { ...queryParams }; delete params.page;
    const response = await api.get(`${getCurrentApi()}/export/`, { params, responseType: 'blob' });
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `${modelPermissionKey.value}_${new Date().toLocaleDateString('fa-IR')}.xlsx`);
    link.click();
  } catch (error) {
    alert("خطا در اکسل.");
  } finally {
    loading.value = false;
  }
};

onMounted(() => { fetchMetadata(); fetchData(); });
</script>

<style scoped>
.sticky-top { z-index: 10; background-color: #f8f9fa !important; }
th:hover { background-color: #f1f1f1; }
.table-active { background-color: rgba(13, 110, 253, 0.05) !important; }
.table th, .table td { text-align: right !important; }
.input-group-text { border-radius: 0 0.375rem 0.375rem 0 !important; }
input.form-control { border-radius: 0.375rem 0 0 0.375rem !important; }
</style>