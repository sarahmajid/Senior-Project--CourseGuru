
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render
import json
from urllib.request import urlopen
import psycopg2
from django.http.response import HttpResponseRedirect
import tempfile
from pdfminer.pdfparser import PDFParser, PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.layout import LAParams, LTTextBox, LTTextLine
from pdfminer.converter import PDFPageAggregator
import re
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

#importing models 
from CourseGuru_App.models import user
from CourseGuru_App.models import course
from CourseGuru_App.models import questions
from CourseGuru_App.models import answers
from CourseGuru_App.models import category
from CourseGuru_App.models import botanswers
from CourseGuru_App.models import keywords
from CourseGuru_App.models import courseinfo
from test.test_enum import Answer
import shutil
from sqlalchemy.sql.expression import null, except_




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
    qData = questions.objects.get_queryset().order_by('id')
    page = request.GET.get('page', 1)
    
    paginator = Paginator(qData, 10)
    try:
        fquestions = paginator.page(page)
    except PageNotAnInteger:
        fquestions = paginator.page(1)
    except EmptyPage:
        fquestions = paginator.page(paginator.num_pages())
    return render(request, 'CourseGuru_App/question.html', {'content': fquestions})

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

    return render(request, 'CourseGuru_App/answer.html', {'answers': aData, 'Title': qData})

def chatbot(request):
    return render(request, 'CourseGuru_App/botchat.html',)

def parse(request):
    extracted_text = ''
    if request.method == "POST":
        myfile = request.FILES.get("syllabusFile").file.read()
        f = tempfile.TemporaryFile('r+b')
        f.write(myfile)
        f.seek(0)
        parser = PDFParser(f)
        doc = PDFDocument()
        parser.set_document(doc)
        doc.set_parser(parser)
        doc.initialize('')
        rsrcmgr = PDFResourceManager()
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
                if isinstance(lt_obj, LTTextBox) or isinstance(lt_obj, LTTextLine):
                    extracted_text += lt_obj.get_text()
        
        f.close()
        kData = keywords.objects.all()
        for k in kData:
            results = re.search(k.word + "(.*)", extracted_text, re.MULTILINE)
            courseinfo.objects.create(keyword_common_name = k.common_name, syllabus_data = results.group(1), course_id = 'CSC 3110')
            return render(request, 'CourseGuru_App/parse.html', {'keywords': kData})
    kData = keywords.objects.all()
    return render(request, 'CourseGuru_App/parse.html', {'keywords': kData})
#    ---Canvas code---
#    url = (urlopen('https://canvas.wayne.edu/api/v1/courses').read()
#    response = urlopen('https://canvas.wayne.edu/api/v1/courses')
#    data = json.load(response)