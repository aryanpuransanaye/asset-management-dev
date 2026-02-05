from rest_framework import permissions

class DynamicSystemPermission(permissions.BasePermission):
   

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False

        if user.is_superuser or user.is_staff:
            return True

        base_perm_name = getattr(view, 'base_perm_name', None)
        
        if not base_perm_name:
            return False

        crud_perm = f'accounts.asset_{base_perm_name}_crud'
        read_perm = f'accounts.asset_{base_perm_name}_r'

        if request.method in permissions.SAFE_METHODS: # GET
            return user.has_perm(read_perm) or user.has_perm(crud_perm)
        
        #(POST, PUT, PATCH, DELETE)
        return user.has_perm(crud_perm)
    

class PasswordChangeRequired(permissions.BasePermission):

    message = "لطفا ابتدا رمز عبور خود را تغییر دهید."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return True
            
        if getattr(request.user, 'requirement_to_change_the_password', False):
            return False
            
        return True