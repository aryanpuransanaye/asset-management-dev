from .models import Organization, SubOrganization

def get_organization_config():

    filter_fields = []

    all_db_fields = [f.name for f in Organization._meta.get_fields() if not f.many_to_many]
    sorting_fields = all_db_fields + [f'-{field}' for field in all_db_fields]

    search_fields = ['email', 'address', 'phone_number', 'name']

    return {
        'filters': filter_fields,
        'sorting': sorting_fields,
        'search': search_fields
    }

def get_sub_organization_config():

    filter_fields = []

    all_db_fields = [f.name for f in SubOrganization._meta.get_fields() if not f.many_to_many]
    sorting_fields = all_db_fields + [f'-{field}' for field in all_db_fields]

    search_fields = ['address', 'name']

    return {
        'filters': filter_fields,
        'sorting': sorting_fields,
        'search': search_fields
    }