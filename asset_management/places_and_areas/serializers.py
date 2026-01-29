from rest_framework import serializers
from .models import PlacesAndArea
from core.serializer import *


class ListSerializer(BaseListSerializer):
    class Meta(BaseListSerializer.Meta):
        model = PlacesAndArea
        fields = [
           'id', 'location', 'usage', 'owner', 'name',
        ] + BASE_LIST_FIELDS


class DetailSerializer(BaseDetailSerializer):
    class Meta(BaseDetailSerializer.Meta):
        model = PlacesAndArea
        fields = [
            'location', 'usage', 'owner', 'name',
        ] + BASE_DETAIL_FIELDS


class CreateUpdateSerializer(BaseCreateUpdateSerializer):
    class Meta(BaseCreateUpdateSerializer.Meta):
        model = PlacesAndArea
        fields = [
           'location', 'usage', 'owner', 'name',
        ] + BASE_CREATE_UPDATE_FIELDS
