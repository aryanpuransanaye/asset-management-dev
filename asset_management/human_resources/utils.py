from .models import HumanResource

def get_human_resource_config():

    filter_fields = [
        'administrative_position', 'manager', 
        'organization', 'sub_organization'
    ]

    all_db_fields = [f.name for f in HumanResource._meta.get_fields() if not f.many_to_many]
    sorting_fields = all_db_fields + [f'-{field}' for field in all_db_fields]

    search_fields = ['full_name', 'organizational_unit', 'location', 'personnel_id']

    return {
        'filters': filter_fields,
        'sorting': sorting_fields,
        'search': search_fields
    }