import re
import tempfile
import json
import requests
import datetime
import io

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
from django.shortcuts import redirect


#importing models 
from CourseGuru_App.models import questions
from CourseGuru_App.models import answers
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
from CourseGuru_App.luisRun import publishLUIS
from CourseGuru_App.catQuestion import *
from CourseGuru_App.validate import *
from CourseGuru_App.botFunctions import *
from CourseGuru_App.tasks import queuePublish

from builtins import str

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
                #Delete botanswers related to this course
                if botanswers.objects.filter(course_id = cid).exists():
                    botanswers.objects.filter(course_id = cid).delete()
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
        user = request.user
        if not courseusers.objects.filter(user_id = user.id, course_id = cid).exists() and not course.objects.filter(user_id = user.id, id = cid).exists():
            return redirect('courses')
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
        user = request.user
        if not courseusers.objects.filter(user_id = user.id, course_id = cid).exists() and not course.objects.filter(user_id = user.id, id = cid).exists():
            return redirect('courses')
        
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
                
        #Paginator created to limit page display to 10 data items per page
        paginator = Paginator(qData, 10)
        try:
            fquestions = paginator.page(page)
        except PageNotAnInteger:
            fquestions = paginator.page(1)
        except EmptyPage:
            fquestions = paginator.page(paginator.num_pages())       
        return render(request, 'CourseGuru_App/question.html', {'content': fquestions, 'user': user, 'courseID': cid, 'courseName': cName, 'status': filterCategory})
    else:
        return HttpResponseRedirect('/')

def uploadDocument(request):
    if request.user.is_authenticated:
        cid = request.GET.get('cid', '')
        cName = course.objects.get(id = cid)
        user = request.user
        if not course.objects.filter(user_id = user.id, id = cid).exists():
            return redirect('courses')
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
        user = request.user
        if not courseusers.objects.filter(user_id = user.id, course_id = cid).exists() and not course.objects.filter(user_id = user.id, id = cid).exists():
            return redirect('courses')
        # Passes in new question when the submit button is selected
        if request.method == "POST":
            if request.POST.get('Logout') == "Logout":
                logout(request)
                return HttpResponseRedirect('/')
            ques = request.POST.get('NQ')
            comm = request.POST.get('NQcom')
            questionDate = genDate()
            user = request.user    
            categ= categorize(ques) 

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
        user = request.user
        #If user is not an instructor then get them out
        if user.status != "Teacher":
            return redirect('courses')
        if request.method == "POST":
            if request.POST.get('Logout') == "Logout":
                logout(request)
                return HttpResponseRedirect('/')
            newCourse = request.POST.get('NC')
            cType = request.POST.get('cType')
            user = request.user
            if course.objects.filter(courseName = newCourse, user_id = user.id).exists():
                errorMsg = "You already have a course with this name."
                return render(request, 'CourseGuru_App/publishCourse.html', {'error': errorMsg})
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
        if not courseusers.objects.filter(user_id = user.id, course_id = cid).exists() and not course.objects.filter(user_id = user.id, id = cid).exists():
            return redirect('courses')
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
                profRate = False
                if ans.user_id != 38:
                    ansRatings = userratings.objects.filter(answer_id = ans.id)
                    for row in ansRatings:
                        rowUser = row.user_id
                        rateUser = User.objects.get(id = rowUser)
                        if rateUser.status == "Teacher":
                            profRate = True  
                    if ans.rating > 2 or profRate:
                        detokenizer = MosesDetokenizer()
                        data_list = nltk.word_tokenize(qData.question)
                        data = [word for word in data_list if word not in stopwords.words('english')]
                        detokenizer.detokenize(data, return_str=True)
                        dbInfo = " ".join(data).lower()
                        botanswers.objects.create(answer = ans.answer, rating = 0, category_id = 9, entities = dbInfo, course_id = cid)
                        teachLuis(qData.question, 'Other')

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
  def chatbot(request):
    return render(request, 'CourseGuru_App/botchat.html',)

def chatAnswer(request):
    question = request.GET.get('question')
    cid = request.GET.get('cid')
    botAns = cbAnswer(question, cid, chatWindow=True)
    return HttpResponse(botAns)
