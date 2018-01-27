from django.db import models
from unittest.util import _MAX_LENGTH

# Create your models here.
#database set up in django
#===============================================================================
# class user(models.Model):
#     firstName = models.CharField(max_length=30)
#     lastName = models.CharField(max_length=50)
#     userId = models.CharField(max_length=8)
#     status = models.CharField(max_length=18)
# 
# class course(models.Model):
#     user = models.ForeignKey(user, on_delete=models.CASCADE)
#     courseName = models.CharField(max_length=50)
#     courseType = models.CharField(max_length=8)
#     
# class questions(models.Model):
#     user = models.ForeignKey(user, on_delete=models.CASCADE)
#     course = models.ForeignKey(course, on_delete=models.CASCADE)
#     title = models.CharField(max_length=80)
#     question = models.CharField(max_length=200)
# 
# class answers(models.Model):   
#     quesitonID = models.ForeignKey(questions, on_delete=models.CASCADE)
#     user = models.ForeignKey(user, on_delete=models.CASCADE)
#     title = models.CharField(max_length=80)
#     answer = models.CharField(max_length=400)
#     comments = models.CharField(max_length=200)
#     rating = models.BooleanField
#===============================================================================
