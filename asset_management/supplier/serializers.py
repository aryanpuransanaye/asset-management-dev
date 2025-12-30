from rest_framework import serializers
from .models import Supplier
from core.serializer import *


class ListSerializer(BaseListSerializer):
    class Meta(BaseListSerializer.Meta):
        model = Supplier
        fields = [
            'id', 'suppliers_name', 'suppliers_location', 'email', 'manager_name',
            'manager_mobile_number', 'support_name', 'support_mobile_number',
            'company_mobile_number', 'related_property',
        ] + BASE_LIST_FIELDS


class DetailSerializer(BaseDetailSerializer):
    class Meta(BaseDetailSerializer.Meta):
        model = Supplier
        fields = [
            'suppliers_name', 'suppliers_location', 'email', 'manager_name',
            'manager_mobile_number', 'support_name', 'support_mobile_number',
            'company_mobile_number', 'related_property',
        ] + BASE_DETAIL_FIELDS


class CreateUpdateSerializer(BaseCreateUpdateSerializer):
    class Meta(BaseCreateUpdateSerializer.Meta):
        model = Supplier
        fields = [
            'organization', 'sub_organization',
            'suppliers_name', 'suppliers_location', 'email', 'manager_name',
            'manager_mobile_number', 'support_name', 'support_mobile_number',
            'company_mobile_number', 'related_property',
        ] + BASE_CREATE_UPDATE_FIELDS


