from rest_framework import serializers
from .models import ActiveDirectory, ActiveDirectoryUsers
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
    password = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = ActiveDirectory
        fields = [
            'id', 'server_address', 'domain_name', 
            'username', 'password', 'port', 'search_base'
        ]
        # extra_kwargs = {
        #     'password': {'write_only': T},
        # }

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password:
            instance.password = password

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

class CreateScannedADUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'active_directory_server']

    def create(self, validated_data):
    
        user = ActiveDirectoryUsers.objects.create_user(**validated_data)
        user.set_unusable_password()
        user.save()
        return user