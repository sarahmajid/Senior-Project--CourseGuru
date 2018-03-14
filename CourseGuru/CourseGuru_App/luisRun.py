from CourseGuru_App.luisAuthor import addUtterance
import json
import http
import http.client, urllib.request, urllib.parse, urllib.error, base64

def teachLuis(text, intent):

    data = {}
    data = [{"text": text,
             "intentName": intent,
             "entityLabels": [] }]
    
    with open('CourseGuru/CourseGuru_App/static/utterances.json','w') as outfile:
        json.dump(data,outfile)
    
    addUtterance()



def publishLUIS():
    headers = {
        'Content-Type': 'application/json',
        'Ocp-Apim-Subscription-Key': 'c574439a46e64d8cb597879499ccf8f9',
    }
    filename = 'CourseGuru/CourseGuru_App/static/publish.json'
    with open(filename, 'r') as publishJson:
            data = publishJson.read()
    
    params = urllib.parse.urlencode({
    })
    
    try:
        conn = http.client.HTTPSConnection('westus.api.cognitive.microsoft.com')
        conn.request("POST", "/luis/api/v2.0/apps/6059c365-d88a-412b-8f33-d7393ba3bf9f/publish?%s" % params, data.encode("UTF-8"), headers)
        response = conn.getresponse()
        data = response.read()
        print(data)
        conn.close()
    except Exception as e:
        print("LUIS Publish failed")


