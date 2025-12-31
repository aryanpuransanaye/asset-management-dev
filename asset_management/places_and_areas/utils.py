from .models import PlacesAndArea

def get_place_and_area_config():

    filter_fields = ['organization', 'sub_organization', 'usage', 'owner']

    all_db_fields = [f.name for f in PlacesAndArea._meta.get_fields() if not f.many_to_many]
    sorting_fields = all_db_fields + [f'-{field}' for field in all_db_fields]

    search_fields = ['name', 'owner', 'location']

    return {
        'filters': filter_fields,
        'sorting': sorting_fields,
        'search': search_fields
    }