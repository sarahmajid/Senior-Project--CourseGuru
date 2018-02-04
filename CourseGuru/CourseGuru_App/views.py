#===============================================================================
# import json
# import psycopg2
# import shutil
#===============================================================================
import re
import tempfile

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


#importing models 
from CourseGuru_App.models import user

from CourseGuru_App.models import questions
from CourseGuru_App.models import answers
from CourseGuru_App.models import keywords
from CourseGuru_App.models import courseinfo
#===============================================================================
# from CourseGuru_App.models import course
# from CourseGuru_App.models import category
# from CourseGuru_App.models import botanswers
# from test.test_enum import Answer
#===============================================================================





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
        #Set parameters from page to be passed to db
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        username = request.POST.get('username')
        psword = request.POST.get('password')
        cpsword = request.POST.get('cpassword')
        stat = request.POST.get('status')       
        mismatch = 'Password Mismatch'
        #If password doesnt match display page again with info but password mismatch error
        if (psword != cpsword):
            return render(request, 'CourseGuru_App/account.html', {'fname': firstname, 'lname': lastname, 'uname': username, 'status': stat,'msmatch': mismatch})
        else:
            #edit possibly drop user ID from the table or allow it to be null 
            user.objects.create(firstName = firstname, lastName = lastname, userName = username, password = psword, status = stat)   
        
    return render(request, 'CourseGuru_App/account.html')

def question(request):
    # Passes in new question when the submit button is selected
    if request.method == "POST":
        newquestion = request.POST.get('NewQuestion')
        questions.objects.create(question = newquestion, course_id = 1, user_id = 1)
        return HttpResponseRedirect('/question/')    
    
    #Grabs the questions form the db and orders them by id in desc fashion so the newest are first
    qData = questions.objects.get_queryset().order_by_desc('id')
    page = request.GET.get('page', 1)
    
    #Paginator created to limit page display to 10 data items per page
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
    
    #Grab question id to associate with answer
    qid = request.GET.get('id', '') 
    
    #Create new answer
    if request.method == "POST":
        ans = request.POST.get('ANS')
        answers.objects.create(answer = ans, user_id = 1, question_id = qid)
        return HttpResponseRedirect('/answer/?id=%s' % qid)
    
    #Set question and answers 
    aData = answers.objects.filter(question_id = qid)
    qData = questions.objects.get(id = qid)
    return render(request, 'CourseGuru_App/answer.html', {'answers': aData, 'Title': qData})

def chatbot(request):
    return render(request, 'CourseGuru_App/botchat.html',)

def parse(request):
    #Create empty string for text to be extracted into
    extracted_text = ''
    
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
        courseid = re.search('[A-Z]{3} \d{4}', extracted_text, re.MULTILINE)
        f.close()
        kData = keywords.objects.all()
        for k in kData:
            results = re.search(k.word + "(.*)", extracted_text, re.MULTILINE)
            if results is not None:
                info = re.sub('[^0-9a-zA-Z][ ]', '', results.group(1))
                courseinfo.objects.create(keyword_common_name = k.common_name, syllabus_data = info, course_id = courseid[0])
    return render(request, 'CourseGuru_App/parse.html')
#    ---Canvas code---
#    url = (urlopen('https://canvas.wayne.edu/api/v1/courses').read()
#    response = urlopen('https://canvas.wayne.edu/api/v1/courses')
#    data = json.load(response)