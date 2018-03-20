from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import default


#from email.policy import default

# Create your models here.
#database set up in django
    
status = models.CharField(max_length=18, default='Student')
status.contribute_to_class(User, 'status')

class course(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    courseName = models.CharField(max_length=50)
    courseType = models.CharField(max_length=30)
    
class courseusers(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(course, on_delete=models.CASCADE)    
     
class questions(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(course, on_delete=models.CASCADE)
    question = models.CharField(max_length=200)
    date = models.DateTimeField(auto_now_add=True)
    comment = models.CharField(max_length=400)
    category = models.CharField(max_length=20)
 
class answers(models.Model):   
    #edit variable below
    question = models.ForeignKey(questions, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    answer = models.CharField(max_length=5000)
    comments = models.CharField(max_length=200)
    rating = models.IntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default = False)

    class meta:
        ordering = ['rating']
 
class userratings(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    answer = models.ForeignKey(answers, on_delete=models.CASCADE)
    rating = models.SmallIntegerField(default=1)
 
class comments(models.Model):
    #edit variable below
    question = models.ForeignKey(questions, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.CharField(max_length=300)
    date = models.DateTimeField(auto_now_add=True) 

class category(models.Model):
    intent = models.CharField(max_length=50)
    
class botanswers(models.Model):
    category = models.ForeignKey(category, on_delete=models.CASCADE)
    course = models.ForeignKey(course, on_delete=models.CASCADE)
    answer = models.CharField(max_length=5000)
    rating = models.IntegerField(default=0)
    entities = models.CharField(max_length=5000)

    
    
class keywords(models.Model):
    categoryKeyWords = models.CharField(max_length=100)
    subCategoryKeyWords = models.CharField(max_length=100) 
   
    
class courseinfo(models.Model):
    fkCourseId = models.ForeignKey(course, on_delete=models.CASCADE)
    category = models.CharField(max_length=50)
    entities = models.CharField(max_length=200)    
    infoData = models.TextField()
    courseId = models.CharField(max_length = 15)

    
    
    
