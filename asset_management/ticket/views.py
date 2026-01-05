from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import TicketRoom, Question, MessageCategory, TicketMessage
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from . import serializers
from django.shortcuts import get_object_or_404
import openpyxl, jdatetime
from django.http import HttpResponse
from django.db.models import Q, Count
from core.utils import apply_filters_and_sorting, get_accessible_queryset


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

        summary_data = {
            {'label': 'تعداد کل تیکت‌ها', 'value': ticket_details['total_tickets_count'], 'color': 'blue'},
            {'label': 'تیکت‌های باز', 'value': ticket_details['open_tickets_count'], 'color': 'green'},
            {'label': 'تیکت‌های بسته شده', 'value': ticket_details['closed_tickets_count'], 'color': 'red'},
        }

        return Response(summary_data, status=status.HTTP_200_OK)
    

class TicketListAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        accessible_queryset = get_accessible_queryset(request, model=TicketRoom)
        tickets = accessible_queryset
        serializer = serializers.TicketListSerializer(tickets, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


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
            target_user = serializer.validate_data.get('user')

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



#message Category
class MessageCategoryList(APIView):

    def get(self, request):
        message_categories = MessageCategory.objects.all()
        serializer = serializers.MessageCategoryListSerializer(message_categories, many = True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    

class MessageCategoryAPIView(APIView):

    def get(self, request, message_category_id):
        
        message_category = get_object_or_404(MessageCategory, id = message_category_id)
        serializer = serializers.MessageCategoryDetailSerializer(message_category)

        return Response(serializer.data, status=status.HTTP_200_OK)


    def post(self, request):

        serializer = serializers.MessageCategoryCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user = request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, message_category_id):

        message_category = get_object_or_404(MessageCategory, id = message_category_id)
        serializer = serializers.MessageCategoryCreateUpdateSerializer(message_category ,data=request.data, partial = True)
        if serializer.is_valid():
            serializer.save(user = request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *arg, **kwargs):

        ids_to_delete = request.data.get('ids', [])
        if not ids_to_delete:
            return Response({'errors': 'there is not id to delete'}, status=status.HTTP_400_BAD_REQUEST)
        
        message_category = Question.objects.filter(id__in = ids_to_delete)

        if not message_category.exists():
            return Response({'errors': "not found any object to delete"}, status=status.HTTP_404_NOT_FOUND)
        
    
        deleted_count, _ = message_category.delete()

        return Response({'message': f"{deleted_count} objects are deleted"}, status=status.HTTP_200_OK)




# QUESTIONS
class QuestionListAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        
        questions = Question.objects.all()
        serializer = serializers.QuestionsListSerializer(questions, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
class QuestionAPIView(APIView):

    permission_classes = [IsAuthenticated]


    def get(self, request, question_id):
        
        question = get_object_or_404(Question, id = question_id)
        serializer = serializers.QuestionsDetailSerializer(question)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        
        serializer = serializers.QuestionCreateUpdate(data = request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
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