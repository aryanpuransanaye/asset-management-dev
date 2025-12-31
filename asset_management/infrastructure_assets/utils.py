from .models import InfrastructureAssets

def get_infrastructure_asset_config():

    filter_fields = ['organization', 'sub_organization', 'supplier', 'owner']

    all_db_fields = [f.name for f in InfrastructureAssets._meta.get_fields() if not f.many_to_many]
    sorting_fields = all_db_fields + [f'-{field}' for field in all_db_fields]

    search_fields = ['related_property', 'owner', 'location', 'name']

    return {
        'filters': filter_fields,
        'sorting': sorting_fields,
        'search': search_fields
    }