<template>
  <div class="p-4" dir="rtl">
    <div class="card shadow-sm border-0 mb-4 bg-light">
      <div class="card-body">
        <h6 class="mb-3 fw-bold text-secondary text-end">
          <i class="bi bi-funnel-fill"></i> فیلترهای جستجو و عملیات
        </h6>
        
        <div class="row g-3">
          <div class="col-md-4">
            <input 
              v-model="queryParams.q" 
              type="text" 
              class="form-control" 
              :placeholder="(metadata.display_names?.q || 'جستجو') + '...'"
              @keyup.enter="fetchData"
            />
          </div>

          <template v-for="(label, key) in metadata.display_names" :key="key">
            <div 
              v-if="!['q', 'organization', 'sub_organization'].includes(key)" 
              class="col-md-2"
            >
              <select v-model="queryParams[key]" class="form-select" @change="fetchData">
                <option :value="null">{{ label }} (همه)</option>
                <template v-if="metadata[key] && Array.isArray(metadata[key])">
                  <option 
                    v-for="item in metadata[key].filter(i => i !== null)" 
                    :key="item.id || item.value || item" 
                    :value="item.id !== undefined ? item.id : (item.value !== undefined ? item.value : item)"
                  >
                    {{ item.name || item.label || item }}
                  </option>
                </template>
              </select>
            </div>
          </template>

          <div class="col-md-2" v-if="metadata.display_names?.organization">
            <select v-model="queryParams.organization" class="form-select" @change="handleOrgChange">
              <option :value="null">{{ metadata.display_names.organization }} (همه)</option>
              <template v-if="metadata.organization">
                <option v-for="item in metadata.organization.filter(i => i !== null)" :key="item.id" :value="item.id">
                  {{ item.name }}
                </option>
              </template>
            </select>
          </div>

          <div class="col-md-2" v-if="metadata.display_names?.sub_organization">
            <select 
              v-model="queryParams.sub_organization" 
              class="form-select" 
              @change="fetchData"
              :disabled="!queryParams.organization"
            >
              <option :value="null">{{ metadata.display_names.sub_organization }} (همه)</option>
              <option v-for="item in filteredSubOrgs" :key="item.id" :value="item.id">
                {{ item.name }}
              </option>
            </select>
          </div>
        </div>

        <div class="d-flex justify-content-end mt-3 gap-2">
          <button @click="exportData" class="btn btn-outline-success btn-sm px-3 shadow-sm" :disabled="loading">
            <i class="bi bi-file-earmark-excel-fill"></i> خروجی اکسل
          </button>
          
          <button @click="resetFilters" class="btn btn-outline-secondary btn-sm px-3">حذف فیلترها</button>
          
          <button @click="fetchData" class="btn btn-primary btn-sm px-4 shadow-sm">
            <i class="bi bi-search"></i> اعمال جستجو
          </button>
        </div>
      </div>
    </div>

    <div class="table-responsive shadow-sm rounded border bg-white" style="max-height: 70vh;">
      <table class="table table-hover mb-0 text-end">
        <thead class="table-light text-nowrap sticky-top">
          <tr>
            <th 
              v-for="col in columns" 
              :key="col.key" 
              class="py-3 text-secondary small fw-bold"
              style="cursor: pointer; user-select: none;"
              @click="handleSort(col.key)"
            >
              <div class="d-flex align-items-center gap-1 justify-content-start">
                {{ col.label }}
                <span v-if="sortState.key === col.key" class="text-primary">
                  <i v-if="sortState.order === 'asc'" class="bi bi-sort-up"></i>
                  <i v-else class="bi bi-sort-down"></i>
                </span>
                <span v-else class="text-muted opacity-25">
                  <i class="bi bi-arrow-down-up" style="font-size: 0.7rem;"></i>
                </span>
              </div>
            </th>
            <th class="text-center text-secondary small fw-bold">عملیات</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td :colspan="columns?.length + 1" class="text-center py-5">
              <div class="spinner-border spinner-border-sm text-primary"></div>
              <span class="ms-2">در حال دریافت اطلاعات...</span>
            </td>
          </tr>

          <template v-else>
            <tr v-for="row in items" :key="row.id">
              <td v-for="col in columns" :key="col.key" class="small align-middle text-nowrap">
                {{ (row[col.key] !== null && row[col.key] !== '') ? row[col.key] : '---' }}
              </td>
              <td class="text-center align-middle">
                <button 
                  class="btn btn-sm btn-link text-primary p-0 mx-1 text-decoration-none" 
                  @click="$emit('edit', row.id)"
                >
                  ویرایش
                </button>
              </td>
            </tr>
            
            <tr v-if="items.length === 0">
              <td :colspan="columns?.length + 1" class="text-center py-5 text-muted small">
                اطلاعاتی یافت نشد.
              </td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue';
import api from '@/api/axios';

/** ۱. تعریف حالت‌های واکنش‌گرا (State) **/
const items = ref([]); 
const columns = ref([]);
const loading = ref(false);
const metadata = ref({ display_names: {} });
const queryParams = reactive({});

// وضعیت مرتب‌سازی (Sort)
const sortState = reactive({
  key: null,
  order: 'asc'
});

/** ۲. منطق وابستگی زیرسازمان‌ها **/
const filteredSubOrgs = computed(() => {
  if (!queryParams.organization || !metadata.value.sub_organization) return [];
  return metadata.value.sub_organization.filter(
    sub => sub !== null && sub.organization_id === queryParams.organization
  );
});

/** ۳. متد دریافت اطلاعات از سرور (Fetch Data) **/
const fetchData = async () => {
  loading.value = true;
  try {
    const cleanParams = {};
    Object.keys(queryParams).forEach(key => {
      if (queryParams[key] !== null && queryParams[key] !== '') {
        cleanParams[key] = queryParams[key];
      }
    });
    
    const response = await api.get('asset/data-and-information/list/', { params: cleanParams });
    items.value = response.data.results || [];
    columns.value = response.data.columns || [];
  } catch (error) {
    console.error("خطا در دریافت لیست:", error);
  } finally {
    setTimeout(() => { loading.value = false; }, 50);
  }
};

/** ۴. مدیریت مرتب‌سازی ستون‌ها **/
const handleSort = (key) => {
  if (sortState.key === key) {
    sortState.order = sortState.order === 'asc' ? 'desc' : 'asc';
  } else {
    sortState.key = key;
    sortState.order = 'asc';
  }
  
  // مقداردهی پارامتر سورت برای ارسال به API
  queryParams.sort_by = sortState.order === 'desc' ? `-${key}` : key;
  fetchData();
};

/** ۵. متد خروجی اکسل (Export) **/
const exportData = async () => {
  try {
    const cleanParams = {};
    Object.keys(queryParams).forEach(key => {
      if (queryParams[key] !== null && queryParams[key] !== '') {
        cleanParams[key] = queryParams[key];
      }
    });

    // درخواست فایل به صورت Blob
    const response = await api.get('asset/data-and-information/export/', { 
      params: cleanParams,
      responseType: 'blob' 
    });

    // ساخت لینک دانلود در مرورگر
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `data-and-information_Export_${new Date().toLocaleDateString('fa-IR')}.xlsx`);
    document.body.appendChild(link);
    link.click();
    link.remove();
  } catch (error) {
    console.error("خطا در دانلود اکسل:", error);
  }
};

/** ۶. متد دریافت اطلاعات اولیه فیلترها **/
const fetchMetadata = async () => {
  try {
    const response = await api.get('asset/data-and-information/metadata/');
    metadata.value = response.data || { display_names: {} };
    
    if (metadata.value.display_names) {
      Object.keys(metadata.value.display_names).forEach(key => {
        if (!(key in queryParams)) {
          queryParams[key] = key === 'q' ? '' : null;
        }
      });
    }
  } catch (error) {
    console.error("خطا در دریافت متادیتا:", error);
  }
};

/** ۷. سایر متدهای کمکی **/
const handleOrgChange = () => {
  if ('sub_organization' in queryParams) queryParams.sub_organization = null;
  fetchData();
};

const resetFilters = () => {
  sortState.key = null;
  sortState.order = 'asc';
  Object.keys(queryParams).forEach(key => {
    queryParams[key] = key === 'q' ? '' : null;
  });
  fetchData();
};

onMounted(async () => {
  await fetchMetadata();
  await fetchData();
});
</script>

<style scoped>
.sticky-top {
  z-index: 10;
  background-color: #f8f9fa !important;
}

th:hover {
  background-color: #f1f1f1;
}

/* راست‌چین کردن محتویات جدول برای زبان فارسی */
.table th, .table td {
  text-align: right !important;
}
</style>