
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
from CourseGuru_App.models import category
from CourseGuru_App.models import botanswers
from test.test_enum import Answer
from sqlalchemy.sql.expression import null



#Function to populate Main page
def index(request):
    credentialmismatch = 'This associated username and password does not exist'
    if request.method == "POST":
        submit = request.POST.get('submit')
        if (submit == "CREATE ACCOUNT"):
            return HttpResponseRedirect('/account/')
        if (submit == "ENTER"):
            
            usname = request.POST.get('username')
            psword = request.POST.get('password')
            try:
                lid = user.objects.get(userName = usname, password = psword)
            
                if (lid.id>0):
                    return HttpResponseRedirect('/question/') 
            except:
                return render(request, 'CourseGuru_App/index.html',{'credentialmismatch': credentialmismatch})

        
    else:
        return render(request, 'CourseGuru_App/index.html')
    

def account(request):
    if request.method == "POST":
       firstname = request.POST.get('firstname')
       lastname = request.POST.get('lastname')
       username = request.POST.get('username')
       psword = request.POST.get('password')
       cpsword = request.POST.get('cpassword')
       stat = request.POST.get('status')       
       
       mismatch = 'Password Mismatch'
       if (psword != cpsword):
            return render(request, 'CourseGuru_App/account.html', {'fname': firstname, 'lname': lastname, 'uname': username, 'status': stat,'msmatch': mismatch})
       else:
           #edit possibly drop user ID from the table or allow it to be null 
            user.objects.create(firstName = firstname, lastName = lastname, userName = username, password = psword, status = stat)   
        
#        return HttpResponseRedirect('/index/')
#       
#    usData = 
    return render(request, 'CourseGuru_App/account.html')
def question(request):
    if request.method == "POST":
        nq = request.POST.get('NQ')
        questions.objects.create(question = nq, course_id = 1, user_id = 1)
        return HttpResponseRedirect('/question/')
    qData = questions.objects.all()
    return render(request, 'CourseGuru_App/question.html', {'content': qData})

def getIntent(category, entities):
    
    answer = category.objects.filter(intent = category) 
    entitylist = entities.split(",")
    
    numEntMtch = 0
    ansID= 0
    
    for i in answer:
        entList = answer.entities(i)
        temp = 0
        for j in entList:
            temp += entitylist.count(j)
            if temp > numEntMtch:
                numEntMtch = temp
                ansID = answer.objects.get(id)
            
    return ansID

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

    
    credentialmismatch = 'This associated username and password does not exist'
    voteButton = request.POST.get('submit')
    answerId = request.POST.get('answer-id')
    
    if (voteButton == "voteUp"):
        record = answer.objects.get(answer_id = answerId)
        record.rating = record.rating + 1
        record.save()
        return render(request, 'CourseGuru_App/index.html',{'credentialmismatch': credentialmismatch})
    if (voteButton == "voteDown"):
        record = answer.objects.get(answer_id = answerId)
        record.rating = record.rating - 1
        record.save()
        
        
    return render(request, 'CourseGuru_App/answer.html', {'answers': aData, 'Title': qData})

def chatbot(request):
    return render(request, 'CourseGuru_App/botchat.html',)


#    ---Canvas code---
#    url = (urlopen('https://canvas.wayne.edu/api/v1/courses').read()
#    response = urlopen('https://canvas.wayne.edu/api/v1/courses')
#    data = json.load(response)