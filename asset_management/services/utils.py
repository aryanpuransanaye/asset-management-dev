from .models import Services

def get_service_config():

    filter_fields = ['port', 'organization', 'sub_organization', 'owner']

    all_db_fields = [f.name for f in Services._meta.get_fields() if not f.many_to_many]
    sorting_fields = all_db_fields + [f'-{field}' for field in all_db_fields]

    search_fields = ['name', 'hardware_location', 'related_property', 'build_number_os']

    return {
        'filters': filter_fields,
        'sorting': sorting_fields,
        'search': search_fields
    }