from django.urls import path
from . import views

urlpatterns = [
#    path('', views.index, name='index'),
    path('loginform/', views.login, name = 'login'),
    path('', views.index, name='index'),
    path('account/', views.account, name='account'),
    path('question/', views.question, name='question'),
    path('answer/', views.answer, name='answer'),
    path('parse/', views.parse, name='parse'),
    path('chatbot/', views.chatbot, name='chatbot'),

]