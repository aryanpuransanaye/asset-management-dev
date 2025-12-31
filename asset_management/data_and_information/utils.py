from .models import DataAndInformation

def get_data_and_information_config():

    filter_fields = ['document_type', 'organization', 'sub_organization', 'confidentiality_level']

    all_db_fields = [f.name for f in DataAndInformation._meta.get_fields() if not f.many_to_many]
    sorting_fields = all_db_fields + [f'-{field}' for field in all_db_fields]

    search_fields = ['name', 'owner', 'usage', 'location', 'version']

    return {
        'filters': filter_fields,
        'sorting': sorting_fields,
        'search': search_fields
    }