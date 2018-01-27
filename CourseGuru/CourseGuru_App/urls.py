from django.urls import path
from . import views

urlpatterns = [
 #   path('contact/', views.contact, name='contact')
    path('', views.index, name='index'),
    path('QAP/', views.QAP, name = 'QAP')
]