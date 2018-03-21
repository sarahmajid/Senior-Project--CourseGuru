"""CourseGuru URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import include, path
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    path('', include('CourseGuru_App.urls')),
    path('/account/', include('CourseGuru_App.urls')),
    path('/question/', include('CourseGuru_App.urls')),
    path('/answer/', include('CourseGuru_App.urls')),
    path('/publish/', include('CourseGuru_App.urls')), 
    path('/publishAnswer/', include('CourseGuru_App.urls')),
    path('/publishCourse/', include('CourseGuru_App.urls')),
    path('/courses/', include('CourseGuru_App.urls')),  
    path('/roster/', include('CourseGuru_App.urls')), 
    path('/chatAnswer/', include('CourseGuru_App.urls')), 
    path('/voting/', include('CourseGuru_App.urls')),
    path('admin/', admin.site.urls),
    path('/uploadDocument/', include('CourseGuru_App.urls')),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
