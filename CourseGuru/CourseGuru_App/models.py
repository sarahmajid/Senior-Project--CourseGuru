from django.db import models
from django.forms import ModelForm
from django import forms
from django.db.models.signals import post_save
from django.dispatch import receiver
from email.policy import default
from datetime import timezone
from django.contrib.auth.models import User

# Create your models here.
#database set up in django

class user(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=18)
    
class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
            model = User
            fields = ["username", "password", "first_name", "last_name", "email" ]

class UserProfileForm(forms.ModelForm):
        
        class Meta:
                model = user
                fields = ['status']

class course(models.Model):
    user = models.ForeignKey(user, on_delete=models.CASCADE)
    courseName = models.CharField(max_length=50)
    courseType = models.CharField(max_length=8)
     
class questions(models.Model):
    user = models.ForeignKey(user, on_delete=models.CASCADE)
    course = models.ForeignKey(course, on_delete=models.CASCADE)
    question = models.CharField(max_length=200)
    date = models.CharField(max_length=20)
 
class answers(models.Model):   
    #edit variable below
     question = models.ForeignKey(questions, on_delete=models.CASCADE)
     user = models.ForeignKey(user, on_delete=models.CASCADE)
     answer = models.CharField(max_length=400)
     comments = models.CharField(max_length=200)
     rating = models.IntegerField(default=0)
     date = models.CharField(max_length=20, null=True)

     class meta:
        ordering = ['-rating']
 
class comments(models.Model):
    #edit variable below
    question = models.ForeignKey(questions, on_delete=models.CASCADE)
    user = models.ForeignKey(user, on_delete=models.CASCADE)
    comment = models.CharField(max_length=300)
    date = models.CharField(max_length=20) 

class category(models.Model):
    intent = models.CharField(max_length=50)
    
class botanswers(models.Model):
    category = models.ForeignKey(category, on_delete=models.CASCADE)
    answer = models.CharField(max_length=400)
    rating = models.IntegerField(default=0)
    entities = models.CharField(max_length=200)
    
class keywords(models.Model):
    word = models.CharField(max_length=50)
    common_name = models.CharField(max_length=50)
    
class courseinfo(models.Model):
    keyword_common_name = models.CharField(max_length=50)
    syllabus_data = models.CharField(max_length=50)
    course_id = models.CharField(max_length=20)
    
    
    
    
    
    
