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
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

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
from CourseGuru_App import pdfParser
from CourseGuru_App.luisRun import publishLUIS

from io import BytesIO

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
        else:
            newAct = request.GET.get('newAct', '')
            if newAct == "1":
                newAct = "Account successfully created"
                return render(request, 'CourseGuru_App/index.html',{'newAct': newAct}) 
            return render(request, 'CourseGuru_App/index.html')

def account(request):
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
        return render(request, 'CourseGuru_App/account.html')

def passwordValidator(password):
    passRegCheck = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)"
    if (len(password)<8): 
        errorMsg = 'Your password must be at least 8 characters long.'
        return errorMsg
    elif ((re.search(passRegCheck, password))==None):
        errorMsg = "Your password must contain one uppercase character, one lowercase character, and at least one number!"
        return errorMsg
    else:
        return None
            
def emailValidator(email):
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False
    
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
        
        return render(request, 'CourseGuru_App/question.html', {'content': fquestions, 'user': user, 'courseID': cid, 'courseName': cName})
    else:
        return HttpResponseRedirect('/')

def uploadDocument(request):
    if request.user.is_authenticated:
        cid = request.GET.get('cid', '')
        cName = course.objects.get(id = cid)
        if request.method == "POST":
            if request.POST.get('Logout') == "Logout":
                logout(request)
                return HttpResponseRedirect('/')
            if len(request.FILES) != 0:
                courseFile = request.FILES.get("courseFile").file.read()
                docType = request.POST.get("docType")
                catID = category.objects.get(intent = docType)
                f = tempfile.TemporaryFile('r+b')
                f.write(courseFile)
                docxParser(f, cid, catID)
        return render(request, 'CourseGuru_App/uploadDocument.html', {'courseID': cid, 'courseName': cName})
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
            categ= categorizeQuestion(ques, comm) 
            newQ = questions.objects.create(question = ques, course_id = cid, user_id = user.id, date = questionDate, comment = comm, category=categ)
               
            botAns = cbAnswer(ques, cid)
            answerDate = genDate()
            
            if botAns is not None:
                answers.objects.create(answer = botAns, user_id = 38, question_id = newQ.id, date = answerDate)
            #teachLuis(ques, "Name")
            return HttpResponseRedirect('/answer/?id=%s&cid=%s' % (newQ.id, cid)) 
        return render(request, 'CourseGuru_App/publish.html', {'courseID': cid})
    else:
        return HttpResponseRedirect('/')
    
def categorizeQuestion(ques,comm):
    syllabus="Syllabus"
    other="Other"
    sylKeyTerms = "syllabus,instructor name,teachers name,grading scale,grade,ta,teaching assistant,student,due date,due,assignment,late"
    sylKeyTermList=sylKeyTerms.split(',')
    matchCount=0
    for z in sylKeyTermList:
        if ques.__contains__(z):
            matchCount += 1
        if comm.__contains__(z):
            matchCount+=1
    if matchCount > 0:
        return syllabus
    else:
        return other
             
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
            answers.objects.create(answer = ans, user_id = user.id, question_id = qid, date = answerDate)
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
        aData = answers.objects.filter(question_id = qid).order_by('pk')
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

        if request.method == "POST":
            if request.POST.get('Logout') == "Logout":
                logout(request)
                return HttpResponseRedirect('/')
            elif 'query' in request.POST:
                query = request.POST.get('query')
                if query: 
                    aData = aData.filter(answer__icontains=query)
                return render(request, 'CourseGuru_App/answer.html', {'answers': aData, 'numAnswers': ansCt, 'Title': qData, 'comments': cData, 'courseID': cid})
            
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

            return HttpResponseRedirect('/answer/?id=%s&cid=%s' % (qid, cid)) 
        return render(request, 'CourseGuru_App/answer.html', {'answers': aData, 'numAnswers': ansCt, 'Title': qData, 'comments': cData, 'courseID': cid, 'upData': upData, 'downData': downData})
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

def courseFile(request):
    if request.method == "POST":
        #Sets myfile to the selected file on page and reads it
        myfile = request.FILES.get("syllabusFile").file.read()
        test = pdfParser.pdfToText(myfile)
    return render(request, 'CourseGuru_App/parse.html', {'convText' : test})


def fileParsing(request):
    if request.method == "POST":
        myfile = request.FILES.get("syllabusFile").file.read()
         
        f = tempfile.TemporaryFile('r+b')
        f.write(myfile)
        
        docxParser(f)
        
    return render(request, 'CourseGuru_App/parse.html')  
  def chatbot(request):
    return render(request, 'CourseGuru_App/botchat.html',)

def cbAnswer(nq, courseID=0, chatWindow=False):
    r = requests.get('https://westus.api.cognitive.microsoft.com/luis/v2.0/apps/6059c365-d88a-412b-8f33-d7393ba3bf9f?subscription-key=c574439a46e64d8cb597879499ccf8f9&spellCheck=true&bing-spell-check-subscription-key={5831ea4a48994d53abdc2312b6ea7ccf}&verbose=true&timezoneOffset=0&q=%s' % nq)
    luisStr = json.loads(r.text)
    #Grabs intent score of question
    luisScore = float(luisStr['topScoringIntent']['score'])
    #Grabs intent of question
    luisIntent = luisStr['topScoringIntent']['intent']
    #Grabs entities
    if luisIntent == 'Greetings' and chatWindow == True:
        return('Hello, how can I help you?')
    elif luisIntent == 'Greetings':
        return
    elif luisIntent == 'Name' or luisIntent == 'Course Policies':
        luisIntent = 'Syllabus'
    #If intent receives a lower score than 75% or there is no intent, the question does not get answered
    elif (luisIntent == "None" or not luisStr['entities'] or luisScore < 0.75) and chatWindow == True:
        return("Sorry, I didn't understand that.")
    elif luisIntent == "None" or not luisStr['entities'] or luisScore < 0.75:
        return
    
    print(luisIntent, chatWindow)
    
    #teachLuis(nq, 'Other')
    #publishLUIS()
    
    luisEntities = ""
    z = 0
    #regex = re.compile('[^a-zA-Z]')

    for x in luisStr['entities']:
        newEnt = luisStr['entities'][z]['entity']
        #newEnt = regex.sub('', newEnt)
        if z == 0:
            luisEntities += newEnt
        else:
            luisEntities += ',' + newEnt
        z += 1
    
    #Add variations of names a student would call the teacher if one is found
    profNames = ['instructor','teacher','professor']
    for name in profNames:
        if name in luisEntities.lower():
            for addName in profNames:
                if addName not in luisEntities.lower():
                    luisEntities += ',' + addName
        else:
            continue
        break
    if 'ta' in luisEntities.lower():
        luisEntities += ',' + 'teaching assistant'
                    
    
    entAnswer = getIntentAns(luisIntent, luisEntities, courseID, chatWindow)
    if entAnswer == "":
        return
    #botAns = reformQuery(nq) + entAnswer
    botAns = entAnswer
    return(botAns)

# returns a good match to entities answer object  
def getIntentAns(luisIntent, luisEntities, courseID=0, chatWindow=False):    
    count = 0
    answr = ""
    
    entitiesList = luisEntities.lower().split(",")
    catgry = category.objects.get(intent = luisIntent)
    
    #Changes plural to singular
    lem = nltk.wordnet.WordNetLemmatizer()
    for ind, ent in enumerate(entitiesList):
        print("CHECK: " + ent)
        entitiesList[ind] = lem.lemmatize(ent)
        print("AFTER: " + entitiesList[ind])
    
    if courseID != 0:
        filtAns = botanswers.objects.filter(category_id = catgry.id, course_id = courseID)
    else:
        filtAns = botanswers.objects.filter(category_id = catgry.id)
    
    for m in filtAns:
        Match = 0
        ansLen = len(m.entities)
        for ent in entitiesList:
            if ent.lower() in m.entities.lower():
                Match += 1
        Accuracy = (Match/ansLen)
        if Accuracy>count:
            count = Accuracy
            answr = m.answer
            
    if answr == "" and chatWindow == True:
        answr = "Sorry, I didn't understand that."
    
    return (answr) 


def chatAnswer(request):
    question = request.GET.get('question')
    botAns = cbAnswer(question, chatWindow=True)
    return HttpResponse(botAns)

