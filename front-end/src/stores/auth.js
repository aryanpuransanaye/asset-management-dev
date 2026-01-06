import { defineStore } from 'pinia';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: null,
    userPermissions: [],
    user: null,
  }),
  
  actions: {
    saveLoginData(token, permissions, userData) {
      this.token = token;
      this.userPermissions = permissions;
      this.user = userData;
      // نکته: اگر persist فعال باشد، نیازی به setItem دستی نیست، 
      // اما برای اطمینان بیشتر (مثلاً برای استفاده در Axios قبل از لود پینیا) می‌توانید بگذارید بماند.
      localStorage.setItem('access_token', token);
    },

    logout() {
      this.token = null;
      this.userPermissions = [];
      this.user = null;
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    }
  },
  
  getters: {
    
    isAdmin: (state) => {
        return state.user?.is_superuser || state.user?.is_staff || state.userPermissions.includes('*');
    },
    
    canSeeAssets: (state) => (asset_name) => {
      // ۱. اول چک کردن ادمین (مستقیماً از روی استیت برای اطمینان)
      if (state.isAdmin) return true;
    
      // ۲. چک کردن پرمیشن‌های خاص
      const prefix = asset_name;
      // حتماً چک کن که userPermissions وجود داشته باشد که ارور undefined نگیری
      const perms = state.userPermissions || []; 

      const hasR = perms.includes(`accounts.${prefix}_r`);
      const hasCrud = perms.includes(`accounts.${prefix}_crud`);

      return hasR || hasCrud;
    },

    // اصلاح شده برای پشتیبانی از "*" و فلگ‌های ادمین
    hasPermission: (state) => (permission) => {
        // ۱. چک کردن ستاره (خروجی جدید بک‌اِند تو برای سوپریوزر)
        if (state.userPermissions.includes('*')) return true;

        // ۲. چک کردن فلگ‌های ادمین
        if (state.user?.is_superuser || state.user?.is_staff) return true;

        // ۳. چک کردن پرمیشن خاص
        return state.userPermissions.includes(permission);
    },
    
  },

  persist: true, // حتماً مطمئن شو پلاگین مربوطه را در main.js نصب کرده‌ای
});