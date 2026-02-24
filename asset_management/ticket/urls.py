from django.urls import path
from . import views

urlpatterns = [

    ###TICKETS###

    #summary
    path('support-management/ticket/summary/', views.SupportTicketSummaryAPIView.as_view(), name='ticket-summary'),
    path('user/ticket/summary/', views.UserTicketSummaryAPIView.as_view(), name='ticket-summary'),

    #ticket list
    path('user/ticket/list/', views.UserTicketListAPIView.as_view(), name='ticket-list'),
    path('support-management/ticket/list/', views.SupportTicketListAPIView.as_view(), name='support-ticket-list'),

    #create or delete
    path('ticket/', views.TicketAPIView.as_view(), name = 'ticket'),

    #update or detail
    path('ticket/<int:ticket_id>/', views.TicketAPIView.as_view(), name='ticket'),


    ###Ticket CATEGORY###

    #question list
    path('ticket-category/list/', views.TicketCategoryList.as_view(), name='message-category-list'),

    #create or delete
    path('ticket-category/', views.TicketCategoryAPIView.as_view(), name='message-category'),

    #detail or update
    path('ticket-category/<int:ticket_category_id>/', views.TicketCategoryAPIView.as_view(), name='message-category'),


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
