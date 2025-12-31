from .models import DiscoveredAsset


def get_ip_manage_config():

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

    filter_fields = ['category']

    all_db_fields = [f.name for f in DiscoveredAsset._meta.get_fields() if not f.many_to_many]
    sorting_fields = all_db_fields + [f'-{field}' for field in all_db_fields]

    search_fields = ['ipaddress', 'mac', 'os', 'vendor']

    return {
        'filters': filter_fields,
        'sorting': sorting_fields,
        'search': search_fields
    }