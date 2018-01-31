
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



#Function to populate Main page
def index(request):
    if request.method == "POST":
        submit = request.POST.get('submit')
        if (submit == "CREATE ACCOUNT"):
            return HttpResponseRedirect('/account/')
        if (submit == "ENTER"):
            return HttpResponseRedirect('/question/')
 #       user.objects.create(username = userName, password = Password, )
        
#    qData = questions.objects.all()
    return render(request, 'CourseGuru_App/index.html')
#     if request.method == "POST":
#         if form.is_valid():
 #            form.save()
#             if 'createAccount' in request.POST:
#                 return HttpResponseRedirect('/account/')
#             else:
#                 userName = request.POST.get('username')
#                 password = request.POST.get('password')
    
 #       questions.objects.create(question = nq, course_id = 1, user_id = 1)
#                 return HttpResponseRedirect('/')
   # qData = questions.objects.all()
#   return render(request, 'CourseGuru_App/index.html', {'content': qData})

def account(request):
    if request.method == "POST":
       firstname = request.POST.get('firstname')
       lastname = request.POST.get('lastname')
       psword = request.POST.get('password')
       cpsword = request.POST.get('cpassword')
       stat = request.POST.get('status')
       mismatch = 'password mismatch'
       if (psword != cpsword):
            return render(request, 'CourseGuru_App/account.html', {'fname': firstname, 'lname': lastname, 'status': stat, 'msmatch': mismatch})
       else:
            user.objects.create(firstNae = firstname, lastName = lastname, userID = 2, password = psword, status = stat)   
        
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