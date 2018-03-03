from django.urls import path
from . import views

urlpatterns = [
#    path('', views.index, name='index'),
    path('', views.index, name='index'),
    path('account/', views.account, name='account'),
    path('question/', views.question, name='question'),
    path('answer/', views.answer, name='answer'),
    path('parse/', views.parse, name='parse'),
    path('publish/', views.publish, name='publish'),
    path('publishAnswer/', views.publishAnswer, name='publishAnswer'),
    path('publishCourse/', views.publishCourse, name='publishCourse'),
    path('chatbot/', views.chatbot, name='chatbot'),
    path('courses/', views.courses, name='courses'),
    path('roster/', views.roster, name='roster'),
    path('chatAnswer/', views.chatAnswer, name='chatAnswer'),

]