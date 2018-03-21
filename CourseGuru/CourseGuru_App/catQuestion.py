'''
Created on Mar 10, 2018

@author: Andriy Marynovskyy
'''
import json
import requests

def categorize(nq):
    
    noCat='Other'
    
    r = requests.get('https://westus.api.cognitive.microsoft.com/luis/v2.0/apps/6059c365-d88a-412b-8f33-d7393ba3bf9f?subscription-key=c574439a46e64d8cb597879499ccf8f9&verbose=true&timezoneOffset=0&q=%s' % nq)
    luisStr = json.loads(r.text)
    #Grabs intent score of question
    luisScore = float(luisStr['topScoringIntent']['score'])
    #Grabs intent of question
    luisIntent = luisStr['topScoringIntent']['intent']

    #If intent receives a lower score than 75% or there is no intent, the question does not get answered
    if luisScore < 0.75 or luisIntent == 'None':
        return noCat
    else: 
        return luisIntent

