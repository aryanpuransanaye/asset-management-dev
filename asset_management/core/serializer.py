from rest_framework import serializers
import jdatetime
from organization.models import Organization, SubOrganization

BASE_LIST_FIELDS = [

    'user', 'access_level', 'organization', 'sub_organization',
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

    user = serializers.ReadOnlyField(source='user.username', label='نام کاربری')
    access_level = serializers.ReadOnlyField(source='user.access_level.level_name', label='سطح دسترسی')
    organization = serializers.ReadOnlyField(source='organization.name', label='سازمان')
    sub_organization = serializers.ReadOnlyField(source='sub_organization.name', label='زیرسازمان')
    
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = None
        fields = []

    def get_created_at(self, obj):
        if obj.created_at:
            return obj.created_at.strftime('%Y/%m/%d')
        return None
    
    @classmethod
    def get_active_columns(cls):
       
        model = cls.Meta.model
        target_fields = getattr(cls.Meta, 'fields', [])
        
        columns = []
        for field_name in target_fields:
            try:
              
                label = model._meta.get_field(field_name).verbose_name
            except:
                label = field_name.replace('_', ' ').capitalize()
            
            columns.append({
                'key': field_name,
                'label': label
            })
            
        return columns
    

class BaseDetailSerializer(serializers.ModelSerializer):

    organization = serializers.ReadOnlyField(source = 'organization.name')
    sub_organization = serializers.ReadOnlyField(source = 'sub_organization.name')

    class Meta:
        model = None
        fields = []


class BaseCreateUpdateSerializer(serializers.ModelSerializer):

    organization = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.all()
    )
    sub_organization = serializers.PrimaryKeyRelatedField(
        queryset=SubOrganization.objects.all()
    )
    class Meta:
        model = None
        fields = []


    @classmethod
    def get_form_config(cls):
        config = []
        model = cls.Meta.model
        fields_to_create = getattr(cls.Meta, 'fields', [])

        for field_name in fields_to_create:
            if field_name in ['id', 'user', 'access_level', 'created_at', 'updated_at']:
                continue
            try:
                model_field = model._meta.get_field(field_name)
                field_data = {
                    'key': field_name,
                    'label': model_field.verbose_name,
                    'required': not model_field.blank,
                    'type': model_field.get_internal_type(),
                }

                if model_field.choices:
                    field_data['type'] = 'ChoiceField'
                    field_data['options'] = [{'value': k, 'label': v} for k, v in model_field.choices]
                
                elif model_field.is_relation:
                    field_data['type'] = 'ForeignKey'
                    related_model = model_field.related_model
                    
                    if field_name == 'sub_organization':
                        raw_data = related_model.objects.all().values('id', 'name', 'organization_id')
                        field_data['options'] = [
                            {'value': item['id'], 'label': item['name'], 'parent_id': item['organization_id']} 
                            for item in raw_data
                        ]
                    else:
                        raw_data = related_model.objects.all().values('id', 'name')
                        field_data['options'] = [
                            {'value': item['id'], 'label': item['name']} for item in raw_data
                        ]
                config.append(field_data)
                
            except: continue

        return config
    
    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user:
            validated_data['user'] = request.user
            validated_data['access_level'] = request.user.access_level

        return super().create(validated_data)

    