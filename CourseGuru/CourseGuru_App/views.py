#from django.http import HttpResponse
#from django.template import loader
from django.shortcuts import render
import json
#from urllib.request import urlopen
#import psycopg2
from django.http.response import HttpResponseRedirect
import requests

#importing models 
from CourseGuru_App.models import user
from CourseGuru_App.models import course
from CourseGuru_App.models import questions
from CourseGuru_App.models import answers
from CourseGuru_App.models import category
from CourseGuru_App.models import botanswers
from CourseGuru_App.models import comments

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
            user.objects.create(firstNae = firstname, lastName = lastname, userID = 2, password = psword, status = stat)   
         
#        return HttpResponseRedirect('/index/')
#       
#    usData = 
    return render(request, 'CourseGuru_App/account.html')


# Function to populate Main page
def question(request):
    if request.method == "POST":
        nq = request.POST.get('NQ')
        questions.objects.create(question = nq, course_id = 1, user_id = 1)
        cbAnswer(nq)
        #=======================================================================
        # luisIntent = cbAnswer(nq)
        # catID = category.objects.get(id=1)
        # cbAns = botanswers.objects.get(category_id = catID.id)
        # qid = questions.objects.get(question = nq)
        # answers.objects.create(answer = cbAns.answer, user_id = 1, question_id = qid.id)
        #=======================================================================
#        questions.objects.filter(id=4).update(question=catID.id)
        
        #=======================================================================
        # try:
        #     r = request.get('ENDPOINTq=%s' % nq, '')
        #     luisStr = json.loads(r.text)
        #     luisStr = luisStr['topScoringIntent']['intent']
        #     questions.objects.filter(id=3).update(question=luisStr)
        # except Exception as e:
        #     questions.objects.filter(id=3).update(question='failed')
        #=======================================================================
        return HttpResponseRedirect('/question/') 
    qData = questions.objects.all()
    return render(request, 'CourseGuru_App/question.html', {'content': qData})

# Function to populate Answers page
def answer(request):
#    if request.method=='GET':
    qid = request.GET.get('id', '') 
    if request.method == "POST":
        if 'COM' not in request.POST:
            ans = request.POST.get('ANS')
            answers.objects.create(answer = ans, user_id = 1, question_id = qid)
            return HttpResponseRedirect('/answer/?id=%s' % qid)
        else:
            com = request.POST.get('COM')
            comments.objects.create(comment = com, question_id = qid, user_id = 1)
            return HttpResponseRedirect('/answer/?id=%s' % qid)
    aData = answers.objects.filter(question_id = qid)
    qData = questions.objects.get(id = qid)
    cData = comments.objects.filter(question_id = qid)
    return render(request, 'CourseGuru_App/answer.html', {'answers': aData, 'Title': qData, 'comments': cData})

def chatbot(request):
    return render(request, 'CourseGuru_App/botchat.html',)

def cbAnswer(nq):
    r = requests.get('ENDPOINT%s' % nq)
    luisStr = json.loads(r.text)
    #Grabs intent score of question
    luisScore = float(luisStr['topScoringIntent']['score'])
    #Grabs intent of question
    luisIntent = luisStr['topScoringIntent']['intent']
    #Grabs entities
    luisEntity = luisStr['entities']
    #If intent receives a lower score than 60% or there is no intent, the question does not get answered
    if luisScore < 0.6 or luisIntent == 'None':
        return
    catID = category.objects.get(intent=luisIntent)
    #Sets cbAns to the first answer it can find matching that category (This needs to be improved)
    cbAns = botanswers.objects.filter(category_id = catID.id).first()
    #ID of the latest question created
    qid = questions.objects.last()
    answers.objects.create(answer = cbAns.answer, user_id = 1, question_id = qid.id)
#    return(intent)

#    ---Canvas code---
#    url = (urlopen('https://canvas.wayne.edu/api/v1/courses').read()
#    response = urlopen('https://canvas.wayne.edu/api/v1/courses')

#    data = json.load(response)