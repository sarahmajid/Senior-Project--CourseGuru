from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render
import json
from urllib.request import urlopen





# Create your views here.
def index(request):
    return render(request, 'CourseGuru_App/questions.html', {})
#    template = loader.get_template('courseguru_app/index.html')
#    return HttpResponse(template)
#    return HttpResponse("We made it fam!")

def contact(request):
    return render(request, 'CourseGuru_App/index.html', {'content':['Hi','Mike']})


#    url = (urlopen('https://canvas.wayne.edu/api/v1/courses').read()
#    response = urlopen('https://canvas.wayne.edu/api/v1/courses')
#    data = json.load(response)