from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render
import json
from urllib.request import urlopen
import psycopg2
#importing modes 
from CourseGuru_App.models import user
from CourseGuru_App.models import course
from CourseGuru_App.models import questions
from CourseGuru_App.models import answers






# Create your views here.
def index(request):
    #===========================================================================
    # myConnection = psycopg2.connect( host='aa1kaxr8yrczw6m.cynst32f7ubm.us-east-2.rds.amazonaws.com', 
    #                                  user='cguser', password='csc4996!', dbname='postgres')
    # cur = myConnection.cursor()
    # cur.execute("SELECT question from questions")
    #===========================================================================
# creates an object of the questions table
#    prt = []
#    for row in data:
#        prt.append(row[0])
#    prt = ' '.join(prt)
#    myConnection.close()
#    return render(request, 'CourseGuru_App/index.html', {'content': prt})
    questionData = questions.objects.all() 
    return render(request, 'CourseGuru_App/index.html',{'questionData': questionData})

def answer(request):
    #===========================================================================
    # if request.method=='GET':
    #     id = request.GET.get('id')
    #     myConnection = psycopg2.connect( host='aa1kaxr8yrczw6m.cynst32f7ubm.us-east-2.rds.amazonaws.com', 
    #                                  user='cguser', password='csc4996!', dbname='postgres')
    #     cur = myConnection.cursor()
    #     cur.execute("select answer from answers a right join questions b on a.q_id = b.q_id where question = '" + id + "'")
    #     prt = []
    #     for row in cur.fetchall():
    #         prt.append(row[0])
    #     return render(request, 'CourseGuru_App/answer.html', {'content': prt})
    #===========================================================================

    if request.method=='GET':
        id = request.GET.get('id')
        #need to edit the modules answer table where foreign key writes quesitonID
        answerData = answers.objects.filter(quesitonID = id) 
        return render(request, 'CourseGuru_App/answer.html',{'answerData': answerData})




#    url = (urlopen('https://canvas.wayne.edu/api/v1/courses').read()
#    response = urlopen('https://canvas.wayne.edu/api/v1/courses')
#    data = json.load(response)