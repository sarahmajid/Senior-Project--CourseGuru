from django.urls import path
from . import views
from CourseGuru_App import views

urlpatterns = [
#    path('', views.index, name='index'),
    path('', views.index, name='index'),
    path('account/', views.account, name='account'),
    path('question/', views.question, name='question'),
    path('answer/', views.answer, name='answer'),
    path('parse/', views.parse, name='parse'),
    path('publish/', views.publish, name='publish'),
    path('publishAnswer/', views.publishAnswer, name='publishAnswer'),
    path('chatbot/', views.chatbot, name='chatbot'),

]