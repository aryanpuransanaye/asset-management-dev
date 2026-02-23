from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated
from .models import TicketRoom, Question, TicketCategory, TicketMessage
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from . import serializers
from django.shortcuts import get_object_or_404
import openpyxl, jdatetime
from django.http import HttpResponse
from django.db.models import Q, Count
from core.utils import apply_filters_and_sorting, get_accessible_queryset, set_paginator
from .utils import get_question_config, get_ticket_category_config

#ticket

class TicketSummaryAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        accessible_queryset = get_accessible_queryset(request, model=TicketRoom)

        ticket_details = accessible_queryset.aggregate(
            total_tickets_count =  Count('id'),
            open_tickets_count = Count('id', filter=Q(is_active=True)),
            closed_tickets_count = Count('id', filter=Q(is_active=False)),
        )

        summary_data = [
            {'label': 'تعداد کل تیکت‌ها', 'value': ticket_details['total_tickets_count'], 'color': 'blue'},
            {'label': 'تیکت‌های باز', 'value': ticket_details['open_tickets_count'], 'color': 'green'},
            {'label': 'تیکت‌های بسته شده', 'value': ticket_details['closed_tickets_count'], 'color': 'red'},
        ]

        return Response(summary_data, status=status.HTTP_200_OK)
    

class UserTicketListAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        
        accessable_ticket = TicketRoom.objects.filter(user=request.user)

        ticket_rooms = apply_filters_and_sorting(
            request, 
            ticket_category_config['sorting'], 
            ticket_category_config['filters'], 
            ticket_category_config['search'],  
            session_key='ticket_category',
            query_set=accessable_ticket
        ).select_related('user', 'access_level')

        paginator = set_paginator(request, ticket_rooms)
        serializer = serializers.TicketListSerializer(paginator['data'], many=True)
        return Response({
            'results':serializer.data,
            'total_pages': paginator['total_pages'],
            'current_page': paginator['current_page'],
            'total_items': paginator['total_items'],
        }, status=status.HTTP_200_OK)


class SupportTicketListAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        ticket_rooms = apply_filters_and_sorting(
            request, 
            ticket_category_config['sorting'], 
            ticket_category_config['filters'], 
            ticket_category_config['search'],  
            session_key='ticket_category',
            model=TicketRoom
        ).select_related('user', 'access_level')

        paginator = set_paginator(request, ticket_rooms)
        serializer = serializers.TicketListSerializer(paginator['data'], many=True)
        return Response({
            'results':serializer.data,
            'total_pages': paginator['total_pages'],
            'current_page': paginator['current_page'],
            'total_items': paginator['total_items'],
        }, status=status.HTTP_200_OK)
        

class TicketAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, ticket_id):

        accessible_queryset = get_accessible_queryset(request, model=TicketRoom)
        ticket = get_object_or_404(accessible_queryset, id = ticket_id)
        serializer = serializers.TicketDetailSerializer(ticket)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):

        serializer = serializers.TicketCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            target_user = serializer.validated_data.get('user')

            if target_user:
                ticket_owner = target_user
                user_info = f'ساخته شده برای {request.user.username}'
            else:
                ticket_owner = request.user
                user_info = f'ساخته شده برای خود کاربر'

            serializer.save(user = ticket_owner, access_level = ticket_owner.access_level, user_info_summary = user_info)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, ticket_id):
        
        accessible_queryset = get_accessible_queryset(request, model=TicketRoom)
        ticket = get_object_or_404(accessible_queryset, id = ticket_id)
        serializer = serializers.TicketCreateUpdateSerializer(ticket, data=request.data, partial = True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



#Ticket Category

ticket_category_config = get_ticket_category_config()
class TicketCategoryList(APIView):

    def get(self, request):

        questions = apply_filters_and_sorting(
            request, 
            ticket_category_config['sorting'], 
            ticket_category_config['filters'], 
            ticket_category_config['search'],  
            session_key='ticket_category',
            model=TicketCategory
        ).select_related('user', 'access_level')

        paginator = set_paginator(request, questions)
        serializer = serializers.QuestionsListSerializer(paginator['data'], many=True)
        return Response({
            'results':serializer.data,
            'total_pages': paginator['total_pages'],
            'current_page': paginator['current_page'],
            'total_items': paginator['total_items'],
        }, status=status.HTTP_200_OK)
    

class TicketCategoryAPIView(APIView):

    def get(self, request, ticket_category_id):
        
        message_category = get_object_or_404(TicketCategory, id = ticket_category_id)
        serializer = serializers.TicketCategoryDetailSerializer(message_category)

        return Response(serializer.data, status=status.HTTP_200_OK)


    def post(self, request):

        serializer = serializers.TicketCategoryCreateUpdateSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(user = request.user, access_level = request.user.access_level)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, ticket_category_id):

        message_category = get_object_or_404(TicketCategory, id = ticket_category_id)
        serializer = serializers.TicketCategoryCreateUpdateSerializer(message_category ,data=request.data, partial = True)
        if serializer.is_valid():
            serializer.save(user = request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *arg, **kwargs):

        ids_to_delete = request.data.get('ids', [])
        if not ids_to_delete:
            return Response({'errors': 'there is not id to delete'}, status=status.HTTP_400_BAD_REQUEST)
        
        ticket_category = TicketCategory.objects.filter(id__in = ids_to_delete)

        if not ticket_category.exists():
            return Response({'errors': "not found any object to delete"}, status=status.HTTP_404_NOT_FOUND)
        
    
        deleted_count, _ = ticket_category.delete()

        return Response({'message': f"{deleted_count} objects are deleted"}, status=status.HTTP_200_OK)



# QUESTIONS

question_config = get_question_config()

class QuestionListAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        
        questions = apply_filters_and_sorting(
            request, 
            question_config['sorting'], 
            question_config['filters'], 
            question_config['search'],  
            session_key='question',
            model=Question
        ).select_related('user', 'access_level')

        paginator = set_paginator(request, questions)
        serializer = serializers.QuestionsListSerializer(paginator['data'], many=True)
        return Response({
            'results':serializer.data,
            'total_pages': paginator['total_pages'],
            'current_page': paginator['current_page'],
            'total_items': paginator['total_items'],
        }, status=status.HTTP_200_OK)
    
class QuestionAPIView(APIView):

    permission_classes = [IsAuthenticated]


    def get(self, request, question_id):
        
        question = get_object_or_404(Question, id = question_id)
        serializer = serializers.QuestionsDetailSerializer(question)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        
        serializer = serializers.QuestionCreateUpdate(data = request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, access_level=request.user.access_level)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    def patch(self, request, question_id):

        question = get_object_or_404(Question, id = question_id)
        serializer = serializers.QuestionCreateUpdate(question, data = request.data, partial = True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

    def delete(self, request, *arg, **kwargs):

        ids_to_delete = request.data.get('ids', [])
        if not ids_to_delete:
            return Response({'errors': 'there is not id to delete'}, status=status.HTTP_400_BAD_REQUEST)
        
        questions = Question.objects.filter(id__in = ids_to_delete)

        if not questions.exists():
            return Response({'errors': "not found anything to delete"}, status=status.HTTP_404_NOT_FOUND)
        
    
        deleted_count, _ = questions.delete()

        return Response({'message': f"{deleted_count} things are deleted"}, status=status.HTTP_200_OK)


class TicketMessageAPIView(APIView):

    def get(self, request, ticket_id):
        
        accessible_queryset = get_accessible_queryset(request, model=TicketRoom)
        ticket_room = get_object_or_404(accessible_queryset, id = ticket_id)
        ticket_message = TicketMessage.objects.filter(ticket_room = ticket_room)

        serializer = serializers.TicketMessageSerializer(ticket_message, many = True, context={'request': request})

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request, ticket_id):

        accessible_queryset = get_accessible_queryset(request, model=Question)
        ticket_room = get_object_or_404(accessible_queryset, id=ticket_id)

        if ticket_room.user != request.user and not request.user.is_staff:
            return Response({"detail": "شما اجازه ارسال پیام در این تیکت را ندارید."}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = serializers.TicketMessageSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(sender=request.user, ticket_room=ticket_room)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)