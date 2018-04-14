import nltk, re, tempfile
from nltk.corpus import stopwords
from nltk.tokenize.moses import MosesDetokenizer

from CourseGuru_App.models import questions
from CourseGuru_App.models import answers
from CourseGuru_App.models import userratings
from CourseGuru_App.models import courseusers
from CourseGuru_App.models import course
from CourseGuru_App.models import botanswers
from CourseGuru_App.models import User
from CourseGuru_App.models import document
from CourseGuru_App.models import category
from CourseGuru_App.luisRun import teachLuis
from CourseGuru_App.pdfParser import pdfToText
from CourseGuru_App.docxParser import docxParser
from CourseGuru_App.pptxParser import parsePPTX
from django.conf import settings
import os.path

import win32com.client as win32
from win32com.client import constants
import pythoncom
import win32com.client as client

def delCourse(cid):
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
    #Delete files associated with this course
    if document.objects.filter(course_id = cid).exists():
        document.objects.filter(course_id = cid).delete()
            
        
def delQuestion(qid):
    tempAns = answers.objects.filter(question_id = qid)
    for x in tempAns:
        if userratings.objects.filter(answer_id = x.id).exists():
            userratings.objects.filter(answer_id = x.id).delete()
    if answers.objects.filter(question_id = qid).exists():
        answers.objects.filter(question_id = qid).delete()
    if questions.objects.filter(id = qid).exists():
        questions.objects.filter(id = qid).delete()
        
def delAnswers(aid):
    if userratings.objects.filter(answer_id = aid).exists():
        userratings.objects.filter(answer_id = aid).delete()
    if answers.objects.filter(id = aid).exists():
        answers.objects.filter(id = aid).delete()

def delFile(fid):
    botanswers.objects.filter(file_id = fid).delete()
    document.objects.filter(id = fid).delete()
        
def resolveQues(cid, aid, qData):
    ans = answers.objects.get(id = aid)
    ans.resolved = True
    ans.save()
    profRate = False
    taRate = False
    checked = False
    if ans.user_id != 38:
        ansRatings = userratings.objects.filter(answer_id = ans.id)
        if ans.user.status == "Teacher":
            profRate = True
        elif ans.user.status == "TA":
            taRate = True
        else:
            for row in ansRatings:
                rowUser = row.user_id
                rateUser = User.objects.get(id = rowUser)
                if (rateUser.status == "Teacher" or rateUser.status == "TA") and row.rating == 1:
                    checked = True  
        rostSize = courseusers.objects.filter(course_id = cid).count()
        weight = (ans.rating / rostSize) * 100
        if weight >= 5 or profRate or taRate or checked:
            detokenizer = MosesDetokenizer()
            data_list = nltk.word_tokenize(qData.question)
            data = [word for word in data_list if word not in stopwords.words('english')]
            detokenizer.detokenize(data, return_str=True)
            dbInfo = " ".join(data).lower()
            merit = 0
            if taRate:
                merit = 1
            elif profRate:
                merit = 2
            exampleID = teachLuis(qData.question, 'Other')
            botanswers.objects.create(answer = ans.answer, rating = merit, category_id = 9, entities = dbInfo, course_id = cid, example_id = exampleID)
            
            
def newRating(rate, answerID, userID):
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

def fileUpload(cid, docType, upFile, upFileName, fileType, user):
    if docType == 'Syllabus' and document.objects.filter(course_id = cid, category_id = 6).exists():
        file = document.objects.get(course_id = cid, category_id = 6)
        delFile(file.id)
    catID = category.objects.get(intent = docType)
    newFile = document(docfile = upFile, uploaded_by_id = user.id, course_id = cid, category_id = catID.id, file_name = upFileName)
    newFile.save()
    
    #if upFileName.endswith('.doc'):
    #    docToDocx(dest, upFileName)
    courseFile = newFile.docfile.read()
    f = tempfile.TemporaryFile('r+b')
    f.write(courseFile)    
                        
    if upFileName.endswith('.docx') and fileType == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
        docxParser(f, cid, catID, newFile.id, docType)
    elif upFileName.endswith('.pdf') and fileType == 'application/pdf':
        pdfToText(f, cid, catID, newFile.id, docType)
    else: 
        parsePPTX(upFile, cid, catID, newFile.id, docType)
    newFile.docfile.close()
    
def docToDocx(dest, upFileName):
    pythoncom.CoInitialize()
    word = win32.gencache.EnsureDispatch('Word.Application')
    doc = word.Documents.Open(dest + upFileName)
    doc.Activate ()
    newName = dest + os.path.splitext(upFileName)[0] + 'NEW'
    new_file_abs = re.sub(r'\.\w+$', '.docx', newName)
    word.ActiveDocument.SaveAs(
        new_file_abs, FileFormat=constants.wdFormatXMLDocument
    )
    doc.Close(False)
