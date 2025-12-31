from .models import Software

def get_software_config():

    filter_fields = [
        'license_status', 'port', 'organization', 'sub_organization', 
        'owner', 'manufacturer'
    ]

    all_db_fields = [f.name for f in Software._meta.get_fields() if not f.many_to_many]
    sorting_fields = all_db_fields + [f'-{field}' for field in all_db_fields]

    search_fields = ['name', 'supplier', 'owner', 'manufacturer', 'hardware_location', 'related_property']

    return {
        'filters': filter_fields,
        'sorting': sorting_fields,
        'search': search_fields
    }