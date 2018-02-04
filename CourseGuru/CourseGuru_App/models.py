from django.db import models
from email.policy import default

# Create your models here.
#database set up in django
class user(models.Model):
     firstName = models.CharField(max_length=30)
     lastName = models.CharField(max_length=50)
     #get rid of userId its auto gen by django 
     password = models.CharField(max_length=8)
     status = models.CharField(max_length=18)
 
class course(models.Model):
     user = models.ForeignKey(user, on_delete=models.CASCADE)
     courseName = models.CharField(max_length=50)
     courseType = models.CharField(max_length=8)
     
class questions(models.Model):
     user = models.ForeignKey(user, on_delete=models.CASCADE)
     course = models.ForeignKey(course, on_delete=models.CASCADE)
     question = models.CharField(max_length=200)
 
class answers(models.Model):   
    #edit variable below
     question = models.ForeignKey(questions, on_delete=models.CASCADE)
     user = models.ForeignKey(user, on_delete=models.CASCADE)
     answer = models.CharField(max_length=400)
     comments = models.CharField(max_length=200)
     rating = models.IntegerField(default=0)
     
class category(models.Model):
    intent = models.CharField(max_length=50)
    entities = models.CharField(max_length=150)
    
class botanswers(models.Model):
    category = models.ForeignKey(category, on_delete=models.CASCADE)
    answer = models.CharField(max_length=400)
    rating = models.IntegerField(default=0)
    
class keywords(models.Model):
    word = models.CharField(max_length=50)
    common_name = models.CharField(max_length=50)
    
class courseinfo(models.Model):
    keyword_common_name = models.CharField(max_length=50)
    syllabus_data = models.CharField(max_length=50)
    course_id = models.CharField(max_length=20)
    
    
    
    
    
    
