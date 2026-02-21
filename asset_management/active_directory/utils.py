from .models import ActiveDirectory

def get_active_directory_config():

    filter_fields = []

    all_db_fields = [f.name for f in ActiveDirectory._meta.get_fields() if not f.many_to_many]
    sorting_fields = all_db_fields + [f'-{field}' for field in all_db_fields]

    search_fields = ['server_address', 'domain_name', 'username']

    return {
        'filters': filter_fields,
        'sorting': sorting_fields,
        'search': search_fields
    }