from .models import HumanResource

def get_human_resource_config():

    """
    Returns the metadata configuration for the model.

    This configuration defines the behavior for:
    - filter_fields: Columns available for dropdown filtering.
    - sorting: All database fields in both ascending and descending order.
    - search: Specific fields targeted by the global search query.

    Returns:
        dict: A dictionary containing 'filters', 'sorting', and 'search' configurations.
    """

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