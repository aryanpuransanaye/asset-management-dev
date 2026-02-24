from .models import User

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_user_config():
        
    filter_fields = ['groups', 'user_permissions', 'gender']

    all_db_fields = [f.name for f in User._meta.get_fields() if not f.many_to_many]
    sorting_fields = all_db_fields + [f'-{field}' for field in all_db_fields]

    search_fields = ['username', 'email', 'first_name', 'last_name', 'phone_number']

    return {
        'filters': filter_fields,
        'sorting': sorting_fields,
        'search': search_fields
    }