<template>
  <div class="card shadow-sm p-4 text-end" dir="rtl">
    <h5 class="mb-4 text-primary border-bottom pb-2">{{ title }}</h5>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary"></div>
      <p class="mt-2 text-muted small">در حال بارگذاری اطلاعات...</p>
    </div>

    <form v-else @submit.prevent="handleSubmit">
      <div class="row">
        <div 
          v-for="field in formConfig" 
          :key="field.key" 
          :class="field.type === 'TextField' ? 'col-12' : 'col-md-6'"
          class="mb-3"
        >
          <label class="form-label fw-bold small">
            {{ field.label }}
            <span v-if="field.required" class="text-danger">*</span>
          </label>

          <select 
            v-if="field.type === 'ChoiceField' || field.type === 'ForeignKey'" 
            v-model="formData[field.key]" 
            class="form-select border-primary-subtle"
            :required="field.required"
            @change="handleFieldChange(field.key)"
            :disabled="field.key === 'sub_organization' && !formData.organization"
          >
            <option :value="null">
              {{ getPlaceholder(field) }}
            </option>
            
            <option 
              v-for="opt in getOptions(field)" 
              :key="opt.value" 
              :value="opt.value"
            >
              {{ opt.label }}
            </option>
          </select>

          <input 
            v-else 
            v-model="formData[field.key]" 
            :type="getInputType(field.type)" 
            class="form-control border-primary-subtle"
            :required="field.required"
          />
          
          <div v-if="backendErrors[field.key]" class="text-danger small mt-1">
            {{ backendErrors[field.key][0] }}
          </div>
        </div>
      </div>

      <div class="d-flex justify-content-start mt-4 border-top pt-3">
        <button type="submit" class="btn btn-primary px-5" :disabled="submitting">
          <span v-if="submitting" class="spinner-border spinner-border-sm me-1"></span>
          ذخیره تغییرات
        </button>
        <button type="button" class="btn btn-outline-secondary ms-2" @click="$emit('cancel')">
          انصراف
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '@/api/axios';

const props = defineProps({
  hardwareId: {
    type: [Number, String],
    default: null
  }
});

const emit = defineEmits(['success', 'cancel']);

const formData = ref({});
const formConfig = ref([]);
const backendErrors = ref({});
const loading = ref(true);
const submitting = ref(false);
const title = ref('ثبت تجهیز جدید');

// تابع جدید برای مدیریت متن راهنمای منوها
const getPlaceholder = (field) => {
  if (field.key === 'sub_organization' && !formData.value.organization) {
    return 'ابتدا سازمان را انتخاب کنید...';
  }
  return 'انتخاب کنید...';
};

const handleFieldChange = (key) => {
  if (key === 'organization') {
    formData.value.sub_organization = null;
  }
};

const getOptions = (field) => {
  if (field.key === 'sub_organization') {
    if (!formData.value.organization) return [];
    return (field.options || []).filter(opt => opt.parent_id === formData.value.organization);
  }
  return field.options || [];
};

const getInputType = (type) => {
  const types = {
    'IntegerField': 'number',
    'DateTimeField': 'datetime-local',
    'DateField': 'date'
  };
  return types[type] || 'text';
};

const initForm = async () => {
  loading.value = true;
  try {
    const url = props.hardwareId 
      ? `asset/data-and-information/${props.hardwareId}/` 
      : `asset/data-and-information/`;
    
    const response = await api.get(url);
    formConfig.value = response.data.config_form;
    formData.value = response.data.result || {};
    
    if (props.hardwareId) {
      title.value = 'ویرایش تجهیز';
    }
  } catch (err) {
    console.error("خطا در لود فرم:", err);
  } finally {
    loading.value = false;
  }
};

const handleSubmit = async () => {
  submitting.value = true;
  backendErrors.value = {};
  
  try {
    const url = props.hardwareId 
      ? `asset/data-and-information/${props.hardwareId}/` 
      : `asset/data-and-information/`;
    
    if (props.hardwareId) {
      await api.patch(url, formData.value);
    } else {
      await api.post(url, formData.value);
    }
    emit('success');
  } catch (err) {
    if (err.response && err.response.data) {
      backendErrors.value = err.response.data;
    }
  } finally {
    submitting.value = false;
  }
};

onMounted(initForm);
</script>