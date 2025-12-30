<template>
    <div class="p-4" dir="rtl">
      <h2 class="text-xl font-bold mb-4">مدیریت سازمان‌ها و زیرمجموعه‌ها</h2>
  
      <div class="mb-6 p-4 border rounded bg-gray-50">
        <label class="block mb-2 font-semibold">انتخاب سازمان اصلی:</label>
        <select 
          v-model="selectedOrgId" 
          @change="loadSubOrganizations"
          class="w-full p-2 border rounded"
        >
          <option :value="null">یک سازمان را انتخاب کنید...</option>
          <option v-for="org in organizations" :key="org.id" :value="org.id">
            {{ org.name }}
          </option>
        </select>
      </div>
  
      <div v-if="selectedOrgId" class="mt-4">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-medium">زیرمجموعه‌های این سازمان:</h3>
          <button @click="showAddModal = true" class="bg-blue-600 text-white px-4 py-2 rounded">
            افزودن زیرمجموعه جدید +
          </button>
        </div>
  
        <table class="w-full text-right border-collapse border">
          <thead>
            <tr class="bg-gray-200">
              <th class="p-2 border">نام واحد</th>
              <th class="p-2 border">آدرس اختصاصی</th>
              <th class="p-2 border">عملیات</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="sub in subOrganizations" :key="sub.id">
              <td class="p-2 border">{{ sub.name }}</td>
              <td class="p-2 border">{{ sub.address || 'ثبت نشده' }}</td>
              <td class="p-2 border">
                <button @click="deleteSub(sub.id)" class="text-red-500">حذف</button>
              </td>
            </tr>
            <tr v-if="subOrganizations.length === 0">
              <td colspan="3" class="p-4 text-center text-gray-500">هیچ زیرمجموعه‌ای یافت نشد.</td>
            </tr>
          </tbody>
        </table>
      </div>
  
      <div v-if="showAddModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
        <div class="bg-white p-6 rounded shadow-lg w-96">
          <h3 class="mb-4 font-bold">افزودن زیرمجموعه جدید</h3>
          <input v-model="newSub.name" placeholder="نام واحد" class="w-full mb-2 p-2 border rounded" />
          <input v-model="newSub.address" placeholder="آدرس" class="w-full mb-4 p-2 border rounded" />
          <div class="flex justify-end gap-2">
            <button @click="showAddModal = false" class="px-4 py-2 border rounded">انصراف</button>
            <button @click="addSubOrganization" class="px-4 py-2 bg-green-600 text-white rounded">ذخیره</button>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
 import api from '@/api/axios'
  
  export default {
    data() {
      return {
        organizations: [],
        subOrganizations: [],
        selectedOrgId: null,
        showAddModal: false,
        newSub: {
          name: '',
          address: ''
        }
      };
    },
    mounted() {
      this.getOrganizations();
    },
    methods: {
      // دریافت لیست سازمان‌ها برای دراپ‌دان
      async getOrganizations() {
        try {
          const res = await api.get('organization/organization/list/'); 
          this.organizations = res.data;
        } catch (e) { console.error("Error loading organizations"); }
      },
  
      // دریافت زیرمجموعه‌ها بر اساس ID سازمان (مطابق ویوی SubOrganizationListAPIView تو)
      async loadSubOrganizations() {
        if (!this.selectedOrgId) return;
        try {
          const res = await api.get(`organization/sub-organization/list/${this.selectedOrgId}/`);
          this.subOrganizations = res.data;
        } catch (e) { console.error("Error loading subs"); }
      },
  
      // افزودن زیرمجموعه جدید (مطابق متد post در SubOrganizationAPIView تو)
      async addSubOrganization() {
        try {
          const payload = {
            ...this.newSub,
            organization: this.selectedOrgId // آیدی سازمان پدر را میفرستیم
          };
          await axios.post('organization/sub-organization/', payload);
          this.showAddModal = false;
          this.newSub = { name: '', address: '' };
          this.loadSubOrganizations(); // لیست را بروز کن
        } catch (e) { alert("خطا در ثبت"); }
      },
  
      // حذف (مطابق متد delete در SubOrganizationAPIView تو که لیست IDs میگیرد)
      async deleteSub(id) {
        if (!confirm("مطمئنی؟")) return;
        try {
          await axios.delete('sub-organization/', { data: { ids: [id] } });
          this.loadSubOrganizations();
        } catch (e) { console.error("Delete failed"); }
      }
    }
  };
  </script>