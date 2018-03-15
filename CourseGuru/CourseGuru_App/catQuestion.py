'''
Created on Mar 10, 2018

@author: Andriy Marynovskyy
'''
import json
import requests

def categorize(nq):
    
    noCat='Other'
    
    r = requests.get('https://westus.api.cognitive.microsoft.com/luis/v2.0/apps/ea475a53-c283-4ddc-ae52-1de7421ecf26?subscription-key=c574439a46e64d8cb597879499ccf8f9&verbose=true&timezoneOffset=-300&q=%s' % nq)
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

