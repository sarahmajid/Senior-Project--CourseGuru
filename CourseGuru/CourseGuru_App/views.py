from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render
import json
from urllib.request import urlopen
import psycopg2






# Create your views here.
def index(request):
    myConnection = psycopg2.connect( host='aa1kaxr8yrczw6m.cynst32f7ubm.us-east-2.rds.amazonaws.com', 
                                     user='cguser', password='csc4996!', dbname='postgres')
    cur = myConnection.cursor()
    cur.execute("SELECT question from questions")
    prt = []
    for row in cur.fetchall():
        prt.append(row[0])
#    prt = ' '.join(prt)
    myConnection.close()
    return render(request, 'CourseGuru_App/index.html', {'content': prt})

def answer(request):
    if request.method=='GET':
        id = request.GET.get('id')
        return render(request, 'CourseGuru_App/answer.html')


def contact(request):
    return render(request, 'CourseGuru_App/index.html', {'content':['Hi','Mike']})


#    url = (urlopen('https://canvas.wayne.edu/api/v1/courses').read()
#    response = urlopen('https://canvas.wayne.edu/api/v1/courses')
#    data = json.load(response)