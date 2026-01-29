from rest_framework import serializers
from .models import HumanResource
from core.serializer import *

class ListSerializer(BaseListSerializer):
    class Meta(BaseListSerializer.Meta):
        model = HumanResource
        fields = [
            'id', 'full_name', 'manager', 'start_date', 'end_date_of_work', 'organizational_unit', 'location',
            'administrative_position', 'personnel_id',
        ] + BASE_LIST_FIELDS


class DetailSerializer(BaseDetailSerializer):
    class Meta(BaseDetailSerializer.Meta):
        model = HumanResource
        fields = [
            'full_name', 'manager', 'start_date', 'end_date_of_work', 'organizational_unit', 'location',
            'administrative_position', 'personnel_id',
        ] + BASE_DETAIL_FIELDS


class CreateUpdateSerializer(BaseCreateUpdateSerializer):
    class Meta(BaseCreateUpdateSerializer.Meta):
        model = HumanResource
        fields = [
            'full_name', 'manager', 'start_date', 'end_date_of_work', 'organizational_unit', 'location',
            'administrative_position', 'personnel_id',
        ] + BASE_CREATE_UPDATE_FIELDS


