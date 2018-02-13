import re
import tempfile
import json
import requests
import datetime
#===============================================================================
# from sqlalchemy.sql.expression import null, except_
# from urllib.request import urlopen
# from django.http import HttpResponse
# from django.template import loader
#===============================================================================
from django.shortcuts import render
from django.http.response import HttpResponseRedirect
from pdfminer.pdfparser import PDFParser, PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.layout import LAParams, LTTextBox, LTTextLine
from pdfminer.converter import PDFPageAggregator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.models import User


#importing models 
#from CourseGuru_App.models import user

from CourseGuru_App.models import questions
from CourseGuru_App.models import answers
from CourseGuru_App.models import keywords
from CourseGuru_App.models import courseinfo
from CourseGuru_App.models import course
from CourseGuru_App.models import category
from CourseGuru_App.models import botanswers
from CourseGuru_App.models import comments


from test.test_enum import Answer
from django.contrib.auth import authenticate, login

#Function to populate Main page
def index(request):
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
                    return HttpResponseRedirect('/question/')
            else:
                return render(request, 'CourseGuru_App/index.html')
    
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
       
        if (psword != cpsword):
            mismatch = 'Password Mismatch'
            return render(request, 'CourseGuru_App/account.html', {'msmatch': mismatch})
        else:
            if User.objects.filter(username = username).exists():
                mismatch = "Username taken"
                return render(request, 'CourseGuru_App/account.html', {'msmatch': mismatch})
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

def genDate():
    
    curDate = datetime.datetime.now().strftime("%m-%d-%Y %I:%M %p")
        
    return (curDate)


# Function to populate Main page
def question(request):
    
        #Grabs the questions form the db and orders them by id in desc fashion so the newest are first
    qData = questions.objects.get_queryset().order_by('pk')
    page = request.GET.get('page', 1)
    
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
    
    return render(request, 'CourseGuru_App/question.html', {'content': fquestions, 'user': user})

def publish(request):
    # Passes in new question when the submit button is selected
    if request.method == "POST":
        if request.GET.get('type') == "Question":
            ques = request.POST.get('NQ')
            comm = request.POST.get('NQcom')
            questionDate = genDate()
            user = request.user
            questions.objects.create(question = ques, course_id = 1, user_id = user.id, date = questionDate, comment = comm)
            cbAnswer(ques)
            return HttpResponseRedirect('/question/') 
    return render(request, 'CourseGuru_App/publish.html', {})

def publishAnswer(request):
    qid = request.GET.get('id', '')
    qData = questions.objects.get(id = qid)
    if request.method == "POST":
        if request.GET.get('type') == "Answer":
                ans = request.POST.get('NQcom')
                answerDate = genDate()
                user = request.user
                answers.objects.create(answer = ans, user_id = user.id, question_id = qid, date = answerDate)
                return HttpResponseRedirect('/answer/?id=%s' % qid)
    return render(request, 'CourseGuru_App/publishAnswer.html', {'Title': qData})

# Function to populate Answers page
def answer(request):
#    if request.method=='GET':
    qid = request.GET.get('id', '')
    user = request.user
    if request.method == "POST":
        if 'voteUp' in request.POST: 
            answerId = request.POST.get('voteUp')
            record = answers.objects.get(id = answerId)
            record.rating = record.rating + 1
            record.save()
            return HttpResponseRedirect('/answer/?id=%s' % qid)
        elif 'voteDown' in request.POST: 
            answerId = request.POST.get('voteDown')
            record = answers.objects.get(id = answerId)
            record.rating = record.rating - 1
            record.save()
            return HttpResponseRedirect('/answer/?id=%s' % qid)
        
        return HttpResponseRedirect('/answer/?id=%s' % qid)  
    aData = answers.objects.filter(question_id = qid).order_by('date')
    qData = questions.objects.get(id = qid)
    cData = comments.objects.filter(question_id = qid)
    return render(request, 'CourseGuru_App/answer.html', {'answers': aData, 'Title': qData, 'comments': cData})

# returns a good match to entities answer object  
def getIntentAns(luisIntent, luisEntities):    

    count = 0
    answr = ""
    
    entitiesList = luisEntities.split(",")
    catgry = category.objects.get(intent = luisIntent)
    
    filtAns = botanswers.objects.filter(category_id = catgry.id)
     
    for m in filtAns:
        b = m.answer.split(" ")
        tempCntMtch = 0
        ttlCnt = len(b)
        for n in b: 
            tempCntMtch += entitiesList.count(n)
            cntAccuracy = (tempCntMtch/ttlCnt)
            if cntAccuracy>count:
                count = cntAccuracy 
                answr = botanswers.objects.get(id = m.id)
    return (answr)    


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
    luisEntity = luisStr['entities']
    #If intent receives a lower score than 60% or there is no intent, the question does not get answered
    if luisScore < 0.6 or luisIntent == 'None':
        return
    catID = category.objects.get(intent=luisIntent)
    #Sets cbAns to the first answer it can find matching that category (This needs to be improved)
    cbAns = botanswers.objects.filter(category_id = catID.id).first()
    #ID of the latest question created
    qid = questions.objects.last()
    answerDate = genDate()
    answers.objects.create(answer = cbAns.answer, user_id = 38, question_id = qid.id, date = answerDate)
#    return(intent)

#    ---Canvas code---
#    url = (urlopen('https://canvas.wayne.edu/api/v1/courses').read()
#    response = urlopen('https://canvas.wayne.edu/api/v1/courses')

def parse(request):
    #Create empty string for text to be extracted into
#     extracted_text = ''
#     
#     #When button is clicked we parse the file
#     if request.method == "POST":
#         #Sets myfile to the selected file on page and reads it
#         myfile = request.FILES.get("syllabusFile").file.read()
#         
#         #Create tempfile in read and write binary mode
#         f = tempfile.TemporaryFile('r+b')
#         f.write(myfile)
#         
#         #Sets the cursor back to 0 in f to be parsed and sets the documents and parser
#         f.seek(0)
#         parser = PDFParser(f)
#         doc = PDFDocument()
#         parser.set_document(doc)
#         doc.set_parser(parser)
#         doc.initialize('')
#         rsrcmgr = PDFResourceManager()
#         laparams = LAParams()
#         
#         #Required to define seperation of text within pdf
#         laparams.char_margin = 1
#         laparams.word_margin = 1
#         
#         #Device takes LAPrams and uses them to parse individual pdf objects
#         device = PDFPageAggregator(rsrcmgr, laparams=laparams)
#         interpreter = PDFPageInterpreter(rsrcmgr, device)
#         
#         for page in doc.get_pages():
#             interpreter.process_page(page)
#             layout = device.get_result()
#             for lt_obj in layout:
#                 if isinstance(lt_obj, LTTextBox) or isinstance(lt_obj, LTTextLine):
#                     extracted_text += lt_obj.get_text()
#         courseid = re.search('[A-Z]{3} \d{4}', extracted_text, re.MULTILINE)
#         f.close()
#         kData = keywords.objects.all()
#         for k in kData:
#             results = re.search(k.word + "(.*)", extracted_text, re.MULTILINE)
#             if results is not None:
#                 info = re.sub('[^0-9a-zA-Z][ ]', '', results.group(1))
#                 courseinfo.objects.create(keyword_common_name = k.common_name, syllabus_data = info, course_id = courseid[0])
    return render(request, 'CourseGuru_App/parse.html')

#===============================================================================
# def fileParser(file):
#     
#     
#     
#     return(csvFile)
#===============================================================================
