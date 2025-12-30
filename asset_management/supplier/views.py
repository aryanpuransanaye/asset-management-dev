from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated
from .models import Supplier
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


class SupplierListAPIView(APIView):

    permission_classes = [IsAuthenticated, DynamicSystemPermission]
    base_perm_name = 'suppliers'

    def get(self, request):

        sorting_fields = ['created_at', '-created-at', 'suppliers_name']
        allowed_filters = ['organization', 'sub_organization', 'access_level', 'related_property']
        searching_fields = ['supplier_name', 'manager_name', 'support_name', 'email', 'support_mobile_number', 'manager_mobile_number', 'company_mobile_number']
        suppliers = apply_filters_and_sorting(request, sorting_fields, allowed_filters, searching_fields, session_key='supplier', model=Supplier)

        serializer = serializers.ListSerializer(suppliers, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)



class SupplierAPIView(APIView):

    permission_classes = [IsAuthenticated, DynamicSystemPermission]
    base_perm_name = 'suppliers'

    def get(self, request, supplier_id):

        accessible_queryset = get_accessible_queryset(request, model=Supplier)
        supplier = get_object_or_404(accessible_queryset, id = supplier_id)
        serializer = serializers.DetailSerializer(supplier)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):

        serializer = serializers.CreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user = request.user, access_level = request.user.access_level)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, supplier_id):

        accessible_queryset = get_accessible_queryset(request, model=Supplier)
        supplier = get_object_or_404(accessible_queryset, id = supplier_id)
        
        serializer = serializers.CreateUpdateSerializer(supplier, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, *args, **kwargs):
        
        ids_to_delete = request.data.get('ids', [])
        if not ids_to_delete:
            return Response({'errors': 'there is not id to delete'}, status=status.HTTP_400_BAD_REQUEST)
        
        accessible_queryset = get_accessible_queryset(request, model=Supplier)
        suppliers = accessible_queryset.filter(id__in = ids_to_delete)

        if not suppliers.exists():
            return Response({'errors': "not found anything to delete"}, status=status.HTTP_404_NOT_FOUND)
        
        deleted_count, _ = suppliers.delete()

        return Response({'message': f"{deleted_count} things are deleted"}, status=status.HTTP_200_OK)
    


class SupplierExportAPIView(APIView):
    
    permission_classes = [IsAuthenticated, DynamicSystemPermission]
    base_perm_name = 'suppliers'

    def get(self, request):

        filters = request.session.get('supplier_filters', {})
        sorted_by = request.session.get('supplier_sorted_by', '-created_at')
        accessible_queryset = get_accessible_queryset(request, model=Supplier)
        suppliers = accessible_queryset.filter(**filters).order_by(sorted_by)

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = 'تامین کنندگان'

        fields = Supplier._meta.fields

        header = [field.verbose_name for field in fields]
        ws.append(header)
        
        for thing in suppliers:
            row = []
            for field in fields:
                value = getattr(thing, field.name)

                if field.name == 'user' and value:
                    value = value.username
                elif field.name == 'access_level' and value:
                    value = value.level_name
                elif field.name == 'organization' and value:
                    value = value.organization.name
                elif field.name == 'sub_organization' and value:
                    value = value.sub_organization.name
                elif field.name in ['created_at', 'updated_at'] and value:
                    value = jdatetime.datetime.fromgregorian(datetime=value).strftime('%Y/%m/%d %H:%M')

                row.append(value if value else '-')
            ws.append(row)

        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="supplier.xlsx"'
        ws.sheet_view.rightToLeft = True
        wb.save(response)

        return response