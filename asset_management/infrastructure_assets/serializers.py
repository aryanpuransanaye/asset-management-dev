from rest_framework import serializers
from .models import InfrastructureAssets
from core.serializer import *


class ListSerializer(BaseListSerializer):
    class Meta(BaseListSerializer.Meta):
        model = InfrastructureAssets
        fields = [
           'id', 'supplier','location', 'related_property', 'usage', 'owner', 'name',
        ] + BASE_LIST_FIELDS


class DetailSerializer(BaseDetailSerializer):
    class Meta(BaseDetailSerializer.Meta):
        model = InfrastructureAssets
        fields = [
            'supplier','location', 'related_property', 'usage', 'owner', 'name',
        ] + BASE_DETAIL_FIELDS


class CreateUpdateSerializer(BaseCreateUpdateSerializer):
    class Meta(BaseCreateUpdateSerializer.Meta):
        model = InfrastructureAssets
        fields = [
            'organization', 'sub_organization',
            'supplier','location', 'related_property', 'usage', 'owner', 'name',
        ] + BASE_CREATE_UPDATE_FIELDS
