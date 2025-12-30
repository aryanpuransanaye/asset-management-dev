from rest_framework.permissions import IsAuthenticated
from .models import DataAndInformation
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from . import serializers
from django.shortcuts import get_object_or_404
import openpyxl, jdatetime
from django.http import HttpResponse
from django.db.models import Q
from core.utils import apply_filters_and_sorting, get_accessible_queryset
from core.permissions import DynamicSystemPermission


class DataAndInformationListAPIView(APIView):

    permission_classes = [IsAuthenticated, DynamicSystemPermission]
    base_perm_name = 'data_and_information'

    def get(self, request):
        
        
        sorting_fields = ['created_at', '-created-at', 'confidentiality_level', 'name']
        allowed_filters = ['confidentiality_level', 'version', 'document_type', 'organization', 'sub_organization']
        search_fields = ['name', 'owner', 'usage', 'location', 'version']
        
        data_and_informations = apply_filters_and_sorting(request, sorting_fields, allowed_filters, search_fields, session_key='data_info', model=DataAndInformation)

        serializer = serializers.ListSerializer(data_and_informations, many=True)
        # meta_data = serializers.ListSerializer.get_metadata()
        return Response(serializer.data, status=status.HTTP_200_OK)
            


class DataAndInformationAPIView(APIView):

    permission_classes = [IsAuthenticated, DynamicSystemPermission]
    base_perm_name = 'data_and_information'

    def get(self, request, pk):
        
        accessible_queryset = get_accessible_queryset(request, model=DataAndInformation)
        data_and_information = get_object_or_404(accessible_queryset, id=pk)
        serializer  = serializers.DetailSerializer(data_and_information)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
        

    def post(self, request):

        serializer = serializers.CreateUpdateSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user=request.user, access_level=request.user.access_level)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    def delete(self, request, *args, **kwargs):

        ids_to_delete = request.data.get('ids', [])
        if not ids_to_delete:
            return Response({'errors': 'there is not id to delete'}, status=status.HTTP_400_BAD_REQUEST)
        
        accessible_queryset = get_accessible_queryset(request, model=DataAndInformation)
        data_and_informations = accessible_queryset.filter(id__in = ids_to_delete)
        if not data_and_informations.exists():
            return Response({'errors': "not found anything to delete"}, status=status.HTTP_404_NOT_FOUND)
        
    
        deleted_count, _ = data_and_informations.delete()

        return Response({'message': f"{deleted_count} things are deleted"}, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        
        accessible_queryset = get_accessible_queryset(request, model=DataAndInformation)
        selected_data_and_infomation = get_object_or_404(accessible_queryset, id=pk)

        serializer = serializers.CreateUpdateSerializer(selected_data_and_infomation, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)


class DataAndInformationExport(APIView):

    permission_classes = [IsAuthenticated, DynamicSystemPermission]
    base_perm_name = 'data_and_information'

    def get(self, request):

        filters = request.session.get('data_info_applied_filters', {})
        sorted_by = request.session.get('data_info_sorted_by', '-created_at')
        accessible_queryset = get_accessible_queryset(request, model=DataAndInformation)
        data_and_informations = accessible_queryset.filter(**filters).order_by(sorted_by)
        
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = 'داده و اطلاعات'

        fields = DataAndInformation._meta.fields
        header = [field.verbose_name for field in fields]
        ws.append(header)

        for thing in data_and_informations:
            row = []
            for field in fields:
                value = getattr(thing, field.name)

                if field.name == 'user' and value:
                        value = value.username
                elif field.name == 'access_level' and value:
                        value = value.level_name
                elif field.name == 'organization' and value:
                        value = value.name
                elif field.name == 'sub_organization' and value:
                        value = value.name
                elif field.name == 'created_at' and value:
                    value = jdatetime.datetime.fromgregorian(datetime=value).strftime('%Y/%m/%d %H:%M')
                elif field.name == 'updated_at' and value:
                    value = jdatetime.datetime.fromgregorian(datetime=value).strftime('%Y/%m/%d %H:%M')

                row.append(value if value else '-')
        ws.append(row)

        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="data_and_information_export.xlsx"'
        wb.save(response)
        return response