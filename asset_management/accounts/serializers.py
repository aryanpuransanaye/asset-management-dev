from rest_framework import serializers
from .models import User, AccessLevel
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
import jdatetime
from .utils import get_client_ip

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        data['username'] = self.user.username
        data['email'] = self.user.email
        data['is_staff'] = self.user.is_staff
        data['is_superuser'] = self.user.is_superuser
        data['is_active'] = self.user.is_active

        all_perms = self.user.get_all_permissions()
        data['permissions'] = [p for p in all_perms if p.startswith('accounts.')] if not data['is_superuser'] else ['*']

        user = self.user
        user.ip_login = get_client_ip(request=self.context.get('request'))
        user.last_login = jdatetime.date.today()
        user.save(update_fields=['ip_login', 'last_login'])
        
        return data
    

class AccessLevelSerliazlizer(serializers.ModelSerializer):
    class Meta:
        
        model = AccessLevel
        fields = ['id', 'level_name', 'parent', 'main_level']

        def validete_parent(self, value):
            return value


class GroupSimpleSerializer(serializers.ModelSerializer):
    users_count = serializers.IntegerField(read_only=True)
    permissions_count = serializers.IntegerField(read_only=True)
    class Meta:
        model = Group
        fields = ['id', 'name', 'users_count', 'permissions_count']


class PermissionsSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'name', 'codename']    


class UserSerializer(serializers.ModelSerializer):

    groups = GroupSimpleSerializer(many=True, read_only=True)
    user_permissions = PermissionsSimpleSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone_number', 'first_name', 'last_name', 'gender', 'groups', 'user_permissions']
        read_only_fields = fields


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=6)
    email = serializers.EmailField(required=False, allow_blank=True, allow_null=True, default="")
    groups = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all(), many=True, required=False)
    user_permissions = serializers.PrimaryKeyRelatedField(queryset=Permission.objects.all(), many=True, required=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'gender', 'password', 'groups', 'user_permissions', 'is_staff', 'is_active']

    def create(self, validated_data):
        groups_data = validated_data.pop('groups', [])
        permissions_data = validated_data.pop('user_permissions', [])

        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)

        if groups_data:
            user.groups.set(groups_data)
        if permissions_data:
            user.user_permissions.set(permissions_data)

        return user


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'phone_number', 'email', 'gender', 'is_staff', 'is_active']


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number', 'email', 'gender']

    def update(self, instance, validated_data):
       
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.gender = validated_data.get('gender', instance.gender)
        
        email = validated_data.get('email')
        if email == "" or email is None:
            instance.email = None
        else:
            instance.email = email

        instance.save()
        return instance

  

class ChangePasswordSerializer(serializers.Serializer):
    
    current_password = serializers.CharField(required=True, style={'input_type': 'password'})
    new_password = serializers.CharField(required=True, style={'input_type': 'password'})
    new_password_confirm = serializers.CharField(required=True, style={'input_type': 'password'})
    
    def validate(self, data):
        
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError({"new_password_confirm": "رمز عبور جدید و تکرار آن مطابقت ندارند."})
        
        user = self.context['request'].user
        if not user.is_authenticated:
             raise serializers.ValidationError("کاربر احراز هویت نشده است.")
        
        if not user.check_password(data['current_password']):
            raise serializers.ValidationError({"current_password": "رمز عبور فعلی وارد شده اشتباه است."})
        
        if data['current_password'] == data['new_password']:
             raise serializers.ValidationError({"new_password": "رمز عبور جدید نمی‌تواند با رمز عبور فعلی یکسان باشد."})
             
        return data
    
    def update(self, instance, validated_data):
        instance.set_password(validated_data['new_password'])
        instance.save()
        return instance


class ChangeUserPasswordByAdmin(serializers.Serializer):

    new_password = serializers.CharField(required=True, style={'input_type': 'password'})
    new_password_confirm = serializers.CharField(required=True, style={'input_type': 'password'})

    def validate(self, data):
        
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError({'new_password_confim': 'رمز عبور جدید و تکرار آن مطابقت ندارند'})
        
        user = self.context.get('user_instance')
        if user and user.check_password(data['new_password']):
            raise serializers.ValidationError({'new_password': 'رمز عبور جدید نمی‌تواند مشابه رمز فعلی باشد'})
        
        try:
            validate_password(data['new_password'], user)
        except Exception as e:
            raise serializers.ValidationError({'new_password': list(e.messages)})

        return data
    
    def update(self, instance, validated_data):
        instance.set_password(validated_data['new_password'])
        instance.save()
        return instance



class GroupAssignmentSerializer(serializers.Serializer):
    group_ids = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(),
        many=True,
        required=True
    )

class UserPermissionAssignmentSerializer(serializers.Serializer):
    
    permission_ids = serializers.PrimaryKeyRelatedField(
        queryset=Permission.objects.all(),
        many=True,                       
        required=True,
        write_only=True,
        label="Permission IDs"
    )


class PermissionDetailSerializer(serializers.ModelSerializer):
    # app_label = serializers.SerializerMethodField() 
    custom_user_set = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Permission
        fields = ['id', 'name', 'codename', 'custom_user_set'] #'user_set' to show users with this permission

    def get_app_label(self, obj):
        return obj.content_type.app_label



class GroupsDetailSerializer(serializers.ModelSerializer):
    custom_user_set = UserSerializer(many=True, read_only=True)
    users_count = serializers.IntegerField(read_only=True)
    group_permissions = PermissionsSimpleSerializer(source='permissions', many=True, read_only=True)

    class Meta:
        model = Group
        fields = ['id', 'name', 'custom_user_set', 'users_count', 'group_permissions']  # 'user_set' to show users in the group


class GroupsCreateSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True, required=False)
    permissions = serializers.PrimaryKeyRelatedField(queryset=Permission.objects.all(), many=True, required=False)

    class Meta:
        model = Group
        fields = ['id', 'name', 'user', 'permissions']

    def create(self, validated_data):
        users_data = validated_data.pop('user', [])
        permissions_data = validated_data.pop('permissions', [])

        group = Group.objects.create(**validated_data)

        if users_data:
            group.custom_user_set.set(users_data)
        if permissions_data:
            group.permissions.set(permissions_data)

        return group



class GroupsUpdateSerializer(serializers.ModelSerializer):

    permissions = serializers.PrimaryKeyRelatedField(
        queryset=Permission.objects.all(),
        many=True,
        required=False,
        write_only=True
    )


    users = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=True,
        required=False,
        source='user_set',
        write_only=True
    )

    group_permissions = PermissionDetailSerializer(
        source='permissions', 
        many=True, 
        read_only=True
    )

    class Meta:
        model = Group
        fields = ['name', 'permissions', 'users', 'group_permissions']

    def update(self, instance, validated_data):
        permissions_data = validated_data.pop('permissions', None)
        users_data = validated_data.pop('user_set', None)

        instance.name = validated_data.get('name', instance.name)
        instance.save()

        if permissions_data is not None:
            instance.permissions.set(permissions_data)

        if users_data is not None:
           instance.custom_user_set.set(users_data)

        return instance

class UserUpdateSerializer(serializers.ModelSerializer):
    

    groups_input = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(),
        many=True,
        required=False,
        write_only=True
    )

    user_permissions_input = serializers.PrimaryKeyRelatedField(
        queryset=Permission.objects.all(),
        many=True,
        required=False,
        write_only=True
    )
   
    groups = GroupsDetailSerializer(many=True, read_only=True)
    
 
    user_permissions = PermissionDetailSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'phone_number', 
            'first_name', 'last_name', 'is_active', 'is_staff',
            'groups_input', 'user_permissions_input', 'gender',
            'groups', 'user_permissions' 
        ]
        read_only_fields = ['id']

    
    def update(self, instance, validated_data):
        
        groups_data = validated_data.pop('groups_input', None)
        permissions_data = validated_data.pop('user_permissions_input', None)
        
        instance = super().update(instance, validated_data) 
        
        if groups_data is not None:
            instance.groups.set(groups_data)
            
        if permissions_data is not None:
            instance.user_permissions.set(permissions_data)
            
        return instance

    
    def validate(self, data):
       
        email = data.get('email')
        if email and User.objects.filter(email=email).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError({"email": "این ایمیل قبلاً ثبت شده است."})
            
        phone_number = data.get('phone_number')
        if phone_number and User.objects.filter(phone_number=phone_number).exclude(id=self.instance.id).exists():
             raise serializers.ValidationError({"phone_number": "این شماره تلفن قبلاً ثبت شده است."})
        
        return data