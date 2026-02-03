from rest_framework import serializers
from .models import IPManage, DiscoveredAsset
from accounts.models import User, AccessLevel
from data_and_information.models import DataAndInformation
from software.models import Software
from services.models import Services
from hardware.models import Hardware
from human_resources.models import HumanResource
from places_and_areas.models import PlacesAndArea
from infrastructure_assets.models import InfrastructureAssets
from intangible_assets.models import IntangibleAsset
from supplier.models import Supplier
import jdatetime


class IPByUserListSerializer(serializers.ModelSerializer):

    username = serializers.ReadOnlyField(source = 'user.username')
    access_level_name = serializers.ReadOnlyField(source = 'access_level.level_name')
    created_at = serializers.SerializerMethodField()

    status = serializers.SerializerMethodField()
    result_count = serializers.SerializerMethodField()

    LABEL_OVERRIDES = {
        'status': 'وضعیت اخرین اسکن',
        'result_count': 'تعداد یافته ها در اخرین اسکن',
    }
    class Meta:
        model = IPManage
        fields = [
            'id', 'name', 'username', 'access_level_name',
            'ipaddress', 'subnet', 'vlan', 'status', 'result_count', 'created_at',
        ]
    
    def get_created_at(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        return None

    def get_status(self, obj):
    
        last = obj.scan_history.order_by('-created_at').first()
        if last:
            return last.get_status_display()
        return None

    def get_result_count(self, obj):
        
        last = obj.scan_history.order_by('-created_at').first()
        if last:
            return last.result_count
        return None
    
    @classmethod
    def get_active_columns(cls):
       
        model = cls.Meta.model
        target_fields = getattr(cls.Meta, 'fields', [])
        
        columns = []
        for field_name in target_fields:
            try:
              
                label = model._meta.get_field(field_name).verbose_name
            except:
                label = field_name.replace('_', ' ').capitalize()
            # apply any serializer-level label overrides for computed fields
            overrides = getattr(cls, 'LABEL_OVERRIDES', {})
            if field_name in overrides:
                label = overrides[field_name]
            
            columns.append({
                'key': field_name,
                'label': label
            })
            
        return columns
    


class IpByUserDetailSerializer(serializers.ModelSerializer):

    username = serializers.ReadOnlyField(source = 'user.username')
    access_level = serializers.ReadOnlyField(source = 'access_level.level_name')

    class Meta:
        model = IPManage
        fields = [
            'name', 'ipaddress', 'subnet', 'vlan', 'access_level', 'username'
        ]


class IpByUserCreateUpdateSerializer(serializers.ModelSerializer):

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
    

    @classmethod
    def get_form_config(cls):
       
        config = []
        model = cls.Meta.model
        fields_to_create = getattr(cls.Meta, 'fields', [])

        for field_name in fields_to_create:
          
            if field_name in ['id', 'created_at', 'updated_at']:
                continue

            try:
                model_field = model._meta.get_field(field_name)
                field_data = {
                    'key': field_name,
                    'label': model_field.verbose_name,
                    'required': not model_field.blank,
                    'type': model_field.get_internal_type(),
                }

                if model_field.choices:
                    field_data['type'] = 'ChoiceField'
                    field_data['options'] = [
                        {'value': k, 'label': v} for k, v in model_field.choices
                    ]
                
                elif model_field.is_relation:
                    field_data['type'] = 'ForeignKey'

                config.append(field_data)
            except:
                continue

        return config


class CreateScannedAssetSerializer(serializers.ModelSerializer):

    network_range = serializers.PrimaryKeyRelatedField(queryset=IPManage.objects.all())
    access_level = serializers.PrimaryKeyRelatedField(queryset=AccessLevel.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    
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

    user = serializers.ReadOnlyField(source = 'user.username')
    access_level = serializers.ReadOnlyField(source = 'access_level.level_name')
    network_range = serializers.ReadOnlyField(source = 'network_range.ipaddress')
    category = serializers.ReadOnlyField(source = 'get_category_display')
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = DiscoveredAsset
        fields = [
            'id', 'user', 'access_level', 'network_range', 'ipaddress',
            'mac', 'os', 'vendor', 'category', 'created_at'
        ]

    def get_created_at(self, obj):
        if obj.created_at:
            return jdatetime.datetime.fromgregorian(datetime=obj.created_at).strftime('%Y/%m/%d %H:%M')
        return None
    
    @classmethod
    def get_active_columns(cls):
       
        model = cls.Meta.model
        target_fields = getattr(cls.Meta, 'fields', [])
        
        columns = []
        for field_name in target_fields:
            try:
              
                label = model._meta.get_field(field_name).verbose_name
            except:
                label = field_name.replace('_', ' ').capitalize()
            
            columns.append({
                'key': field_name,
                'label': label
            })
            
        return columns
    
    
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
   
    target_object_id = serializers.ReadOnlyField()

    class Meta:
        model = DiscoveredAsset
        fields = [
            'ipaddress', 'os', 'mac', 'vendor', 'category', 'target_object_id'
        ]

    def update(self, instance, validated_data):

        instance.ipaddress = validated_data.get('ipaddress', instance.ipaddress)
        instance.os = validated_data.get('os', instance.os)
        instance.mac = validated_data.get('mac', instance.mac)
        instance.vendor = validated_data.get('vendor', instance.vendor)
        
        category = validated_data.get('category')
        if category is not None:
            instance.category = category

        instance.save()

        created_target_id = None

        if category:
            DESTINATION_MAP = {
                'data-and-information': DataAndInformation,
                'software': Software,
                'services': Services,
                'hardware': Hardware,
                'places-and-areas': PlacesAndArea,
                'human-resource': HumanResource,
                'infrastructure-asset': InfrastructureAssets,
                'intangible-asset': IntangibleAsset,
                'supplier': Supplier
            }
            
            target_model_class = DESTINATION_MAP.get(category)
            
            if target_model_class:
                new_asset = target_model_class.objects.create(
                    ipaddress=instance.ipaddress,
                    mac=instance.mac,
                    os=instance.os,
                    vendor=instance.vendor,
                    user=instance.user,
                    access_level=instance.access_level,
                )
                
                created_target_id = new_asset.id
                
                instance.delete()

        if created_target_id:
            setattr(instance, 'target_object_id', created_target_id)

        return instance
    
    @classmethod
    def get_form_config(cls):
       
        config = []
        model = cls.Meta.model
        fields_to_create = getattr(cls.Meta, 'fields', [])
        for field_name in fields_to_create:
          
            if field_name in ['id', 'created_at', 'updated_at']:
                continue

            try:
                model_field = model._meta.get_field(field_name)
                field_data = {
                    'key': field_name,
                    'label': model_field.verbose_name,
                    'required': not model_field.blank,
                    'type': model_field.get_internal_type(),
                }

                if model_field.choices:
                    field_data['type'] = 'ChoiceField'
                    field_data['options'] = [
                        {'value': k, 'label': v} for k, v in model_field.choices
                    ]
                
                elif model_field.is_relation:
                    field_data['type'] = 'ForeignKey'

                config.append(field_data)
            except:
                continue

        return config