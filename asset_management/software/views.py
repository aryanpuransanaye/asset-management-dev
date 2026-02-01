from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated
from .models import Software
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from . import serializers
from django.shortcuts import get_object_or_404
import openpyxl, jdatetime
from django.http import HttpResponse
from django.db.models import Q, Count
from core.utils import apply_filters_and_sorting, get_accessible_queryset, set_paginator, BaseMetaDataAPIView
from core.permissions import DynamicSystemPermission
from .utils import get_software_config

config = get_software_config()


class SoftwareSummaryAPIView(APIView):

    permission_classes = [IsAuthenticated, DynamicSystemPermission]
    base_perm_name = 'software'

    def get(self, request):

        accessible_queryset = get_accessible_queryset(request, model=Software)

        total_count = accessible_queryset.count()

        software = accessible_queryset.aggregate(
            license_expired_count = Count('license_expired_date', filter=Q(license_expired_date__lt=jdatetime.datetime.now().togregorian())),
            license_not_expired_count = Count('license_expired_date', filter=Q(license_expired_date__gte=jdatetime.datetime.now().togregorian())),
        )

        last_item = accessible_queryset.order_by('-created_at').first()
        print(last_item.name)
        summary_data = [
            {'label': 'تعداد نرم‌افزارها', 'value': total_count, 'color': 'purple'},
            {'label': 'مجوز منقضی شده', 'value': software['license_expired_count'], 'color': 'red'},
            {'label': 'مجوز معتبر', 'value': software['license_not_expired_count'], 'color': 'green'},
            {'label': 'جدیدترین', 'value': last_item.name if last_item else 'دارایی ثبت نشده', 'color': 'orange'}
        ]

        return Response(summary_data,status=status.HTTP_200_OK)
    

class SoftwareMetaDataAPIView(BaseMetaDataAPIView):

    model = Software
    fields_map = {field:field for field in config['filters']}
    search_fields = config['search']


class SoftwareListAPIView(APIView):
     
    permission_classes = [IsAuthenticated, DynamicSystemPermission]
    base_perm_name = 'software'

    def get(self, request):

        softwares = apply_filters_and_sorting(
            request, 
            config['sorting'], 
            config['filters'], 
            config['search'], 
            session_key='hardware', 
            model=Software
        ).select_related(
            'organization', 
            'sub_organization', 
            'user', 
            'access_level'
        )

        paginator = set_paginator(request, softwares)
        serializer = serializers.ListSerializer(paginator['data'], many=True)
        columns = serializers.ListSerializer.get_active_columns()
        return Response({
            'results':serializer.data,
            'total_pages': paginator['total_pages'],
            'current_page': paginator['current_page'],
            'total_items': paginator['total_items'],
            'columns': columns
        }, status=status.HTTP_200_OK)

class SoftWareAPIView(APIView):

    permission_classes = [IsAuthenticated, DynamicSystemPermission]
    base_perm_name = 'software'

    def get(self, request, software_id=None):

        config_form = serializers.CreateUpdateSerializer.get_form_config()
        if software_id:
            accessible_queryset = get_accessible_queryset(request, model=Software)
            software = get_object_or_404(accessible_queryset, id = software_id)
            serializer = serializers.DetailSerializer(software)
        
        return Response({
            'result':serializer.data if software_id else {},
            'config_form': config_form
            }, status = status.HTTP_200_OK)
    
    
    def post(self, request):
        
        serializer = serializers.CreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user = request.user, access_level = request.user.access_level)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def patch(self, request, software_id):

        accessible_queryset = get_accessible_queryset(request, model=Software)
        selected_software = get_object_or_404(accessible_queryset, id = int(software_id))

        serializer = serializers.CreateUpdateSerializer(selected_software, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    def delete(self, request, *arg, **kwargs):

        ids_to_delete = request.data.get('ids', [])
        if not ids_to_delete:
            return Response({'errors': 'there is not id to delete'}, status=status.HTTP_400_BAD_REQUEST)
        
        accessible_queryset = get_accessible_queryset(request, model=Software)
        softwares = accessible_queryset.filter(id__in = ids_to_delete)

        if not softwares.exists():
            return Response({'errors': "not found anything to delete"}, status=status.HTTP_404_NOT_FOUND)
        
    
        deleted_count, _ = softwares.delete()

        return Response({'message': f"{deleted_count} things are deleted"}, status=status.HTTP_200_OK)
    

class SoftWareExportAPIView(APIView):
    
    permission_classes = [IsAuthenticated, DynamicSystemPermission]
    base_perm_name = 'software'

    def get(self, request):

        softwares = apply_filters_and_sorting(
            request, 
            config['sorting'], 
            config['filters'], 
            config['search'], 
            session_key='hardware', 
            model=Software
        ).select_related(
            'organization', 
            'sub_organization', 
            'user', 
            'access_level'
        )

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = 'نرم افزار'
        ws.sheet_view.rightToLeft = True
        
        fields = [field for field in Software._meta.fields if field.name != 'id']

        header = header = [field.verbose_name for field in fields]
        ws.append(header)
        
        for thing in softwares:
            row = []
            for field in fields:
                value = getattr(thing, field.name)

                if field.name == 'user':
                        value = value.username
                elif field.name == 'access_level':
                        value = value.level_name
                elif field.name == 'license_status':
                        value = str(thing.get_license_status_display())
                elif field.name == 'organization' and value:
                        value = value.organization.name
                elif field.name == 'sub_organization' and value:
                        value = value.sub_organization.name
                elif field.name in ['created_at', 'updated_at', 'license_expired_date'] and value:
                    value = jdatetime.datetime.fromgregorian(datetime=value).strftime('%Y/%m/%d %H:%M')

                row.append(value if value else '-')
            ws.append(row)

        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="software.xlsx"'
        wb.save(response)
        return response