from rest_framework import serializers
from .models import Organization, SubOrganization


class OrganizationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = [
            'id', 'name', 'description', 'address', 'phone_number',
            'email', 'website'
        ]


class OrganizationDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = [
            'name', 'description', 'address', 'phone_number',
            'email', 'website' 
        ]


class OrganizationCreateUpdate(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = [
            'name', 'description', 'address', 'phone_number',
            'email', 'website'
        ]




class SubOrganizationListSerializer(serializers.ModelSerializer):

    organization_name = serializers.ReadOnlyField(source = 'organization.name')
    email = serializers.ReadOnlyField(source = 'organization.email')
    phone_number = serializers.ReadOnlyField(source = 'organization.phone_number')

    class Meta:
        model = SubOrganization
        fields = [
            'id', 'organization', 'organization_name', 'name', 'address', 'email', 'phone_number'
        ]


class SubOrganizationDetailSerializar(serializers.ModelSerializer):

    organization_name = serializers.ReadOnlyField(source = 'organization.name')
    email = serializers.ReadOnlyField(source = 'organization.email')
    phone_number = serializers.ReadOnlyField(source = 'organization.phone_number')

    class Meta:
        model = SubOrganization
        fields = [
            'organization_name', 'name', 'address', 'email', 'phone_number'
        ]


class SubOrganizationCreateUpdateSerializer(serializers.ModelSerializer):
     class Meta:
        model = SubOrganization
        fields = [
            'organization', 'name', 'address'
        ]