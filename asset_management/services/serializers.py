from rest_framework import serializers
from .models import Services
from core.serializer import *


class ListSerializer(BaseListSerializer):
    class Meta(BaseListSerializer.Meta):
        model = Services
        fields = [
            'id', 'hardware_location', 'port', 'related_property', 'build_number_os', 'name',
        ] + BASE_LIST_FIELDS


class DetailSerializer(BaseDetailSerializer):
    class Meta(BaseDetailSerializer.Meta):
        model = Services
        fields = [
            'hardware_location', 'port', 'related_property', 'build_number_os', 'name',
        ] + BASE_DETAIL_FIELDS


class CreateUpdateSerializer(BaseCreateUpdateSerializer):
    class Meta(BaseCreateUpdateSerializer.Meta):
        model = Services
        fields = [
            'hardware_location', 'port', 'related_property', 'build_number_os', 'name',
        ] + BASE_CREATE_UPDATE_FIELDS
