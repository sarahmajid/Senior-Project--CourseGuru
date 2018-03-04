import re
import tempfile
import json
import requests
import datetime
import PyPDF2
import nltk
import csv 
import io
#===============================================================================
# from sqlalchemy.sql.expression import null, except_
# from urllib.request import urlopen
# from django.http import HttpResponse
# from django.template import loader
#===============================================================================
from django.shortcuts import render, _get_queryset
from django.http.response import HttpResponseRedirect
from pdfminer.pdfparser import PDFParser, PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.layout import LAParams, LTTextBox, LTTextLine, LTTextBoxHorizontal
from pdfminer.converter import PDFPageAggregator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize.moses import MosesDetokenizer, MosesTokenizer

#importing models 
from CourseGuru_App.models import User
from django.shortcuts import render, _get_queryset
from django.http.response import HttpResponseRedirect
#===============================================================================
# from pdfminer.pdfparser import PDFParser, PDFDocument
# from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
# from pdfminer.layout import LAParams, LTTextBox, LTTextLine
# from pdfminer.converter import PDFPageAggregator
#===============================================================================
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

from PyPDF2.generic import PdfObject
from PyPDF2 import pdf
from django.template.context_processors import request
from test.test_decimal import file
from pickle import INST
#from sqlalchemy.sql.expression import null
#from psqlextra.query import ConflictAction
from CourseGuru_App.luisRun import teachLuis
from CourseGuru_App.natLang import reformQuery
from test.test_enum import Answer
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse

from CourseGuru_App.models import courseusers
from CourseGuru_App.models import userratings
from CourseGuru_App.luisRun import teachLuis
from test.test_enum import Answer
from django.contrib.auth import authenticate, login, logout
from pdfminer.pslexer import delimiter
from builtins import str
from django.template.defaultfilters import last
from _ast import Str
from string import ascii_lowercase
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
    if request.method == "POST":
        
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        username = request.POST.get('username')
        psword = request.POST.get('password')
        cpsword = request.POST.get('cpassword')
        stat = request.POST.get('status')       
        passRegCheck = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)"
        if (psword != cpsword):
            mismatch = 'Password Mismatch'
            return render(request, 'CourseGuru_App/account.html', {'msmatch': mismatch, 'fname': firstname, 'lname': lastname, 'status': stat})
        else:
            if (len(psword)<8): 
                mismatch = 'Your password must be at least 8 characters long.'
                return render(request, 'CourseGuru_App/account.html', {'msmatch': mismatch,'fname': firstname, 'lname': lastname, 'status': stat})
            if ((re.search(passRegCheck, psword))==None):
                mismatch = "Your password must contain one uppercase character, one lowercase character, and at least one number!"
                return render(request, 'CourseGuru_App/account.html', {'msmatch': mismatch,'fname': firstname, 'lname': lastname, 'status': stat})
            if User.objects.filter(username = username).exists():
                mismatch = "Username taken"
                return render(request, 'CourseGuru_App/account.html', {'msmatch': mismatch,'fname': firstname, 'lname': lastname, 'status': stat})

            else:
                #edit possibly drop user ID from the table or allow it to be null 
                #user.objects.create(firstName = firstname, lastName = lastname, userName = username, password = psword, status = stat)  
                newUser = User.objects.create_user(username, 'test@test.com', psword) 
                newUser.first_name = firstname
                newUser.last_name = lastname
                newUser.status = stat
                newUser.save()
                return HttpResponseRedirect('/?newAct=1')  
    else:
        return render(request, 'CourseGuru_App/account.html')

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
                    for y in tempAns:
                        if userratings.objects.filter(answer_id = y.id).exists():
                            userratings.objects.filter(answer_id = y.id).delete()
                    if answers.objects.filter(question_id = x.id).exists():
                        answers.objects.filter(question_id = x.id).delete()
                if questions.objects.filter(course_id = cid).exists():
                    questions.objects.filter(course_id = cid).delete()
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
    
    curDate = datetime.datetime.now().strftime("%m-%d-%Y %I:%M %p")

    return (curDate)
def roster(request):
    if request.user.is_authenticated:
        cid = request.GET.get('cid', '')
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
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename=CSVTemplate.csv'
                writer = csv.writer(response)
                writer.writerow(["Username"])
                writer.writerow(["UserName1"])
                writer.writerow(["UserName2"])
                writer.writerow(["UserName3"])
                writer.writerow(["..."])
                return response
            elif request.method == 'POST' and request.FILES['csvFile']:
                #decoding the file for reading 
                csvF = request.FILES['csvFile'].read().decode('utf-8')
                #sniffing for the delimiter in csv
                sniffer = csv.Sniffer().sniff(csvF)         
                #reading csv using DictReader     
                reader = csv.DictReader(((io.StringIO(csvF))), delimiter=sniffer.delimiter)   
                #converts all field names to lowercase
                reader.fieldnames = [header.strip().lower() for header in reader.fieldnames]
                        
                #variable initialization 
                str1 = "The following "
                str2 = " users were not added to the course because the usernames do not exist: "
                strNotAdded = ""
                notAddedUsers = []
                numUserNotAdded=0
                
                #Adds students according to the csv content. If DictReader is changed code below must be edited.            
                for n in reader:
                    if(User.objects.filter(username = n['username'])):
                        addUser = User.objects.get(username = n['username'])
                        if (courseusers.objects.filter(user_id = addUser.id, course_id = cid).exists()==False):
                            courseusers.objects.create(user_id = addUser.id, course_id = cid)
                    else: 
                        notAddedUsers.append(n['username']) 
                        numUserNotAdded+=1   
                        strNotAdded = str1 + str(numUserNotAdded) + str2
                #creates a list of none existing users.         
                if(len(notAddedUsers)>0):
                    for n in notAddedUsers:
                        if n != notAddedUsers[len(notAddedUsers)-1]:
                            strNotAdded += n + ", "
                        else:
                            if (len(notAddedUsers)==1):
                                strNotAdded += n + "."
                                return render(request, 'CourseGuru_App/roster.html', {'courseID': cid, 'studentList': studentList, 'notAdded': strNotAdded})
                            else:
                                strNotAdded += "and " + n +"."
                                return render(request, 'CourseGuru_App/roster.html', {'courseID': cid, 'studentList': studentList, 'notAdded': strNotAdded})
            
            else:
                credentialmismatch = "Username does not exist"
                return render(request, 'CourseGuru_App/roster.html', {'courseID': cid, 'credentialmismatch': credentialmismatch})
        return render(request, 'CourseGuru_App/roster.html', {'courseID': cid, 'studentList': studentList})
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
            
            newQ = questions.objects.create(question = ques, course_id = cid, user_id = user.id, date = questionDate, comment = comm)
            botAns = cbAnswer(ques)
            answerDate = genDate()
            #Simple solution MUST BE CHANGED!!!!!
            syllabus="Syllabus"
            other="Other"
            sylKeyTerms = "syllabus,instructor name,teachers name,grading scale,grade,ta,teaching assistant,student,due date,due,assignment,late"
            n=sylKeyTerms.split(',')
            matchCount = 0
            matchCount=0
            for z in n:
                if ques.__contains__(z):
                    matchCount += 1
                if comm.__contains__(z):
                    matchCount+=1
            if matchCount > 0:
                questions.objects.create(question = ques, course_id = cid, user_id = user.id, date = questionDate, comment = comm, category=syllabus)
            else:
                questions.objects.create(question = ques, course_id = cid, user_id = user.id, date = questionDate, comment = comm, category=other)
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

        if request.method == "POST":
            if request.POST.get('Logout') == "Logout":
                logout(request)
                return HttpResponseRedirect('/')
            if 'voteUp' in request.POST: 
                answerId = request.POST.get('voteUp')
                voting(1, answerId, user)
                return HttpResponseRedirect('/answer/?id=%s&cid=%s' % (qid, cid))
            
            elif 'voteDown' in request.POST: 
                answerId = request.POST.get('voteDown')
                voting(0, answerId, user)
                return HttpResponseRedirect('/answer/?id=%s&cid=%s' % (qid, cid))
            if request.POST.get('query'):
                query = request.POST.get('query')
                if query: 
                    aData = aData.filter(answer__icontains=query)
                return render(request, 'CourseGuru_App/answer.html', {'answers': aData, 'numAnswers': ansCt, 'Title': qData, 'comments': cData, 'courseID': cid})
#            return HttpResponseRedirect('/answer/?id=%s&cid=%s' % (qid, cid))        
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
        return render(request, 'CourseGuru_App/answer.html', {'answers': aData, 'numAnswers': ansCt, 'Title': qData, 'comments': cData, 'courseID': cid})
    else:
        return HttpResponseRedirect('/')
    
def voting(rate, answerId, user):
    if userratings.objects.filter(user_id = user.id, answer_id = answerId).exists():
        newRate = userratings.objects.get(user_id = user.id, answer_id = answerId)
        newRate.rating = rate
        newRate.save()
    else:
        userratings.objects.create(user_id = user.id, answer_id = answerId, rating = rate)    
    uprateCt = userratings.objects.filter(answer_id = answerId, rating = 1).count()
    downrateCt = userratings.objects.filter(answer_id = answerId, rating = 0).count()
    record = answers.objects.get(id = answerId)
    record.rating = (uprateCt - downrateCt)
    record.save()

# returns a good match to entities answer object  
def getIntentAns(luisIntent, luisEntities):    
    count = 0
    answr = ""
    
    entitiesList = luisEntities.split(",")
    catgry = category.objects.get(intent = luisIntent)
    
    filtAns = botanswers.objects.filter(category_id = catgry.id)
     
    for m in filtAns:
        Match = 0
        #testing, change entities name to something else later
        ansLen = len(m.entities)
        for ent in entitiesList:
            print(ent)
            #testing, change entities name to something else later
            if ent in m.entities:
                Match += 1
        Accuracy = (Match/ansLen)
        if Accuracy>count:
            count = Accuracy
            answr = m.answer
            
        #=======================================================================
        # b = m.answer.split(" ")
        # tempCntMtch = 0
        # ttlCnt = len(b)
        # for n in b: 
        #     #if the word in the answer is in the list of entities then increment by 1
        #     if luisEntities.count(n) > 0:
        #         tempCntMtch += 1
        #     cntAccuracy = (tempCntMtch/ttlCnt)
        #     if cntAccuracy>count:
        #         count = cntAccuracy 
        #         answr = m.answer
        #=======================================================================
    #if answr == "":
        #answr = (botanswers.objects.filter(category_id = catgry.id).first()).answer
    return (answr)    

def pdfToText(request):
#    Create empty string for text to be extracted into
    extracted_text = '' 
    test = ''
    #When button is clicked we parse the file
    if request.method == "POST":
        #Sets myfile to the selected file on page and reads it
        myfile = request.FILES.get("syllabusFile").file.read()
            
        #Create tempfile in read and write binary mode
        f = tempfile.TemporaryFile('r+b')
        f.write(myfile)

        #Sets the cursor back to 0 in f to be parsed and sets the documents and parser
        f.seek(0)
        parser = PDFParser(f)
        doc = PDFDocument()
        parser.set_document(doc)
        doc.set_parser(parser)
        doc.initialize('')
        rsrcmgr = PDFResourceManager()
        #sets parameters for analysis 
        laparams = LAParams()
            
        #Required to define seperation of text within pdf
        laparams.char_margin = 1
        laparams.word_margin = 1
            
        #Device takes LAPrams and uses them to parse individual pdf objects
        device = PDFPageAggregator(rsrcmgr, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)
            
        for page in doc.get_pages():
            interpreter.process_page(page)
            layout = device.get_result()
            for lt_obj in layout:
                if isinstance(lt_obj, LTTextBoxHorizontal):
                    extracted_text += lt_obj.get_text() 
        test = pullInfo(extracted_text)   
        f.close() 
    return render(request, 'CourseGuru_App/parse.html', {'convText' : test})

#===============================================================================

#will need a more robust way
def pullInfo(file):

    keyWordObj = courseinfo.objects.all()
    keyWords = []
    #parallel arrays to store the keywords found and their positions 
    keyPositions = []
    keyWordPositions = []
    subCat = ['Name', 'Office location', 'Phone', 'Email', 'Office Hours']
    
    subCatkeyPosition = [] 
    subCatWordPosition = []
    header=[]
    data=[]
#    detokenizer = MosesDetokenizer()
#    tokenizer = MosesTokenizer()
    
#    pdfWords = tokenizer.tokenize(file)
#    print(pdfWords)
#    pdfWords = file.split(' ')
#    print(pdfWords)
    #===========================================================================
    #pdfWords = word_tokenize(file, 'english')
    # retok = detokenizer.detokenize(pdfWords, return_str=True)
    # retok2 = retok.read().decode()
    # retok2 = re.sub("\xe2\x80\x93", "-", retok2)
    # print(retok2)
    #===========================================================================
#    pdfWords = sent_tokenize(file, 'english')

#    for n in pdfWords:
#        words = nltk.word_tokenize(n)
#        tagWords = nltk.pos_tag(words)
#        print(tagWords)
        
    #str(pdfWords)
   # reader = io.StringIO(pdfWords)
    #secondStage = pdfWords.split('\n')
    
    pdfWords = word_tokenize(file, 'english')
    
    for n in keyWordObj:
        keyWords.append(n.intent)
        
           
    # finding all the key word positions 
            
    i=0    
    while i<len(pdfWords)-1:
        for n in keyWords:
            temp = pdfWords[i] + " " + pdfWords[i+1]
            if pdfWords[i] == n or temp == n:
                keyPositions.append(i)
                keyWordPositions.append(n)
                
        i+=1   
   # sub category location finder    
    i=0    
    while i<len(pdfWords)-1:
        for m in subCat: 
            temp = pdfWords[i] + " " + pdfWords[i+1]
            if pdfWords[i] == m or temp == m:
                subCatkeyPosition.append(i)
                subCatWordPosition.append(m)  
        i+=1 
        
    i=0
    while i<len(keyPositions)-1:
        j=0
        while j<len(subCatkeyPosition)-1:
            k = len(subCatkeyPosition)-1
            if ((j%(len(subCat)-1) == 0) and (subCatkeyPosition[j] < keyPositions[i+1]) and keyPositions[i] < subCatkeyPosition[j] and j>0):
                header.append(keyWordPositions[i]+' '+subCatWordPosition[j]) 
                data.append(pdfWords[subCatkeyPosition[j]:keyPositions[i+1]])
                j+=1
            else:
                if (keyPositions[i] < subCatkeyPosition[j] and subCatkeyPosition[j] < keyPositions[i+1]):
                    header.append(keyWordPositions[i]+' '+subCatWordPosition[j]) 
                    data.append(pdfWords[subCatkeyPosition[j]:subCatkeyPosition[j+1]])
                    j+=1
                else: 
                    j+=1
        i+=1
        
    for n in header: 
        print(n) 
    for n in data: 
        print(n)
        
    #to end of file    
    keyPositions.append(len(pdfWords))
    # loops through the key positions and puts data into appropriate rows according to intent name 
    i=0
    while i <len(keyPositions)-1:      
        intent = keyWordObj.get(intent = keyWordPositions[i])
        intent.infoData=(pdfWords[keyPositions[i]:keyPositions[i+1]])
        #intent.save()
        i+=1
    return(pdfWords)
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
    
    entAnswer = getIntentAns(luisIntent, luisEntities)
    if entAnswer == "":
        return
    botAns = reformQuery(nq) + entAnswer
    return(botAns)


def chatAnswer(request):
    question = request.GET.get('question')
    botAns = cbAnswer(question)
    return HttpResponse(botAns)
    
