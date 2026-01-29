from rest_framework import serializers
from .models import Software
from core.serializer import *


class ListSerializer(BaseListSerializer):
    license_status_name = serializers.ReadOnlyField(source = 'get_license_status_display')

    class Meta(BaseListSerializer.Meta):
        model = Software
        fields = [
            'id', 'supplier', 'hardware_location', 'related_property', 'port', 'owner', 'license_status_name',
            'license_expired_date', 'manufacturer', 'name'
        ] + BASE_LIST_FIELDS


class DetailSerializer(BaseDetailSerializer):
    license_status_name = serializers.ReadOnlyField(source = 'get_license_status_display')

    class Meta(BaseDetailSerializer.Meta):
        model = Software
        fields = [
            'supplier', 'hardware_location', 'related_property', 'port', 'owner', 'license_status_name',
            'license_expired_date', 'manufacturer', 'name'
        ] + BASE_DETAIL_FIELDS


class CreateUpdateSerializer(BaseCreateUpdateSerializer):
    class Meta(BaseCreateUpdateSerializer.Meta):
        model = Software
        fields = [
            'supplier', 'hardware_location', 'related_property', 'port', 'owner', 'license_status',
            'license_expired_date', 'manufacturer', 'name'
        ] + BASE_CREATE_UPDATE_FIELDS
