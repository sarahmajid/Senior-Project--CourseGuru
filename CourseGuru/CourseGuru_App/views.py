from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render
import json
from urllib.request import urlopen
import psycopg2
from django.http.response import HttpResponseRedirect

#testing forum bot
import requests
import json

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
        intent = cbAnswer(nq)
        
        questions.objects.filter(id=4).update(question=intent)
        #=======================================================================
        # try:
        #     r = request.get('https://westus.api.cognitive.microsoft.com/luis/v2.0/apps/ee579764-9ebf-44fd-a904-e3353a691b7e?subscription-key=a0d35b39c3874ec1b05ff5bececfa7eb&verbose=true&timezoneOffset=0&q=%s' % nq, '')
        #     luisStr = json.loads(r.text)
        #     luisStr = luisStr['topScoringIntent']['intent']
        #     questions.objects.filter(id=3).update(question=luisStr)
        # except Exception as e:
        #     questions.objects.filter(id=3).update(question='failed')
        #=======================================================================
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

def chatbot(request):
    return render(request, 'CourseGuru_App/botchat.html',)

def cbAnswer(nq):
    r = requests.get('LUISENDPOINTq=%s' % nq)
    luisStr = json.loads(r.text)
    intent = luisStr['topScoringIntent']['intent']
    return(intent)

#    ---Canvas code---
#    url = (urlopen('https://canvas.wayne.edu/api/v1/courses').read()
#    response = urlopen('https://canvas.wayne.edu/api/v1/courses')
#    data = json.load(response)