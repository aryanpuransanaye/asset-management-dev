from rest_framework import serializers
import jdatetime


BASE_LIST_FIELDS = [

    'username', 'access_level_name', 'organization_name', 'sub_organization_name',
    'ipaddress', 'mac', 'os', 'vendor', 'created_at'
]

BASE_DETAIL_FIELDS = [
    'organization_name', 'sub_organization_name',
    'ipaddress', 'mac', 'os','vendor'
]

BASE_CREATE_UPDATE_FIELDS = [
    'ipaddress', 'mac', 'os','vendor', 'organization', 'sub_organization'
]


class BaseListSerializer(serializers.ModelSerializer):

    username = serializers.ReadOnlyField(source='user.username')
    access_level_name = serializers.ReadOnlyField(source='user.access_level.level_name')
    organization_name = serializers.ReadOnlyField(source='organization.name')
    sub_organization_name = serializers.ReadOnlyField(source='sub_organization.name')
    
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = None
        fields = []

    def get_created_at(self, obj):
        if obj.created_at:
            return obj.created_at.strftime('%Y/%m/%d')
        return None
    

class BaseDetailSerializer(serializers.ModelSerializer):

    organization_name = serializers.ReadOnlyField(source = 'organization.name')
    sub_organization_name = serializers.ReadOnlyField(source = 'sub_organization.name')

    class Meta:
        model = None
        fields = []


class BaseCreateUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = None
        fields = []
    
    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user:
            validated_data['user'] = request.user
            validated_data['access_level'] = request.user.access_level

        return super().create(validated_data)

    