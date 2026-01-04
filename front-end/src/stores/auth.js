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

    canSeeAssets: (state) => {
      if (state.user?.is_staff) return true;

      return state.userPermissions.some(p =>
        p.includes('_crud') || p.includes('_r')
      )
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
    
    isAdmin: (state) => {
        return state.user?.is_superuser || state.user?.is_staff || state.userPermissions.includes('*');
    }
  },

  persist: true, // حتماً مطمئن شو پلاگین مربوطه را در main.js نصب کرده‌ای
});