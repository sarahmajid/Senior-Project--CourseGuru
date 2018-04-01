from django.urls import path
from django.urls import include
from . import views
from django.contrib.auth.views import password_reset, password_reset_done, password_reset_confirm, password_reset_complete 

urlpatterns = [
    path('', views.index, name='index'),
    path('account/', views.account, name='account'),
    path('question/', views.question, name='question'),
    path('answer/', views.answer, name='answer'),
    path('publish/', views.publish, name='publish'),
    path('publishAnswer/', views.publishAnswer, name='publishAnswer'),
    path('publishCourse/', views.publishCourse, name='publishCourse'),
    path('courses/', views.courses, name='courses'),
    path('roster/', views.roster, name='roster'),
    path('chatAnswer/', views.chatAnswer, name='chatAnswer'),
    path('voting/', views.voting, name='voting'),
    path('uploadDocument/', views.uploadDocument, name='uploadDocument'),
    path('editAccount/', views.editAccount, name='editAccount'),
    path('reset-password/', password_reset, {'template_name': 'CourseGuru_App/passwordReset.html'}),
    path('reset-password/done/', password_reset_done,  {'template_name': 'CourseGuru_App/emailedPassMessage.html'}, name='password_reset_done'),
    path('reset-password/confirm/<uidb64>/<token>/', password_reset_confirm,  {'template_name': 'CourseGuru_App/newPassword.html'}, name='password_reset_confirm'),
    path('reset-password/complete/', password_reset_complete, {'template_name': 'CourseGuru_App/passwordResetComplete.html'}, name='password_reset_complete'),
]