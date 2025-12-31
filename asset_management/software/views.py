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
from django.db.models import Q
from core.utils import apply_filters_and_sorting, get_accessible_queryset, BaseMetaDataAPIView
from core.permissions import DynamicSystemPermission
from .utils import get_software_config


class SoftwareMetaDataAPIView(BaseMetaDataAPIView):

    model = Software
    fields_map = {
            'port': 'port',
            'owner': 'owner',
            'manufacturer': 'manufacturer',
            'organization': 'organization__name',
            'sub_organization': 'sub_organization__name'
    }
    choices_fields = {'license_statuses': 'license_status'}


class SoftwareListAPIView(APIView):
     
    permission_classes = [IsAuthenticated, DynamicSystemPermission]
    base_perm_name = 'software'

    def get(self, request):

        config = get_software_config()
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
        serializer = serializers.ListSerializer(softwares, many=True)
        columns = serializers.ListSerializer.get_active_columns()
        return Response({
            'results':serializer.data,
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

        config = get_software_config()
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

        fields = Software._meta.fields

        header = [field.verbose_name for field in fields]
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
                elif field.name == 'created_at':
                    value = jdatetime.datetime.fromgregorian(datetime=value).strftime('%Y/%m/%d %H:%M')
                elif field.name == 'updated_at':
                    value = jdatetime.datetime.fromgregorian(datetime=value).strftime('%Y/%m/%d %H:%M')

                row.append(value if value else '-')
            ws.append(row)

        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="software.xlsx"'
        ws.sheet_view.rightToLeft = True
        wb.save(response)
        return response