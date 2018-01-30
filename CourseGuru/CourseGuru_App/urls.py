from django.urls import path
from . import views

urlpatterns = [
 #   path('contact/', views.contact, name='contact')
    path('', views.index, name='index'),
    path('account/', views.account, name='account'),
    path('question/', views.question, name='question'),
    path('answer/', views.answer, name='answer'),
    
    
]