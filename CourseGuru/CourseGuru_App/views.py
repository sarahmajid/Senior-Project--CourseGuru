from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render
import json
from urllib.request import urlopen
import psycopg2




# Create your views here.
def index(request):
    myConnection = psycopg2.connect(host = 'Localhost', user = 'postgres', password ='postgres', dbname = 'CourseGuruDB')
    cur = myConnection.cursor()
    cur.execute("Select name from Test")
    #for name in cur.fetchall():
       ## prt = name
    prt = [row[0] for row in cur.fetchall()]
    myConnection.close()
    return render(request, 'CourseGuru_App/index.html',{'content': prt})
#    template = loader.get_template('courseguru_app/index.html')
#    return HttpResponse(template)
#    return HttpResponse("We made it fam!")

def QAP(request):
    return render(request, 'CourseGuru_App/QAP.html')


#    url = (urlopen('https://canvas.wayne.edu/api/v1/courses').read()
#    response = urlopen('https://canvas.wayne.edu/api/v1/courses')
#    data = json.load(response)