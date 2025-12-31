from .models import Hardware

def get_hardware_config():

    filter_fields = [
        'hardware_type', 'status', 'vulner_status',
        'manufacturer', 'organization', 'sub_organization'
    ]

    all_db_fields = [f.name for f in Hardware._meta.get_fields() if not f.many_to_many]
    sorting_fields = all_db_fields + [f'-{field}' for field in all_db_fields]

    search_fields = [
        'name', 'hostname', 'model', 'manufacturer'
    ]

    return {
        'filters': filter_fields,
        'sorting': sorting_fields,
        'search': search_fields
    }