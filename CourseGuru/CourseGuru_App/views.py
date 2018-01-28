from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render
import json
from urllib.request import urlopen
import psycopg2
from django.http.response import HttpResponseRedirect

#importing models 
from CourseGuru_App.models import user
from CourseGuru_App.models import course
from CourseGuru_App.models import questions
from CourseGuru_App.models import answers



# Function to populate Main page
def index(request):
    if request.method == "POST":
        nq = request.POST.get('NQ')
        questions.objects.create(question = nq, course_id = 1, user_id = 1)
        return HttpResponseRedirect('/')
    qData = questions.objects.all()
    return render(request, 'CourseGuru_App/index.html', {'content': qData})

# Function to populate Answers page
def answer(request):
#    if request.method=='GET':
    qid = request.GET.get('id', '') 
    if request.method == "POST":
        ans = request.POST.get('ANS')
        answers.objects.create(answer = ans, user_id = 1, question_id = qid)
        return HttpResponseRedirect('/answer/?id=%s' % qid)
    aData = answers.objects.filter(question_id = qid)
    qData = questions.objects.get(id = qid)

    return render(request, 'CourseGuru_App/answer.html', {'answers': aData, 'Title': qData})



#    ---Canvas code---
#    url = (urlopen('https://canvas.wayne.edu/api/v1/courses').read()
#    response = urlopen('https://canvas.wayne.edu/api/v1/courses')
#    data = json.load(response)