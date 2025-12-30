from rest_framework import serializers
from .models import Hardware
from core.serializer import BaseListSerializer, BaseDetailSerializer, BaseCreateUpdateSerializer, BASE_LIST_FIELDS, BASE_DETAIL_FIELDS, BASE_CREATE_UPDATE_FIELDS


class ListSerializer(BaseListSerializer):
    class Meta(BaseListSerializer.Meta):
        model = Hardware
        fields = [
            'id', 'supplier', 'hardening', 'vulner_status', 'status', 'hostname', 'port',
            'model', 'manufacturer', 'hardware_type', 'name',
        ] + BASE_LIST_FIELDS


class DetailSerializer(BaseDetailSerializer):
    class Meta(BaseDetailSerializer.Meta):
        model = Hardware
        fields = [
            'supplier', 'hardening', 'vulner_status', 'status', 'hostname', 'port',
            'model', 'manufacturer', 'hardware_type', 'name',
        ] + BASE_DETAIL_FIELDS 


class CreateUpdateSerializer(BaseCreateUpdateSerializer):
    class Meta(BaseCreateUpdateSerializer.Meta):
        model = Hardware
        fields = [
            'supplier', 'hardening', 'vulner_status', 'status', 'hostname', 'port',
            'model', 'manufacturer', 'hardware_type', 'name'
        ] + BASE_CREATE_UPDATE_FIELDS
