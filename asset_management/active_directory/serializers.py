from rest_framework import serializers
from .models import ActiveDirectory
from accounts.models import User

# class ListSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ActiveDirectory
#         fields = [
#             'id', 'server_address', 'domain_name',
#             'username', 'password', 'port', 'search_base'
#         ]


# class DetailSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ActiveDirectory
#         fields = [
#             'server_address', 'domain_name',
#             'username', 'password', 'port', 'search_base'
#         ]


# class CreateUpdateSerializer(serializers.ModelSerializer)


class ActiveDirectorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ActiveDirectory
        fields = [
            'id', 'server_address', 'domain_name', 
            'username', 'password', 'port', 'search_base'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
        }

class CreateScannedADUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'active_directory_server']

    def create(self, validated_data):
    
        user = User.objects.create_user(**validated_data)
        user.set_unusable_password()
        user.save()
        return user