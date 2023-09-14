from django.contrib import admin
from django.urls import path
from chatbot import views, views_chat

urlpatterns = [
    path("", views.index, name='home'),
    path('chatbot', views_chat.chatbot, name='chatbot'),
]
