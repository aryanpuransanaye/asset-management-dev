from rest_framework import serializers
from .models import IntangibleAsset
from core.serializer import *


class ListSerializer(BaseListSerializer):
    class Meta(BaseListSerializer.Meta):
        model = IntangibleAsset
        fields = [
           'id', 'supplier','location', 'usage', 'owner', 'name',
        ] + BASE_LIST_FIELDS


class DetailSerializer(BaseDetailSerializer):
    class Meta(BaseDetailSerializer.Meta):
        model = IntangibleAsset
        fields = [
            'supplier','location', 'usage', 'owner', 'name',
        ] + BASE_DETAIL_FIELDS


class CreateUpdateSerializer(BaseCreateUpdateSerializer):
    class Meta(BaseCreateUpdateSerializer.Meta):
        model = IntangibleAsset
        fields = [
            'supplier','location', 'usage', 'owner', 'name',
        ] + BASE_CREATE_UPDATE_FIELDS

