from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


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
        if value and value.strip() and value != 'null':
            if field in ['organization', 'sub_organization', 'document_type']:
                applied_filters[f"{field}_id"] = value
            else:
                applied_filters[field] = value
    
    request.session[f'{session_key}_applied_filters'] = applied_filters

    search_query = request.GET.get('q')
    search_filter = Q()
    
    if search_query and search_fields:
        for field in search_fields:
            search_filter |= Q(**{f"{field}__icontains": search_query})

    if query_set is None and model is not None:
        query_set = get_accessible_queryset(request, model)
    
    query = query_set.filter(search_filter, **applied_filters).order_by(final_sort)
    
    return query



class BaseMetaDataAPIView(APIView):
    model = None
    fields_map = {} 
    choices_fields = {} 

    def get(self, request):
        if not self.model:
            return Response({"error": "Model not defined"}, status=status.HTTP_400_BAD_REQUEST)

        queryset = self.model.objects.filter(access_level=request.user.access_level)
        
        data = {}
        display_names = {}

        for key, field_path in self.fields_map.items():
            field_name = field_path.split('__')[0]
            model_field = self.model._meta.get_field(field_name)

   
            display_names[key] = model_field.verbose_name

            if model_field.is_relation:
                related_model = model_field.related_model
                
                if field_name == 'sub_organization':
                    related_data = related_model.objects.all().values('id', 'name', 'organization_id')
                else:
                    related_data = related_model.objects.all().values('id', 'name')
                
                data[key] = list(related_data)
            else:
                data[key] = list(queryset.values_list(field_path, flat=True).distinct())


        for key, field_name in self.choices_fields.items():
            field = self.model._meta.get_field(field_name)
            
            display_names[key] = field.verbose_name

            if hasattr(field, 'choices') and field.choices:
                data[key] = [{'value': k, 'label': v} for k, v in field.choices]

        display_names['q'] = 'جستجو'
        data['display_names'] = display_names

        return Response(data, status=status.HTTP_200_OK)