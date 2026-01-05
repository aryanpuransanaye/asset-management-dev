from rest_framework.permissions import IsAuthenticated
from .models import Organization, SubOrganization
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from . import serializers
from django.shortcuts import get_object_or_404
# import openpyxl, jdatetime
# from django.http import HttpResponse
from django.db.models import Q
from core.utils import apply_filters_and_sorting, get_accessible_queryset
# from core.permissions import DynamicSystemPermission


###ORGANIZATION###

class OrganizationSummaryAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        total_organizations = Organization.objects.count()

        summary_data = {
            {'label': 'تعداد سازمان‌ها', 'value': total_organizations, 'color': 'blue'}
        }

        return Response(summary_data, status=status.HTTP_200_OK)


class OrganizationListAPIView(APIView):

    permission_classes = [IsAuthenticated]
    def get(self, request):
        
        organizations = Organization.objects.all()
        serializer = serializers.OrganizationListSerializer(organizations, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    

class OrganizationAPIView(APIView):

    def get(self, request, organization_id):

        organization = get_object_or_404(Organization, id = organization_id)
        serializer = serializers.OrganizationDetailSerializer(organization)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        
        serializer = serializers.OrganizationCreateUpdate(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, organization_id):

        organization = get_object_or_404(Organization, id = organization_id)
        serializer = serializers.OrganizationCreateUpdate(organization, data=request.data, partial = True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, *args, **kwargs):

        ids_to_delete = request.data.get('ids', [])
        if not ids_to_delete:
            return Response({'errors': 'there is not id to delete'}, status=status.HTTP_400_BAD_REQUEST)
        
        # accessible_queryset = get_accessible_queryset(request, model=Organization)
        organization = Organization.objects.filter(id__in = ids_to_delete)

        if not organization.exists():
            return Response({'errors': "not found anything to delete"}, status=status.HTTP_404_NOT_FOUND)
        
    
        deleted_count, _ = organization.delete()

        return Response({'message': f"{deleted_count} things are deleted"}, status=status.HTTP_200_OK)



###SUB ORGANIZATION###

class SubOrganizationSummaryAPIView(APIView):

    def get(self, request, organization_id):

        organization = get_object_or_404(Organization, id = organization_id)
        total_sub_organizations = SubOrganization.objects.filter(organization=organization).count()

        summary_data = {
            {'label': 'تعداد زیرسازمان‌ها', 'value': total_sub_organizations, 'color': 'green'}
        }

        return Response(summary_data, status=status.HTTP_200_OK)


class SubOrganizationListAPIView(APIView):

    def get(self, request, organization_id):

        organization = get_object_or_404(Organization, id = organization_id)
        sub_organization = SubOrganization.objects.all().filter(organization = organization)
        serializer = serializers.SubOrganizationListSerializer(sub_organization, many = True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    


class SubOrganizationAPIView(APIView):

    def get(self, request, sub_organization_id):

        sub_organization = get_object_or_404(SubOrganization, id = sub_organization_id)
        serializer = serializers.SubOrganizationDetailSerializar(sub_organization)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):

        serializer = serializers.SubOrganizationCreateUpdateSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, sub_organization_id):

        sub_organization = get_object_or_404(SubOrganization, id = sub_organization_id)
        
        serializer = serializers.SubOrganizationCreateUpdateSerializer(sub_organization, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status = status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, *args, **kwargs):

        ids_to_delete = request.data.get('ids', [])
        if not ids_to_delete:
            return Response({'errors': 'there is not id to delete'}, status=status.HTTP_400_BAD_REQUEST)
        
        # accessible_queryset = get_accessible_queryset(request, model=Organization)
        sub_organization = SubOrganization.objects.filter(id__in = ids_to_delete)

        if not sub_organization.exists():
            return Response({'errors': "not found anything to delete"}, status=status.HTTP_404_NOT_FOUND)
        
    
        deleted_count, _ = sub_organization.delete()

        return Response({'message': f"{deleted_count} things are deleted"}, status=status.HTTP_200_OK)
        