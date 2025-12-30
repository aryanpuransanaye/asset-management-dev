from rest_framework import serializers
from .models import IPManage, DiscoveredAsset
from data_and_information.models import DataAndInformation
from software.models import Software
from services.models import Services
from hardware.models import Hardware
from places_and_areas.models import PlacesAndArea
from infrastructure_assets.models import InfrastructureAssets
from intangible_assets.models import IntangibleAsset
from supplier.models import Supplier
import jdatetime


class IPByUserListSerializer(serializers.ModelSerializer):

    username = serializers.ReadOnlyField(source = 'user.username')
    access_level_name = serializers.ReadOnlyField(source = 'access_level.level_name')
    created_at = serializers.SerializerMethodField()
    class Meta:
        model = IPManage
        fields = [
            'id', 'name', 'username', 'access_level_name',
            'ipaddress', 'subnet', 'vlan', 'created_at',
        ]
    
    def get_created_at(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    @staticmethod
    def get_metadata():
        return {
            'filters': [
                {'key': 'subnet', 'label': 'ساب نت', 'type': 'select', 'data_source': 'subnets'},
                {'key': 'vlan', 'label': 'ساب نت', 'type': 'select', 'data_source': 'vlans'},
                {'key': 'access_level', 'label': '', 'type': 'select', 'data_source': 'access_levels'},
            ],
            'sorting': [
                {'key': 'created_at', 'label': 'تاریخ (صعودی)'},
                {'key': '-created_at', 'label': 'تاریخ (صعودی)'},
                {'key': 'ipaddress', 'label': 'آدرس آی پی'},
                {'key': 'vlan', 'label': 'VLAN'}
            ],
            'searching': ['name', 'ipaddress']
        }


class IpByUserDetail(serializers.ModelSerializer):

    username = serializers.ReadOnlyField(source = 'user.username')
    access_level = serializers.ReadOnlyField(source = 'access_level.level_name')

    class Meta:
        model = IPManage
        fields = [
            'name', 'ipaddress', 'subnet', 'vlan'
        ]


class IpByUserCreateUpdate(serializers.ModelSerializer):

    class Meta:
        model = IPManage
        fields = [
            'name', 'ipaddress', 'subnet', 'vlan'
        ]
    
    def create(self, validated_data):

        request = self.context.get('request')
        if request and request.user:
            validated_data['user'] = request.user
            validated_data['access_level'] = request.user.access_level

        return super().create(validated_data)


class CreateScannedAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscoveredAsset
        fields = [
            'network_range', 'ipaddress', 'mac',
            'os', 'vendor', 'access_level', 'user'
        ]

    @classmethod
    def bulk_create_assets(cls, asset_lis_data):
        new_objects = [DiscoveredAsset(**data) for data in asset_lis_data]
        return DiscoveredAsset.objects.bulk_create(new_objects)


class AssetInManualyRangeListSerializer(serializers.ModelSerializer):

    username = serializers.ReadOnlyField(source = 'user.username')
    access_level_name = serializers.ReadOnlyField(source = 'access_level.level_name')
    network_range_ip = serializers.ReadOnlyField(source = 'network_range.ipaddress')
    category_name = serializers.ReadOnlyField(source = 'get_category_display')
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = DiscoveredAsset
        fields = [
            'id', 'username', 'access_level_name', 'network_range_ip', 'ipaddress',
            'mac', 'os', 'vendor', 'category_name', 'created_at'
        ]

    def get_created_at(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    @staticmethod
    def get_metadata():
        return {
            'filters': [
                {'key': 'category', 'label': 'دسته بندی', 'type': 'select', 'data_source': 'categories'},
                {'key': 'network_ranges', 'label': 'محدوده شبکه', 'type': 'select', 'data_source': 'network_ranges'},
                {'key': 'access_level', 'label': 'سطح دستری', 'type': 'select', 'data_source': 'access_levels'},
            ],
            'sorting': [
                {'key': 'created_at', 'label': 'تاریخ (صعودی)'},
                {'key': '-created_at', 'label': 'تاریخ (صعودی)'},
                {'key': 'ipaddress', 'label': 'آدرس آی پی'},
            ], 
            'searching': ['mac', 'ipaddress', 'os', 'vendor']
        }
    

class AssetInManualyRangeDetail(serializers.ModelSerializer):

    username = serializers.ReadOnlyField(source = 'user.username')
    access_level_name = serializers.ReadOnlyField(source = 'access_level.level_name')
    network_range_ip = serializers.ReadOnlyField(source = 'network_range.ipaddress')
    
    class Meta:
        model = DiscoveredAsset
        fields = [
            'username', 'access_level_name', 'network_range_ip', 'ipaddress',
            'mac', 'os', 'vendor', 'category'
        ]

class AssetInManualyRangeUpdate(serializers.ModelSerializer):

    class Meta:
        model = DiscoveredAsset
        fields = [
            'ipaddress', 'os', 'mac', 'vendor', 'category'
        ]

    def update(self, instance, validated_data):
        
        category = validated_data.pop('category', None)
        if category:
            instance.category = category
            instance.save()

            DESTINATION_MAP = {
                '0': DataAndInformation,
                '1': Software,
                '2': Services,
                '3': Hardware,
                '4': PlacesAndArea,
                '5': InfrastructureAssets,
                '6': IntangibleAsset,
                '7': Supplier
            }

            target_model = DESTINATION_MAP.get(category)
            if target_model:
                target_model.objects.create(
                    ipaddress=instance.ipaddress,
                    mac=instance.mac,
                    os=instance.os,
                    vendor=instance.vendor,
                    user=instance.user,
                    access_level=instance.access_level,
                )
              
                # instance.delete()
                return instance 

        return super().update(instance, validated_data)