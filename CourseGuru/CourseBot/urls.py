from django.conf.urls import include, url
from django.contrib import admin
from chatterbot.ext.django_chatterbot import urls as chatterbot_urls
from CourseBot.views import Bot

urlpatterns = [
     url(r'^$', Bot.as_view(), name='bot'),
     url(r'^admin/', include(admin.site.urls), name='admin'),
     url(r'^api/chatterbot/', include(chatterbot_urls, namespace='chatterbot')),
 
]