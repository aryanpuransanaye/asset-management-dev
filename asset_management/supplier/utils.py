from .models import Supplier

def get_supplier_config():

    filter_fields = ['organization', 'sub_organization']

    all_db_fields = [f.name for f in Supplier._meta.get_fields() if not f.many_to_many]
    sorting_fields = all_db_fields + [f'-{field}' for field in all_db_fields]

    search_fields = [
        'supplier_name', 'manager_name', 'support_name', 'email', 
        'support_mobile_number', 'manager_mobile_number', 'company_mobile_number', 
        'related_property'
    ]

    return {
        'filters': filter_fields,
        'sorting': sorting_fields,
        'search': search_fields
    }