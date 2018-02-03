
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render
import json
from urllib.request import urlopen
import psycopg2
from django.http.response import HttpResponseRedirect

#importing models 
from CourseGuru_App.models import user, category
from CourseGuru_App.models import course
from CourseGuru_App.models import questions
from CourseGuru_App.models import answers
from CourseGuru_App.models import category
from CourseGuru_App.models import botanswers
from test.test_enum import Answer



#Function to populate Main page
def index(request):
    if request.method == "POST":
        submit = request.POST.get('submit')
        if (submit == "CREATE ACCOUNT"):
            return HttpResponseRedirect('/account/')
        if (submit == "ENTER"):
            return HttpResponseRedirect('/question/')
 #       user.objects.create(username = userName, password = Password, )
        
    return render(request, 'CourseGuru_App/index.html')


def account(request):
    if request.method == "POST":
       firstname = request.POST.get('firstname')
       lastname = request.POST.get('lastname')
       psword = request.POST.get('password')
       cpsword = request.POST.get('cpassword')
       stat = request.POST.get('status')       
       
       mismatch = 'Password Mismatch'
       if (psword != cpsword):
            return render(request, 'CourseGuru_App/account.html', {'fname': firstname, 'lname': lastname, 'status': stat,'msmatch': mismatch})
       else:
           #edit possibly drop user ID from the table or allow it to be null 
            user.objects.create(firstName = firstname, lastName = lastname, userID = 2, password = psword, status = stat)   
        
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

# returns a good match to entities answer object  
def getIntent(intnt, entities):    
#def getIntent(request):   
#    catgry=""
    count = 0
    answr = ""
    #=========for testing using index page=============
    # if request.method == "POST":
    #      submit = request.POST.get('submit')
    #      if (submit == "CREATE ACCOUNT"):
    #         categories = request.POST.get('username')
    #         entities = request.POST.get('password')
    #===========================================================================
    entitiesList = entities.split(",")
    catgry = category.objects.get(intent = intnt)
    
    filtAns = botanswers.objects.filter(category_id = catgry.id)
     
    for m in filtAns:
        b = m.entities.split(",")
        tempCntMtch = 0
        ttlCnt = len(b)
        for n in b: 
            tempCntMtch += entitiesList.count(n)
            cntAccuracy = (tempCntMtch/ttlCnt)
            if cntAccuracy>count:
                count = cntAccuracy 
                answr = botanswers.objects.get(id = m.id)
    return (answr)                     
    #===========================================================================
    # return render(request, 'CourseGuru_App/index.html', {'answers': ansID})
    #===========================================================================
#    print(a.intent)
    
#===========================================================================
    # answer = category.objects.filter(intent = category) 
    # entitylist = entities.split(",")
    # 
    # numEntMtch = 0
    # ansID= 0
    # 
    # for i in answer:
    #     entList = answer.entities(i)
    #     temp = 0
    #     for j in entList:
    #         temp += entitylist.count(j)
    #         if temp > numEntMtch:
    #             numEntMtch = temp
    #             ansID = answer.objects.get(id = i.id)
    # aData = answers.objects.filter(id = ansID)
    #===========================================================================
#    return render(request, 'CourseGuru_App/index.html', {'answers': a})

#    return ansID

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


#    ---Canvas code---
#    url = (urlopen('https://canvas.wayne.edu/api/v1/courses').read()
#    response = urlopen('https://canvas.wayne.edu/api/v1/courses')
#    data = json.load(response)