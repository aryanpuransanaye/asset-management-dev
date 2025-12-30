from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from core.models import Organization, SubOrganization
from accounts.models import User, AccessLevel
from ip_management.models import IPManage, DiscoveredAsset
from data_and_information.models import DataAndInformation
from hardware.models import Hardware
from software.models import Software


class FilterOptionsAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        app_name = request.GET.get('app')
        data = {}


        data['access_levels'] = list(AccessLevel.objects.values('id', 'level_name'))

        if app_name in ['data_and_information', 'hardware', 'software']:
            data['organization'] = list(Organization.objects.values('id', 'name'))
            data['sub_organization'] = list(SubOrganization.objects.values('id', 'name'))


        if app_name == 'ip_management':
            data['subnet'] = list(IPManage.objects.exclude(subnet__isnull=True).values_list('subnet', flat=True).distinct())
            data['vlan'] = list(IPManage.objects.exclude(vlan__isnull=True).values_list('vlan', flat=True).distinct())
            unique_cats = DiscoveredAsset.objects.values_list('category', flat=True).distinct()
            data['category'] = [
                {'id': c, 'label': dict(DiscoveredAsset.CATEGORY_CHOICES).get(c, c)} 
                for c in unique_cats if c
            ]
            data['network_range'] = list(DiscoveredAsset.objects.values_list('network_range', flat=True).distinct())


        if app_name == 'data_and_information':
            unique_confidentiality_level = list(DataAndInformation.objects.values_list('confidentiality_level', flat=True).distinct())
            data['confidentiality_level'] = [
                {'id': c, 'label': dict(DiscoveredAsset.CATEGORY_CHOICES).get(c, c)} 
                for c in unique_confidentiality_level if c
            ]
            data['version'] = list(DataAndInformation.objects.exclude(version__isnull=True).values_list('version', flat=True).distinct())
            data['document_type'] = list(DataAndInformation.objects.exclude(document_type__isnull=True).values_list('document_type', flat=True).distinct())


        if app_name == 'hardware':
            data['hostname'] = list(Hardware.objects.exclude(version__isnull=True).values_list('hostname', flat=True).distinct())
            data['hardware_type'] = list(Hardware.objects.exclude(version__isnull=True).values_list('hardware_type', flat=True).distinct())
            data['status'] = list(Hardware.objects.exclude(version__isnull=True).values_list('status', flat=True).distinct())
            data['vulner_status'] = list(Hardware.objects.exclude(version__isnull=True).values_list('vulner_status', flat=True).distinct())
            data['manufacturer'] = list(Hardware.objects.exclude(version__isnull=True).values_list('manufacturer', flat=True).distinct())


        if app_name == 'software':
            unique_license_status = list(Hardware.objects.values_list('license_status', flat=True).distinct())
            data['license_status'] = [
                {'id':c, 'lavel': dict(Software.LICENCE_STATUS).get(c, c)}
                for c in unique_license_status if c
            ]
            data['hostname'] = list(Software.objects.exclude(version__isnull=True).values_list('hostname', flat=True).distinct())
            data['port'] = list(Software.objects.exclude(version__isnull=True).values_list('hardware_type', flat=True).distinct())


        if app_name == 'services':
            ...


        if app_name == 'places_and_areas':
            ...

        return Response(data, status=status.HTTP_200_OK)