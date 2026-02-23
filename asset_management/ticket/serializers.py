from rest_framework import serializers
from .models import *
import jdatetime
from rest_framework import serializers
from .models import TicketRoom


class TicketListSerializer(serializers.ModelSerializer):

    assets_category_name = serializers.CharField(source='get_related_asset_category_display', read_only=True)
    priority_name = serializers.CharField(source='get_priority_display', read_only=True)
    
    username = serializers.ReadOnlyField(source='user.username')
    access_level_name = serializers.ReadOnlyField(source='access_level.level_name') 
    
    question_text = serializers.ReadOnlyField(source='question.text')

    class Meta:
        model = TicketRoom
        fields = [
            'id', 'username', 'user_info_summary', 'question', 'question_text', 
            'is_active', 'requires_password_reset', 'additional_details',
            'priority_name', 'access_level_name', 'category', 
            'related_asset_id', 'related_asset_category', 'assets_category_name', 'created_at'
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['status_text'] = "باز" if instance.is_active else "بسته"
        return representation
    
    def get_created_at(self, obj):
        if obj.created_at:
            return obj.created_at.strftime('%Y/%m/%d')
        return None



class TicketDetailSerializer(serializers.ModelSerializer):

    username = serializers.ReadOnlyField(source='user.username')
    question_text = serializers.ReadOnlyField(source='question.text')
    priority_name = serializers.CharField(source='get_priority_display', read_only=True)

    class Meta:
        model = TicketRoom
        fields = [
            'priority_name', 'question_text', 'is_active', 'username', 'created_at'
        ]

    def get_created_at(self, obj):
        if obj.created_at:
            return obj.created_at.strftime('%Y/%m/%d')
        return None
    

class TicketCreateUpdateSerializer(serializers.ModelSerializer):

    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False, allow_null=True)
    question = serializers.PrimaryKeyRelatedField(queryset=Question.objects.all(), allow_null=True, required=False)
    category = serializers.PrimaryKeyRelatedField(queryset=TicketCategory.objects.all(), allow_null=True, required=False)

    class Meta:
        model = TicketRoom
        fields = [
            'user',
            'question', 'is_active', 'requires_password_reset', 'additional_details',
            'priority', 'category', 'related_asset_id', 'related_asset_category'
        ]

    # def __init__(self, *args, **kwargs):
    #     user = kwargs.pop('user', None)
    #     super().__init__(*args, **kwargs)

    #     if user:
    #         self.fields['question'].queryset = Question.objects.filter(
    #             access_level__in=user.access_level.get_descendants(include_self=True)
    #         )
    #         self.fields['category'].queryset = TicketCategory.objects.filter(
    #             access_level__in=user.access_level.get_descendants(include_self=True)
    #         )


#MESSAGE CATEGORY
class TicketCategoryListSerializer(serializers.ModelSerializer):

    username = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = TicketCategory
        fields = [
            'id', 'username', 'text', 'created_at'
        ]

    def get_created_at(self, obj):
        if obj.created_at:
            return obj.created_at.strftime('%Y/%m/%d')
        return None


class TicketCategoryDetailSerializer(serializers.ModelSerializer):

    username = serializers.ReadOnlyField(source='user.username')
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = TicketCategory
        fields = [
            'text', 'created_at', 'username'
        ]

    def get_created_at(self, obj):
        if obj.created_at:
            return obj.created_at.strftime('%Y/%m/%d')
        return None
    

class TicketCategoryCreateUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = TicketCategory
        fields = [
            'text'
        ]

        # def validate_text(self, value):
        
        #     normalized_text = value.strip()
            
        #     instance = getattr(self, 'instance', None)
            
        #     mc = TicketCategory.objects.filter(text__iexact=normalized_text)
        #     if instance:
        #         mc = mc.exclude(pk=instance.pk)

        #     if mc.exists():
        #         raise serializers.ValidationError("این دسته بندی تیکت قبلاً در سیستم ثبت شده است.")
                
        #     return normalized_text


#QUESTIONS
class QuestionsListSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField()
    class Meta:
        model = Question
        fields = [
            'id', 'text', 'created_at', 
        ]

    def get_created_at(self, obj):
        if obj.created_at:
            return obj.created_at.strftime('%Y/%m/%d %H:%M:%S')
        return None


class QuestionsDetailSerializer(serializers.ModelSerializer):

    username = username = serializers.ReadOnlyField(source='user.username')
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = [
            'text', 'created_at', 'username'
        ]

    def get_created_at(self, obj):
        if obj.created_at:
            return obj.created_at.strftime('%Y/%m/%d')
        return None

    
class QuestionCreateUpdate(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = [
            'text'
        ]

    def validate_text(self, value):
    
        normalized_text = value.strip()
        
        instance = getattr(self, 'instance', None)
        
        qs = Question.objects.filter(text__iexact=normalized_text)
        if instance:
            qs = qs.exclude(pk=instance.pk)

        if qs.exists():
            raise serializers.ValidationError("این سوال قبلاً در سیستم ثبت شده است.")
            
        return normalized_text

#TICKET MESSAGE

class TicketMessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.ReadOnlyField(source = 'user.username')
    is_me = serializers.SerializerMethodField()
    class Meta:

        model = TicketMessage
        fields = ['id', 'content', 'created_at', 'sender', 'ticket_room', 'is_me', 'sender_username']
        read_only_fields = ['sender', 'ticket_room']

    def get_is_me(self, obj):

        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.sender == request.user
        return False
