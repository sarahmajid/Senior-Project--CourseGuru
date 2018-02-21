import CourseGuru_App.luisAuthor
from CourseGuru_App.luisAuthor import addUtterance
import json

def teachLuis(text, intent):

#===============================================================================
# query = "mike testing 2"
#===============================================================================
    data = {}
    data = [{"text": text,
             "intentName": intent,
             "entityLabels": [] }]
    
    with open('CourseGuru_App/static/utterances.json','w') as outfile:
        json.dump(data,outfile)
    
    addUtterance()
    
#----------------------------------- teachLuis("Hello, this is a test.", "Name")
