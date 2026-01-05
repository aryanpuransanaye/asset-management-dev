from django.urls import path
from . import views

urlpatterns = [

    ###TICKETS###

    #summary
    path('ticket/summary/', views.TicketSummaryAPIView.as_view(), name='ticket-summary'),

    #ticket list
    path('ticket/list/', views.TicketListAPIView.as_view(), name='ticket-list'),
    #create
    path('ticket/', views.TicketAPIView.as_view(), name = 'ticket'),

    #update or detail
    path('ticket/<int:ticket_id>/', views.TicketAPIView.as_view(), name='ticket'),


    ###MESSAGE CATEGORY###

    #question list
    path('message-category/list/', views.MessageCategoryList.as_view(), name='message-category-list'),

    #create or delete
    path('message-category/', views.MessageCategoryAPIView.as_view(), name='message-category'),

    #detail or update
    path('message-category/<int:question_id>/', views.MessageCategoryAPIView.as_view(), name='message-category'),


    ###QUESTION###

    #question list
    path('question/list/', views.QuestionListAPIView.as_view(), name='question-list'),

    #create or delete
    path('question/', views.QuestionAPIView.as_view(), name='question'),

    #detail or update
    path('question/<int:question_id>/', views.QuestionAPIView.as_view(), name='question'),


    ###TICKET MESSAGE###
    path('ticket-message/<int:ticket_id>/', views.TicketMessageAPIView.as_view(), name='ticket-message'),
    # path('ticket-message/<int:question_id>/', views.QuestionAPIView.as_view(), name='question'),


]
