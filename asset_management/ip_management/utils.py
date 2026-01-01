from .models import DiscoveredAsset


def get_ip_manage_config():

    """
    Returns the metadata configuration for the model.

    This configuration defines the behavior for:
    - filter_fields: Columns available for dropdown filtering.
    - sorting: All database fields in both ascending and descending order.
    - search: Specific fields targeted by the global search query.

    Returns:
        dict: A dictionary containing 'filters', 'sorting', and 'search' configurations.
    """

    filter_fields = ['subnet', 'vlan']

    all_db_fields = [f.name for f in DiscoveredAsset._meta.get_fields() if not f.many_to_many]
    sorting_fields = all_db_fields + [f'-{field}' for field in all_db_fields]

    search_fields = ['name', 'ipaddress']

    return {
        'filters': filter_fields,
        'sorting': sorting_fields,
        'search': search_fields
    }



def get_discovered_asset_config():

    """
    Returns the metadata configuration for the model.

    This configuration defines the behavior for:
    - filter_fields: Columns available for dropdown filtering.
    - sorting: All database fields in both ascending and descending order.
    - search: Specific fields targeted by the global search query.

    Returns:
        dict: A dictionary containing 'filters', 'sorting', and 'search' configurations.
    """

    filter_fields = ['category']

    all_db_fields = [f.name for f in DiscoveredAsset._meta.get_fields() if not f.many_to_many]
    sorting_fields = all_db_fields + [f'-{field}' for field in all_db_fields]

    search_fields = ['ipaddress', 'mac', 'os', 'vendor']

    return {
        'filters': filter_fields,
        'sorting': sorting_fields,
        'search': search_fields
    }