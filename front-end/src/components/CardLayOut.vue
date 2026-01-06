<template>
    <div class="row g-3 px-2">
      <div v-for="(item, index) in items" :key="index" class="col-12 col-sm-6 col-xl-3">
        <div class="card h-100 shadow-sm border-0 rounded-3 hover-shadow transition-all">
          <div class="card-body p-3">
            <div class="d-flex align-items-center justify-content-between">
              <div class="d-flex align-items-center gap-3">
                <div 
                  :class="['rounded-pill']" 
                  :style="{ backgroundColor: getValidColor(item.color), width: '5px', height: '45px' }"
                ></div>
                
                <div>
                  <p class="text-secondary mb-1 small fw-bold">{{ item.label }}</p>
                  <h4 class="mb-0 fw-bold" :style="{ color: getValidColor(item.color) }">
                    {{ item.value }}
                  </h4>
                </div>
              </div>
              
              <div class="opacity-25">
                <i class="bi bi-layers-fill fs-3"></i>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  const props = defineProps({
    items: {
      type: Array,
      required: true,
      default: () => []
    }
  });
  
  // تابعی برای اطمینان از اینکه رنگ‌ها درست نمایش داده می‌شوند
  const getValidColor = (color) => {
    const colorMap = {
      purple: '#6f42c1',
      red: '#dc3545',
      green: '#198754',
      orange: '#fd7e14',
      blue: '#0d6efd'
    };
    return colorMap[color] || color || '#6c757d';
  };
  </script>
  
  <style scoped>
  .transition-all {
    transition: all 0.3s ease;
  }
  .hover-shadow:hover {
    transform: translateY(-5px);
    shadow: 0 .5rem 1rem rgba(0,0,0,.15)!important;
  }
  .card {
    background: #ffffff;
  }
  </style>