from rest_framework import serializers
from .models import DataAndInformation
from core.serializer import *


class ListSerializer(BaseListSerializer):

    confidentiality_display = serializers.CharField(source='get_confidentiality_level_display')
    class Meta(BaseListSerializer.Meta):
        model = DataAndInformation
        fields = [
            'id', 'name', 'location', 'usage',
            'owner', 'confidentiality_display', 'document_type',
        ] + BASE_LIST_FIELDS
        

class DetailSerializer(BaseDetailSerializer):

    confidentiality_display = serializers.CharField(source='get_confidentiality_level_display')
    
    class Meta(BaseDetailSerializer.Meta):
        model  = DataAndInformation
        fields = [
            'confidentiality_display',
            'name', 'location', 'usage', 'owner','document_type'
        ] + BASE_DETAIL_FIELDS


class CreateUpdateSerializer(BaseCreateUpdateSerializer):
    class Meta(BaseCreateUpdateSerializer.Meta):
        model = DataAndInformation
        fields = [
            'name', 'location', 'usage', 'confidentiality_level',
            'owner', 'version', 'document_type'
        ] + BASE_CREATE_UPDATE_FIELDS
