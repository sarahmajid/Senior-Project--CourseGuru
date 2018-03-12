from CourseGuru_App.luisAuthor import addUtterance
import json
import sys, os.path
import django.http
import http
import requests

def teachLuis(text, intent):

#===============================================================================
# query = "mike testing 2"
#===============================================================================
    data = {}
    data = [{"text": text,
             "intentName": intent,
             "entityLabels": [] }]
    
    with open('CourseGuru/CourseGuru_App/static/utterances.json','w') as outfile:
        json.dump(data,outfile)
    
    addUtterance()
    
#----------------------------------- teachLuis("Hello, this is a test.", "Name")



def publishLUIS():
    path = "https://westus.api.cognitive.microsoft.com/luis/api/v2.0/apps/6059c365-d88a-412b-8f33-d7393ba3bf9f/versions/0.1/publish"
    headers = {"Content-type": "application/json","Ocp-Apim-Subscription-Key": "c574439a46e64d8cb597879499ccf8f9"}
#     filename = "CourseGuru/CourseGuru_App/static/publish.json"
#     with open(filename, 'r') as utterance:
#         data = utterance.read()
#     conn = http.client.HTTPSConnection("westus.api.cognitive.microsoft.com")
#     conn.request("POST", path, data.encode("UTF-8") or None, headers)
    
    requests.post(path, headers)

    print("Publish requested successfully")

