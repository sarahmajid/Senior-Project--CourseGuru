import re
import tempfile
import json
import requests
import datetime
import io
import os.path

from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.tokenize.moses import MosesDetokenizer

from django.shortcuts import render, _get_queryset
from django.http.response import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.template.context_processors import request
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import redirect
from django.conf import settings
from django.core.files import File

#importing models 
from CourseGuru_App.models import questions
from CourseGuru_App.models import answers
from CourseGuru_App.models import course
from CourseGuru_App.models import category
from CourseGuru_App.models import botanswers
from CourseGuru_App.models import courseusers
from CourseGuru_App.models import userratings
from CourseGuru_App.models import document
from CourseGuru_App.luisRun import teachLuis
from CourseGuru_App.natLang import reformQuery
from CourseGuru_App.pdfParser import *
from CourseGuru_App.docxParser import *
from CourseGuru_App.pptxParser import *
from CourseGuru_App.CSV import *
from CourseGuru_App.luisRun import publishLUIS
from CourseGuru_App.catQuestion import *
from CourseGuru_App.validate import *
from CourseGuru_App.botFunctions import *
from CourseGuru_App.tasks import queuePublish
from CourseGuru_App.viewFuncs import *
from CourseGuru_App.sendEmail import sendEmailExistingUser
from CourseGuru_App.createUsersFunctions import createNewUser, createTempUser, updateUserInfo

from builtins import str
from pip._vendor.requests.api import post
from botocore.vendored.requests.api import request
#from pywin.dialogs.login import newpassword



#Function to populate Main page
def index(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/courses/')
    else:
        credentialmismatch = 'Incorrect username or password'
        if request.method == "POST":
            submit = request.POST.get('submit')
            if (submit == "Login"): 
                usname = request.POST.get('username').lower()
                psword = request.POST.get('password')
                user = authenticate(username=usname, password=psword)
                if user is not None:
                    if user.is_active:
                        login(request, user)
                        return HttpResponseRedirect('/courses/')
                else:
                    return render(request, 'CourseGuru_App/index.html', {'credentialmismatch': credentialmismatch, 'usrname': usname})    
        else:
            newAct = request.GET.get('newAct', '')
            if newAct == "1":
                newAct = "Account successfully created"
                return render(request, 'CourseGuru_App/index.html',{'newAct': newAct}) 
            elif newAct =='2':
                newAct = "Account successfully updated"
                return render(request, 'CourseGuru_App/index.html',{'newAct': newAct}) 
            return render(request, 'CourseGuru_App/index.html')

def account(request):
    stat = 'Student'
    if request.method == "POST":
        firstname = request.POST.get('firstname').strip()
        lastname = request.POST.get('lastname').strip()
        username = request.POST.get('username').lower()
        psword = request.POST.get('password')
        cpsword = request.POST.get('cpassword')
        stat = request.POST.get('status')
        email = request.POST.get('email')       
        if (psword != cpsword):
            errorMsg = 'Password Mismatch'      
        elif (emailValidator(email) == False): 
            errorMsg = "Invalid Email Address!"
        elif(psword == username):
            errorMsg = "Username and Password can not be the same!"
        else:
            if (passwordValidator(psword) != None):
                errorMsg =  passwordValidator(psword)
                return render(request, 'CourseGuru_App/account.html', {'errorMsg': errorMsg,'fname': firstname, 'lname': lastname, 'status': stat, 'email': email})
            if User.objects.filter(username = username).exists():
                errorMsg = "Username taken" 
            else:
                createNewUser(username, email, psword, firstname, lastname, stat)
                return HttpResponseRedirect('/?newAct=1')  
        return render(request, 'CourseGuru_App/account.html', {'errorMsg': errorMsg, 'fname': firstname, 'lname': lastname, 'status': stat, 'email': email})
    else:
        return render(request, 'CourseGuru_App/account.html', {'status': stat})    

def editAccount(request):
    if request.user.is_authenticated:
        curUser = request.user
        stat = 'Student'
        if request.method == "POST":
            if request.POST.get('Logout') == "Logout":
                logout(request)
                return HttpResponseRedirect('/')
            oldusername = request.POST.get('oldusername')
            oldpassword = request.POST.get('oldpassword')
            firstname = request.POST.get('firstname').strip()
            lastname = request.POST.get('lastname').strip()
            username = request.POST.get('username').lower()
            psword = request.POST.get('password')
            cpsword = request.POST.get('cpassword')
            stat = request.POST.get('status')
            email = curUser.email  
            if authenticate(username=oldusername, password=oldpassword) is not None:
                if (psword != cpsword):
                    errorMsg = 'Password Mismatch'
                elif (oldpassword == psword or oldusername == username):
                    errorMsg = 'New password or username can not be the same as the old password or username!'      
                elif (emailValidator(email) == False): 
                    errorMsg = "Invalid Email Address!"
                elif(psword == username):
                    errorMsg = "Username and Password can not be the same!"
                else:
                    if (passwordValidator(psword) != None):
                        errorMsg =  passwordValidator(psword)
                        return render(request, 'CourseGuru_App/editAccount.html', {'errorMsg': errorMsg,'fname': firstname, 'lname': lastname, 'status': stat, 'email': email})
                    if User.objects.filter(username = username).exists():
                        errorMsg = "Username taken" 
                    else:
                        updateUserInfo(username, email, psword, firstname, lastname, stat)
                        return HttpResponseRedirect('/?newAct=2')  
            else: 
                errorMsg = "Could not verify old username and password."
            return render(request, 'CourseGuru_App/editAccount.html', {'errorMsg': errorMsg, 'user': curUser})
        else:
            return render(request, 'CourseGuru_App/editAccount.html', {'user': curUser})    
    else:
        return render(request, 'CourseGuru_App/editAccount.html')
   
def courses(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            if request.POST.get('Logout') == "Logout":
                logout(request)
                return HttpResponseRedirect('/')
            elif request.POST.get('Edit') == 'Edit': 
                return HttpResponseRedirect('/editAccount/')
            elif 'del' in request.POST:
                #Deletes the course selected and all questions, answers, and ratings associated with it
                cid = request.POST.get('del')
                delCourse(cid)
        curUser = request.user
        if curUser.status == "Teacher":
            courseList = course.objects.filter(user_id = curUser.id)
        else:
            courseList = courseusers.objects.filter(user_id = curUser.id)
        return render(request, 'CourseGuru_App/courses.html', {'courses': courseList})
    else:
        return HttpResponseRedirect('/')

def roster(request):
    if request.user.is_authenticated:
        cid = request.GET.get('cid', '')
        cName = course.objects.get(id = cid)
        user = request.user
        if not courseusers.objects.filter(user_id = user.id, course_id = cid).exists() and not course.objects.filter(user_id = user.id, id = cid).exists():
            return redirect('courses')
        studentList = courseusers.objects.filter(course_id=cid)
        if request.method == "POST":
            if request.POST.get('Logout') == "Logout":
                logout(request)
                return HttpResponseRedirect('/')
            elif request.POST.get('Edit') == 'Edit': 
                return HttpResponseRedirect('/editAccount/')
            if 'newUser' in request.POST:
                newUser = request.POST.get('newUser')
                if User.objects.filter(email = newUser).exists():
                    addUser = User.objects.get(email = newUser)
                    if courseusers.objects.filter(user_id = addUser.id, course_id = cid).exists():
                        credentialmismatch = "User is already in the course"
                        return render(request, 'CourseGuru_App/roster.html', {'courseID': cid, 'credentialmismatch': credentialmismatch, 'studentList': studentList})
                    else:
                        userAdded = "User has been successfully added to the course"
                        courseusers.objects.create(user_id = addUser.id, course_id = cid)
                        sendEmailExistingUser(cName.courseName, addUser)
                        return render(request, 'CourseGuru_App/roster.html', {'courseID': cid, 'userAdded': userAdded, 'studentList': studentList})
                else:
                    credentialmismatch = "Email address not yet registered. We have sent an email asking the individual to register."
                    createTempUser(newUser, cid, cName.courseName)
                    addUser = User.objects.get(email = newUser)
                    courseusers.objects.create(user_id = addUser.id, course_id = cid)
                    return render(request, 'CourseGuru_App/roster.html', {'courseID': cid, 'credentialmismatch': credentialmismatch, 'studentList': studentList})
             
            elif 'delete' in request.POST:
                user = request.POST.get('delete')
                rmvUser = courseusers.objects.get(id = int(user))
                courseusers.objects.filter(id = int(user)).delete() 
                remvUserMsg = rmvUser.user.first_name + ' ' + rmvUser.user.last_name + ' has been removed from the course.'            
                return render(request, 'CourseGuru_App/roster.html', {'courseID': cid, 'studentList': studentList, 'notAdded': remvUserMsg})
            elif 'dlCSV' in request.POST:
                response = downloadCSV()
                return response
            elif request.method == 'POST' and request.FILES['csvFile']:
                #getting file and reading it
                csvF = request.FILES['csvFile']
                strNotAdded = readCSV(csvF, cid, cName.courseName)
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
        cid = request.GET.get('cid', '')
        qData = questions.objects.get_queryset().filter(course_id = cid).order_by('-pk')
        page = request.GET.get('page', 1)
        cName = course.objects.get(id = cid)
        user = request.user
        query = request.GET.get('query')
        emptyPostCheck = request.POST.get('query')
        filterCategory = 'All'
        if request.GET.get('filterCategory'):
            filterCategory = request.GET.get('filterCategory')
                    
        if not courseusers.objects.filter(user_id = user.id, course_id = cid).exists() and not course.objects.filter(user_id = user.id, id = cid).exists():
            return redirect('courses')        
        if request.method == "POST":
            if request.POST.get('Logout') == "Logout":
                logout(request)
                return HttpResponseRedirect('/')
            elif request.POST.get('Edit') == 'Edit': 
                return HttpResponseRedirect('/editAccount/')
            elif 'del' in request.POST:
                qid = request.POST.get('del')
                delQuestion(qid)
            if request.POST.get('filterCategory'):
                filterCategory = request.POST.get('filterCategory')
                query = ''
            if request.POST.get('query'):
                query = request.POST.get('query')       

        if filterCategory != 'All':
            qData = qData.filter(category=filterCategory) 
        else:
            qData = questions.objects.get_queryset().filter(course_id = cid).order_by('-pk')
        if emptyPostCheck == '':
            query = ''
            qData = questions.objects.get_queryset().filter(course_id = cid).order_by('-pk')       
        if query and query != '' and query != 'None': 
            qData = qData.filter(Q(question__icontains=query) | Q(comment__icontains=query))  
                
        #Paginator created to limit page display to 10 data items per page
        paginator = Paginator(qData, 10)
        try:
            fquestions = paginator.page(page)
        except PageNotAnInteger:
            fquestions = paginator.page(1)
        except EmptyPage:
            fquestions = paginator.page(paginator.num_pages())       
        return render(request, 'CourseGuru_App/question.html', {'content': fquestions, 'user': user, 'courseID': cid, 'courseName': cName, 'filterCategory': filterCategory, 'query': query})
    else:
        return HttpResponseRedirect('/')

def uploadDocument(request):
    if request.user.is_authenticated:
        cid = request.GET.get('cid', '')
        cName = course.objects.get(id = cid)
        user = request.user
        error = ""
        success = ""
        dest =  settings.MEDIA_ROOT + "/documents/" + cid + "/"
        if not course.objects.filter(user_id = user.id, id = cid).exists() and (courseusers.objects.filter(user_id = user.id, id = cid).exists() and user.status == "TA"):
            return redirect('courses')
        if request.method == "POST":
            if request.POST.get('Logout') == "Logout":
                logout(request)
                return HttpResponseRedirect('/')
            elif request.POST.get('Edit') == 'Edit': 
                return HttpResponseRedirect('/editAccount/')
            elif 'del' in request.POST:
                fid = request.POST.get('del')
                delFile(fid)
            elif len(request.FILES) != 0:
                upFile = request.FILES['courseFile']
                upFileName = upFile.name
                fileType = upFile.content_type
                docType = request.POST.get("docType")

                if os.path.isfile(dest + upFileName):
                    error = "A file with the name " + upFileName + " already exists"
                elif docType == 'Assignment' and document.objects.filter(course_id = cid, category_id = 7).count() > 14:
                    error = "You've reached the maximum number of assignments for this course. (15)"
                elif docType == 'Lecture' and document.objects.filter(course_id = cid, category_id = 8).count() > 14:
                    error = "You've reached the maximum number of lectures for this course. (15)"    
                elif (upFileName.endswith('.docx') and fileType == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document') or (upFileName.endswith('.pdf') and fileType == 'application/pdf') or upFileName.endswith('.pptx'):
                    fileUpload(cid, docType, upFile, upFileName, fileType, user)
                    success = 'Course file successfully uploaded.'
                else:
                    error = 'Course file must be in docx or pdf format.'
        #Syllabus files
        sFiles = document.objects.filter(course_id = cid, category_id = 6).order_by('pk')
        #Assignment files
        aFiles = document.objects.filter(course_id = cid, category_id = 7).order_by('pk')
        #Lecture files
        lFiles = document.objects.filter(course_id = cid, category_id = 8).order_by('pk')
        return render(request, 'CourseGuru_App/uploadDocument.html', {'courseID': cid, 'courseName': cName, 'error': error, 'success': success, 'sFiles': sFiles, 'aFiles': aFiles, 'lFiles': lFiles})
    else:
        return HttpResponseRedirect('/')
    
def courseFiles(request):
    if request.user.is_authenticated:
        cid = request.GET.get('cid', '')
        curCourse = course.objects.get(id = cid)
        user = request.user
        if not courseusers.objects.filter(user_id = user.id, course_id = cid).exists() and not course.objects.filter(user_id = user.id, id = cid).exists():
            return redirect('courses')
        if request.method == "POST":
            if request.POST.get('Logout') == "Logout":
                logout(request)
                return HttpResponseRedirect('/')
            elif 'download' in request.POST:
                fid = request.POST.get('download')
                file = document.objects.get(id = fid)
                fileRtn = HttpResponse(file.docfile, content_type='text/plain')
                fileRtn['Content-Disposition'] = 'attachment; filename=%s' % file.file_name      
                return fileRtn
        #Syllabus files
        sFiles = document.objects.filter(course_id = cid, category_id = 6)
        #Assignment files
        aFiles = document.objects.filter(course_id = cid, category_id = 7)
        #Lecture files
        lFiles = document.objects.filter(course_id = cid, category_id = 8)
        return render(request, 'CourseGuru_App/courseFiles.html', {'course': curCourse, 'sFiles': sFiles, 'aFiles': aFiles, 'lFiles': lFiles})
    else:
        return HttpResponseRedirect('/')

def publish(request):
    if request.user.is_authenticated:
        cid = request.GET.get('cid', '')
        user = request.user
        if not courseusers.objects.filter(user_id = user.id, course_id = cid).exists() and not course.objects.filter(user_id = user.id, id = cid).exists():
            return redirect('courses')
        # Passes in new question when the submit button is selected
        if request.method == "POST":
            if request.POST.get('Logout') == "Logout":
                logout(request)
                return HttpResponseRedirect('/')
            elif request.POST.get('Edit') == 'Edit': 
                return HttpResponseRedirect('/editAccount/')
            ques = request.POST.get('NQ')
            comm = request.POST.get('NQcom')
            #questionDate = genDate()
            user = request.user    
            categ= categorize(ques) 
            
            newQ = questions.objects.create(question = ques, course_id = cid, user_id = user.id, comment = comm, category=categ)    
            botAns = cbAnswer(ques, cid)

            if botAns is not None:
                answers.objects.create(answer = botAns, user_id = 38, question_id = newQ.id)
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
        user = request.user
        if not courseusers.objects.filter(user_id = user.id, course_id = cid).exists() and not course.objects.filter(user_id = user.id, id = cid).exists():
            return redirect('courses')
        if request.method == "POST":
            if request.POST.get('Logout') == "Logout":
                logout(request)
                return HttpResponseRedirect('/')
            elif request.POST.get('Edit') == 'Edit': 
                return HttpResponseRedirect('/editAccount/')
            ans = request.POST.get('NQcom')
            user = request.user
            answers.objects.create(answer = ans, user_id = user.id, question_id = qid)             
            return HttpResponseRedirect('/answer/?id=%s&cid=%s' % (qid, cid))
        return render(request, 'CourseGuru_App/publishAnswer.html', {'Title': qData, 'courseID': cid, 'quesID': qid})
    else:
        return HttpResponseRedirect('/')

def publishCourse(request):
    if request.user.is_authenticated:
        user = request.user
        #If user is not an instructor then get them out
        if user.status != "Teacher":
            return redirect('courses')
        if request.method == "POST":
            if request.POST.get('Logout') == "Logout":
                logout(request)
                return HttpResponseRedirect('/')
            elif request.POST.get('Edit') == 'Edit': 
                return HttpResponseRedirect('/editAccount/')
            newCourse = request.POST.get('NC').strip()
            #cType = request.POST.get('cType')
            user = request.user
            if course.objects.filter(courseName = newCourse, user_id = user.id).exists():
                errorMsg = "You already have a course with this name."
                return render(request, 'CourseGuru_App/publishCourse.html', {'error': errorMsg})
            newCourse = course.objects.create(courseName = newCourse, user_id = user.id)
            cid = newCourse.id
            courseusers.objects.create(user_id = user.id, course_id = cid)
            return HttpResponseRedirect('/courses/')
        return render(request, 'CourseGuru_App/publishCourse.html')
    else:
        return HttpResponseRedirect('/')

# Function to populate Answers page
def answer(request):
    if request.user.is_authenticated:
        qid = request.GET.get('id', '')
        cid = request.GET.get('cid', '')
        user = request.user
        if not courseusers.objects.filter(user_id = user.id, course_id = cid).exists() and not course.objects.filter(user_id = user.id, id = cid).exists():
            return redirect('courses')
        aData = answers.objects.filter(question_id = qid).order_by( '-resolved', 'pk')
        ansCt = aData.count()
        qData = questions.objects.get(id = qid)
  
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
                return render(request, 'CourseGuru_App/answer.html', {'answers': aData, 'numAnswers': ansCt, 'Title': qData, 'courseID': cid, 'resolved':resolve})
            elif 'delAns' in request.POST:
                aid = request.POST.get('delAns')
                delAnswers(aid)
            elif 'delQues' in request.POST:
                delQuestion(qid)
                return HttpResponseRedirect('/question/?cid=%s' % cid)   
            elif 'resolve' in request.POST:
                aid = request.POST.get('resolve')
                resolveQues(cid, aid, qData)
                resolve = True
                aData = answers.objects.filter(question_id = qid).order_by( '-resolved', 'pk')
                return render(request, 'CourseGuru_App/answer.html', {'answers': aData, 'numAnswers': ansCt, 'Title': qData, 'courseID': cid, 'resolved':resolve})        
            return HttpResponseRedirect('/answer/?id=%s&cid=%s' % (qid, cid)) 
        return render(request, 'CourseGuru_App/answer.html', {'answers': aData, 'numAnswers': ansCt, 'Title': qData, 'courseID': cid, 'resolved': resolve, 'upData': upData, 'downData': downData})
    else:
        return HttpResponseRedirect('/')
    
def voting(request):
    rate = request.GET.get('rating')
    answerID = request.GET.get('answer')
    userID = request.GET.get('user')    
    newRating(rate, answerID, userID)
    return HttpResponse()

def chatAnswer(request):
    question = request.GET.get('question')
    cid = request.GET.get('cid')
    botAns = cbAnswer(question, cid, chatWindow=True)
    return HttpResponse(botAns)
