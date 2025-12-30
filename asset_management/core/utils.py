from django.db.models import Q



def get_accessible_queryset(request, model=None, queryset=None):
    
    user = request.user

    if user.is_superuser:
        return queryset if queryset is not None else model.objects.all()

    if not user.access_level:
        return model.objects.none() if model else queryset.none()

    allowed_levels = user.access_level.get_descendants(include_self=True)

    if queryset is not None:
        return queryset.filter(access_level__in=allowed_levels)
    return model.objects.filter(access_level__in=allowed_levels)


def apply_filters_and_sorting(request, sorting_fields:list, allowed_filters: list, search_fields:list, session_key:str, model=None, query_set=None):
  
    sort_by = request.GET.get('sort_by')
    if sort_by and sort_by in sorting_fields:
        final_sort = sort_by
    else:
        final_sort = '-created_at'
        
    request.session[f'{session_key}_sorted_by'] = final_sort

    applied_filters = {}
    for field in allowed_filters:
        value = request.GET.get(field)
        if value and value.strip():
            applied_filters[field] = value
    
    request.session[f'{session_key}_applied_filters'] = applied_filters

    search_query = request.GET.get('q')
    search_filter = Q()
    
    if search_query and search_fields:
        for field in search_fields:
            search_filter |= Q(**{f"{field}__icontains": search_query})

        # request.session[f'{session_key}_search_query'] = search_query

    if query_set is None and model is not None:
        query_set = get_accessible_queryset(request, model)
    
    query = query_set.filter(search_filter, **applied_filters).order_by(final_sort)
    
    return query

