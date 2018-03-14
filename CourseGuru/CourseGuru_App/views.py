import re
import tempfile
import json
import requests
import datetime
import nltk
import io

from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize.moses import MosesDetokenizer

from django.shortcuts import render, _get_queryset
from django.http.response import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.template.context_processors import request
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.models import User


#importing models 
from CourseGuru_App.models import questions
from CourseGuru_App.models import answers
from CourseGuru_App.models import keywords
from CourseGuru_App.models import courseinfo
from CourseGuru_App.models import course
from CourseGuru_App.models import category
from CourseGuru_App.models import botanswers
from CourseGuru_App.models import comments
from CourseGuru_App.models import courseusers
from CourseGuru_App.models import userratings
from CourseGuru_App.luisRun import teachLuis
from CourseGuru_App.natLang import reformQuery
from CourseGuru_App.pdfParser import *
from CourseGuru_App.docxParser import *
from CourseGuru_App.CSV import *
from CourseGuru_App.catQuestion import *
from CourseGuru_App.validate import *


from test.test_decimal import file
from pickle import INST
from test.test_enum import Answer
from builtins import str
from _ast import Str, Yield
from string import ascii_lowercase
from warnings import catch_warnings
from symbol import except_clause
from tkinter.font import BOLD
from attr.validators import instance_of
from docx.oxml.document import CT_Body

from CourseGuru_App import pdfParser, catQuestion
from pip._vendor.html5lib.constants import entities
from _overlapped import NULL
from attr.filters import exclude
#from nltk.parse.featurechart import sent

#Function to populate Main page
def index(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/courses/')
    else:
        credentialmismatch = 'Incorrect username or password'
        if request.method == "POST":
            submit = request.POST.get('submit')
            if (submit == "Login"): 
                usname = request.POST.get('username')
                psword = request.POST.get('password')
                user = authenticate(username=usname, password=psword)
                if user is not None:
                    if user.is_active:
                        login(request, user)
                        return HttpResponseRedirect('/courses/')
                else:
                    return render(request, 'CourseGuru_App/index.html', {'credentialmismatch': credentialmismatch})
        
                #try:
                #    
                #    lid = user.objects.get(userName = usname, password = psword)        
                #    if (lid.id>0):
                #        return HttpResponseRedirect('/question/') 
                #except:
                #    return render(request, 'CourseGuru_App/index.html',{'credentialmismatch': credentialmismatch})      
        else:
            newAct = request.GET.get('newAct', '')
            if newAct == "1":
                newAct = "Account successfully created"
                return render(request, 'CourseGuru_App/index.html',{'newAct': newAct}) 
            return render(request, 'CourseGuru_App/index.html')

def account(request):
    stat = 'Student'
    if request.method == "POST":
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        username = request.POST.get('username')
        psword = request.POST.get('password')
        cpsword = request.POST.get('cpassword')
        stat = request.POST.get('status')
        email = request.POST.get('email')       
        if (psword != cpsword):
            errorMsg = 'Password Mismatch'
            return render(request, 'CourseGuru_App/account.html', {'errorMsg': errorMsg, 'fname': firstname, 'lname': lastname, 'status': stat, 'email': email})
        elif (emailValidator(email) == False): 
            errorMsg = "Invalid Email Address!"
            return render(request, 'CourseGuru_App/account.html', {'errorMsg': errorMsg,'fname': firstname, 'lname': lastname, 'status': stat, 'email': email})
        elif(psword == username):
            errorMsg = "Username and Password can not be the same!"
            return render(request, 'CourseGuru_App/account.html', {'errorMsg': errorMsg,'fname': firstname, 'lname': lastname, 'status': stat, 'email': email})
        else:
            if (passwordValidator(psword) != None):
                errorMsg =  passwordValidator(psword)
                return render(request, 'CourseGuru_App/account.html', {'errorMsg': errorMsg,'fname': firstname, 'lname': lastname, 'status': stat, 'email': email})
            
            if User.objects.filter(username = username).exists():
                errorMsg = "Username taken"
                return render(request, 'CourseGuru_App/account.html', {'errorMsg': errorMsg,'fname': firstname, 'lname': lastname, 'status': stat, 'email': email})

            else:
                #edit possibly drop user ID from the table or allow it to be null 
                #user.objects.create(firstName = firstname, lastName = lastname, userName = username, password = psword, status = stat)  
                newUser = User.objects.create_user(username, email, psword) 
                newUser.first_name = firstname
                newUser.last_name = lastname
                newUser.status = stat
                newUser.save()
                return HttpResponseRedirect('/?newAct=1')  
    else:
        return render(request, 'CourseGuru_App/account.html', {'status': stat})    
def courses(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            if request.POST.get('Logout') == "Logout":
                logout(request)
                return HttpResponseRedirect('/')
            elif 'del' in request.POST:
                #Deletes the course selected and all questions, answers, and ratings associated with it
                cid = request.POST.get('del')
                tempQues = questions.objects.filter(course_id = cid)
                for x in tempQues:
                    tempAns = answers.objects.filter(question_id = x.id)
                    #Delete user ratings in course
                    for y in tempAns:
                        if userratings.objects.filter(answer_id = y.id).exists():
                            userratings.objects.filter(answer_id = y.id).delete()
                    #Delete answers in course
                    if answers.objects.filter(question_id = x.id).exists():
                        answers.objects.filter(question_id = x.id).delete()
                #Delete questions in course
                if questions.objects.filter(course_id = cid).exists():
                    questions.objects.filter(course_id = cid).delete()
                #Delete course users
                if courseusers.objects.filter(course_id = cid).exists():
                    courseusers.objects.filter(course_id = cid).delete()
                #Delete course
                if course.objects.filter(id = cid).exists():
                    course.objects.filter(id = cid).delete()
        curUser = request.user
        if curUser.status == "Teacher":
            courseList = course.objects.filter(user_id = curUser.id)
        else:
            courseList = courseusers.objects.filter(user_id = curUser.id)
        return render(request, 'CourseGuru_App/courses.html', {'courses': courseList})
    else:
        return HttpResponseRedirect('/')
def genDate():
    #This needs to be removed. SQL can do it automatically
    curDate = datetime.datetime.now().strftime("%m-%d-%Y %I:%M %p")

    return (curDate)
def roster(request):
    if request.user.is_authenticated:
        cid = request.GET.get('cid', '')
        cName = course.objects.get(id = cid)
        studentList = courseusers.objects.filter(course_id=cid)
        if request.method == "POST":
            if request.POST.get('Logout') == "Logout":
                logout(request)
                return HttpResponseRedirect('/')
            if 'newUser' in request.POST:
                newUser = request.POST.get('newUser')
                if User.objects.filter(username = newUser).exists():
                    addUser = User.objects.get(username = newUser)
                    if courseusers.objects.filter(user_id = addUser.id, course_id = cid).exists():
                        credentialmismatch = "User is already in the course"
                        return render(request, 'CourseGuru_App/roster.html', {'courseID': cid, 'credentialmismatch': credentialmismatch, 'studentList': studentList})
                    else:
                        userAdded = "User has been successfully added to the course"
                        courseusers.objects.create(user_id = addUser.id, course_id = cid)
                        return render(request, 'CourseGuru_App/roster.html', {'courseID': cid, 'userAdded': userAdded, 'studentList': studentList})
                else:
                    credentialmismatch = "Username does not exist"
                    return render(request, 'CourseGuru_App/roster.html', {'courseID': cid, 'credentialmismatch': credentialmismatch, 'studentList': studentList})
             
            elif 'delete' in request.POST:
                user = request.POST.get('delete')
                courseusers.objects.filter(id = int(user)).delete()                
                return render(request, 'CourseGuru_App/roster.html', {'courseID': cid, 'studentList': studentList})
            elif 'dlCSV' in request.POST:
                response = downloadCSV()
                return response
            elif request.method == 'POST' and request.FILES['csvFile']:
                #decoding the file for reading 
                csvF = request.FILES['csvFile']
                strNotAdded = readCSV(csvF, cid)
                return render(request, 'CourseGuru_App/roster.html', {'courseID': cid, 'studentList': studentList, 'notAdded': strNotAdded})
            else:
                credentialmismatch = "Username does not exist"
                return render(request, 'CourseGuru_App/roster.html', {'courseID': cid, 'credentialmismatch': credentialmismatch, 'courseName': cName})
        return render(request, 'CourseGuru_App/roster.html', {'courseID': cid, 'studentList': studentList, 'courseName': cName})
    else:
        return HttpResponseRedirect('/')
  
# Function to populate Main page
def question(request):
    if request.user.is_authenticated:
            #Grabs the questions form the db and orders them by id in desc fashion so the newest are first
        cid = request.GET.get('id', '')
        qData = questions.objects.get_queryset().filter(course_id = cid).order_by('-pk')
        page = request.GET.get('page', 1)
        cName = course.objects.get(id = cid)
        filterCategory = 'All'
        if request.method == "POST":
            if request.POST.get('Logout') == "Logout":
                logout(request)
                return HttpResponseRedirect('/')
            elif 'del' in request.POST:
                qid = request.POST.get('del')
                tempAns = answers.objects.filter(question_id = qid)
                for x in tempAns:
                    if userratings.objects.filter(answer_id = x.id).exists():
                        userratings.objects.filter(answer_id = x.id).delete()
                if answers.objects.filter(question_id = qid).exists():
                    answers.objects.filter(question_id = qid).delete()
                if questions.objects.filter(id = qid).exists():
                    questions.objects.filter(id = qid).delete()
            if request.POST.get('query'):
                query = request.POST.get('query')
                if query: 
                    qData = qData.filter(question__icontains=query)
            if request.POST.get('Filter'):
                filterCategory = request.POST.get('Filter')
                if filterCategory != 'All':
                    qData = qData.filter(category=filterCategory) 
                else: 
                    qData = questions.objects.get_queryset().filter(course_id = cid).order_by('-pk')
                
        #Paginator created to limit page display to 10 data items per page
        paginator = Paginator(qData, 10)
        try:
            fquestions = paginator.page(page)
        except PageNotAnInteger:
            fquestions = paginator.page(1)
        except EmptyPage:
            fquestions = paginator.page(paginator.num_pages())
    #    return render(request, 'CourseGuru_App/question.html', {'content': fquestions})
        user = request.user
        
        return render(request, 'CourseGuru_App/question.html', {'content': fquestions, 'user': user, 'courseID': cid, 'courseName': cName, 'status': filterCategory})
    else:
        return HttpResponseRedirect('/')

def uploadDocument(request):
    if request.user.is_authenticated:
        cid = request.GET.get('cid', '')
        cName = course.objects.get(id = cid)
        studentList = courseusers.objects.filter(course_id=cid)
        if request.method == "POST":
            if request.POST.get('Logout') == "Logout":
                logout(request)
                return HttpResponseRedirect('/')
            else:
                credentialmismatch = "Username does not exist"
                return render(request, 'CourseGuru_App/uploadDocument.html', {'courseID': cid, 'credentialmismatch': credentialmismatch, 'courseName': cName})
#MIKE BEFORE DELETING THIS DOUBLE CHECK THAT YOU ADDED THE ERROR FILE HANDLING FROM BELOW
#                if request.method == "POST":
#                        myfile = request.FILES.get("syllabusFile")
#                        errorMessage="Only .pdf and .docx type are currently supported"
#                        docType= myfile.content_type
#                        #print(docType)
#                        myfile=myfile.file.read()
#                        f = tempfile.TemporaryFile('r+b')
#                        f.write(myfile)
#                        
#                        if docType == 'application/pdf':
#                            document = pdfParser.pdfToText(f)
#                        elif docType == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
#                            document = docxParser(f)
#                        else: 
#                            return render(request, 'CourseGuru_App/parse.html', {'error': errorMessage})
############################################################################################################        
        return render(request, 'CourseGuru_App/uploadDocument.html', {'courseID': cid, 'studentList': studentList, 'courseName': cName})
    else:
        return HttpResponseRedirect('/')
    
def publish(request):
    if request.user.is_authenticated:
        cid = request.GET.get('cid', '')
        # Passes in new question when the submit button is selected
        if request.method == "POST":
            if request.POST.get('Logout') == "Logout":
                logout(request)
                return HttpResponseRedirect('/')
            ques = request.POST.get('NQ')
            comm = request.POST.get('NQcom')
            questionDate = genDate()
            user = request.user    
            categ= catQuestion.categorize(ques) 

            newQ = questions.objects.create(question = ques, course_id = cid, user_id = user.id, date = questionDate, comment = comm, category=categ)
               
            botAns = cbAnswer(ques)
            answerDate = genDate()
            
            if botAns is not None:
                answers.objects.create(answer = botAns, user_id = 38, question_id = newQ.id, date = answerDate)
            #teachLuis(ques, "Name")
            return HttpResponseRedirect('/answer/?id=%s&cid=%s' % (newQ.id, cid)) 
        return render(request, 'CourseGuru_App/publish.html', {'courseID': cid})
    else:
        return HttpResponseRedirect('/')
                 
def publishAnswer(request):
    if request.user.is_authenticated:
        qid = request.GET.get('id', '')
        cid = request.GET.get('cid', '')
        qData = questions.objects.get(id = qid)

        if request.method == "POST":
            if request.POST.get('Logout') == "Logout":
                logout(request)
                return HttpResponseRedirect('/')
            ans = request.POST.get('NQcom')
            answerDate = genDate()
            user = request.user
            newAns = answers.objects.create(answer = ans, user_id = user.id, question_id = qid, date = answerDate)
            if user.status == 'Teacher':
                botanswers.objects.create(entities = qData.question, answerId= newAns, category_id = 5, answer=ans )              
            return HttpResponseRedirect('/answer/?id=%s&cid=%s' % (qid, cid))
        return render(request, 'CourseGuru_App/publishAnswer.html', {'Title': qData, 'courseID': cid, 'quesID': qid})
    else:
        return HttpResponseRedirect('/')

def publishCourse(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            if request.POST.get('Logout') == "Logout":
                logout(request)
                return HttpResponseRedirect('/')
            newCourse = request.POST.get('NC')
            cType = request.POST.get('cType')
            user = request.user
            course.objects.create(courseName = newCourse, courseType = cType, user_id = user.id)
            cid = course.objects.last()
            courseusers.objects.create(user_id = user.id, course_id = cid.id)
            return HttpResponseRedirect('/courses/')
        return render(request, 'CourseGuru_App/publishCourse.html')
    else:
        return HttpResponseRedirect('/')

# Function to populate Answers page
def answer(request):
    if request.user.is_authenticated:
    #    if request.method=='GET':
        qid = request.GET.get('id', '')
        cid = request.GET.get('cid', '')
        user = request.user
        aData = answers.objects.filter(question_id = qid).order_by( '-resolved', 'pk')
        ansCt = aData.count()
        qData = questions.objects.get(id = qid)
        cData = comments.objects.filter(question_id = qid)
  
        #-----Used for checking if post was previously rated------
        upData2 = userratings.objects.filter(user_id = user.id, rating = 1).only('answer_id')
        downData2 = userratings.objects.filter(user_id = user.id, rating = 0).only('answer_id')
        
        upData = []
        downData = []
        
        for x in upData2:
            upData.append(x.answer_id)
            
        for x in downData2:
            downData.append(x.answer_id)
        #--------------------------------------------------------
        resolve = False
        for a in aData: 
                if a.resolved == True:
                    resolve = True

        if request.method == "POST":
            if request.POST.get('Logout') == "Logout":
                logout(request)
                return HttpResponseRedirect('/')
            elif 'query' in request.POST:
                query = request.POST.get('query')
                if query: 
                    aData = aData.filter(answer__icontains=query)
                return render(request, 'CourseGuru_App/answer.html', {'answers': aData, 'numAnswers': ansCt, 'Title': qData, 'comments': cData, 'courseID': cid, 'resolved':resolve})
            elif 'delAns' in request.POST:
                aid = request.POST.get('delAns')
                if userratings.objects.filter(answer_id = aid).exists():
                    userratings.objects.filter(answer_id = aid).delete()
                if answers.objects.filter(id = aid).exists():
                    answers.objects.filter(id = aid).delete()

            elif 'delQues' in request.POST:
                tempAns = answers.objects.filter(question_id = qid)
                for x in tempAns:
                    if userratings.objects.filter(answer_id = x.id).exists():
                        userratings.objects.filter(answer_id = x.id).delete()
                if answers.objects.filter(question_id = qid).exists():
                    answers.objects.filter(question_id = qid).delete()
                if questions.objects.filter(id = qid).exists():
                    questions.objects.filter(id = qid).delete()
                return HttpResponseRedirect('/question/?id=%s' % cid)   
            elif 'resolve' in request.POST:
                aid = request.POST.get('resolve')
                ans = answers.objects.get(id = aid)
                resolve = True
                ans.resolved = True
                ans.save()
                if ((answers.objects.filter(id = aid).exists()) and (botanswers.objects.filter(answerId = aid).exists() == False)):
                    botanswers.objects.create(entities = qData.question, answerId=ans , category_id = 5, answer=ans.answer)
                aData = answers.objects.filter(question_id = qid).order_by( '-resolved', 'pk')
                return render(request, 'CourseGuru_App/answer.html', {'answers': aData, 'numAnswers': ansCt, 'Title': qData, 'comments': cData, 'courseID': cid, 'resolved':resolve})
#unresolve functionality ===================================         
            #===================================================================
            # elif 'unresolve' in request.POST:
            #     rslvdAnsId = answers.objects.get(resolved = True)
            #     providedBy = User.objects.get(id = rslvdAnsId.user.id)                    
            #     if providedBy.status != 'Teacher':
            #         print(providedBy.status)
            #         botanswers.objects.filter(answerId = rslvdAnsId).delete()
            #     rslvdAnsId.resolved=False
            #     rslvdAnsId.save()
            #     resolve = False
            #     aData = answers.objects.filter(question_id = qid).order_by( '-resolved', 'pk')
            #     return render(request, 'CourseGuru_App/answer.html', {'answers': aData, 'numAnswers': ansCt, 'Title': qData, 'comments': cData, 'courseID': cid, 'resolved':resolve})
            #===================================================================
#=============================================================            
            return HttpResponseRedirect('/answer/?id=%s&cid=%s' % (qid, cid)) 
        return render(request, 'CourseGuru_App/answer.html', {'answers': aData, 'numAnswers': ansCt, 'Title': qData, 'comments': cData, 'courseID': cid, 'resolved': resolve, 'upData': upData, 'downData': downData})

    else:
        return HttpResponseRedirect('/')
    
def voting(request):
    rate = request.GET.get('rating')
    answerID = request.GET.get('answer')
    userID = request.GET.get('user')    
    
    if userratings.objects.filter(user_id = userID, answer_id = answerID).exists():
        newRate = userratings.objects.get(user_id = userID, answer_id = answerID)
        newRate.rating = rate
        newRate.save()
    else:
        userratings.objects.create(user_id = userID, answer_id = answerID, rating = rate)    
    uprateCt = userratings.objects.filter(answer_id = answerID, rating = 1).count()
    downrateCt = userratings.objects.filter(answer_id = answerID, rating = 0).count()
    record = answers.objects.get(id = answerID)
    record.rating = (uprateCt - downrateCt)
    record.save()
    
    return HttpResponse()

# returns a good match to entities answer object  
def getIntentAns(luisIntent, luisEntities, nq):    
    count = 0
    answr = ""
    
    entitiesList = luisEntities.split(",")
    catgry = category.objects.get(intent = luisIntent)
    
    filtAns = botanswers.objects.filter(category_id = catgry.id)
    
    for m in filtAns: 
        if nq.lower() in m.entities.lower():
            answer = m.answer
            return answer
         
    for m in filtAns:
        Match = 0
        #testing, change entities name to something else later
        ansLen = len(m.entities)
        for ent in entitiesList:
            #testing, change entities name to something else later
            if ent.lower() in m.entities.lower():
                Match += 1
        Accuracy = (Match/ansLen)
        if Accuracy>count:
            count = Accuracy
            answr = m.answer

    return (answr)     


def fileParsing(request):
    if request.method == "POST":
        myfile = request.FILES.get("syllabusFile")
        errorMessage="Only .pdf and .docx type are currently supported"
        docType= myfile.content_type
        #print(docType)
        myfile=myfile.file.read()
        f = tempfile.TemporaryFile('r+b')
        f.write(myfile.decode())
        
        if docType == 'application/pdf':
            document = pdfParser.pdfToText(f)
            return render(request, 'CourseGuru_App/parse.html', {'convText': document})
        elif docType == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            document = docxParser(f)
        else: 
            return render(request, 'CourseGuru_App/parse.html', {'error': errorMessage})
        
    return render(request, 'CourseGuru_App/parse.html')  
  def chatbot(request):
    return render(request, 'CourseGuru_App/botchat.html',)

def cbAnswer(nq):
    r = requests.get('https://westus.api.cognitive.microsoft.com/luis/v2.0/apps/6059c365-d88a-412b-8f33-d7393ba3bf9f?subscription-key=c574439a46e64d8cb597879499ccf8f9&verbose=true&timezoneOffset=-300&q=%s' % nq)
    luisStr = json.loads(r.text)
    #Grabs intent score of question
    luisScore = float(luisStr['topScoringIntent']['score'])
    #Grabs intent of question
    luisIntent = luisStr['topScoringIntent']['intent']
    #Grabs entities
    if luisIntent == 'Greetings':
        return('Hello, how can I help you?')
    if not luisStr['entities']:
        return
    luisEntities = ""
    
    z = 0
    for x in luisStr['entities']:
        newEnt = luisStr['entities'][z]['entity']
        if luisStr['entities'][z]['type'] == "Role" and newEnt.endswith('s'):
            newEnt = newEnt[:-1]
        if z == 0:
            luisEntities += newEnt
        else:
            luisEntities += ',' + newEnt
        z += 1
        
    #If intent receives a lower score than 75% or there is no intent, the question does not get answered
    if luisScore < 0.75 or luisIntent == 'None':
        return
    #---catID = category.objects.get(intent=luisIntent)
    #Sets cbAns to the first answer it can find matching that category (This needs to be improved)
    #---cbAns = botanswers.objects.filter(category_id = catID.id).first()
    #ID of the latest question created
    #qid = questions.objects.last()

    
    entAnswer = getIntentAns(luisIntent, luisEntities, nq)
    if entAnswer == "":
        return
    botAns = reformQuery(nq) + entAnswer
    return(botAns)


def chatAnswer(request):
    question = request.GET.get('question')
    botAns = cbAnswer(question)
    return HttpResponse(botAns)

