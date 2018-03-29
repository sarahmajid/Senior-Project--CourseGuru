import requests, json, nltk, re, string
from nltk.stem.wordnet import WordNetLemmatizer
from CourseGuru_App.models import category, botanswers
from nltk.corpus import stopwords
from nltk.tokenize.moses import MosesDetokenizer


def cbAnswer(nq, courseID=0, chatWindow=False):
    r = requests.get('https://westus.api.cognitive.microsoft.com/luis/v2.0/apps/6059c365-d88a-412b-8f33-d7393ba3bf9f?subscription-key=c574439a46e64d8cb597879499ccf8f9&verbose=true&timezoneOffset=-300&q=%s' % nq)
    luisStr = json.loads(r.text)
    #Grabs intent score of question
    luisScore = float(luisStr['topScoringIntent']['score'])
    #Grabs intent of question
    luisIntent = luisStr['topScoringIntent']['intent']
    #Grabs entities
    if luisIntent == 'Greetings' and chatWindow == True:
        return('Hello, how can I help you?')
    elif luisIntent == 'Greetings':
        return
    #If intent receives a lower score than 75% or there is no intent, the question does not get answered
    elif luisIntent == "None" and chatWindow == True:
        return("Sorry, I didn't understand that.")
    elif luisIntent == "None":
        return
    
    #teachLuis(nq, 'Other')
    
    luisEntities = ""
    
    #regex = re.compile('[^a-zA-Z]')
    if luisIntent != 'Other':
        z = 0
        for x in luisStr['entities']:
            newEnt = luisStr['entities'][z]['entity']
            #newEnt = regex.sub('', newEnt)
            if z == 0:
                luisEntities += newEnt
            else:
                luisEntities += ',' + newEnt
            z += 1
    else: 
        #Manual stripping question for entities
        detokenizer = MosesDetokenizer()
        ent_list = nltk.word_tokenize(nq)
        ent_list = [word for word in ent_list if word not in stopwords.words('english')]
        detokenizer.detokenize(ent_list, return_str=True)
        ent_str = " ".join(ent_list).lower()
        #Removes punctuation from string
        regex = re.compile('[%s]' % re.escape(string.punctuation))
        ent_str = regex.sub('', ent_str)
        luisEntities = re.sub("\s+", ",", ent_str.strip())   
    
    if luisEntities == '' and chatWindow == True:
        return("Sorry, I didn't understand that.")
    elif luisEntities == '':
        return   
    
    #Add variations of names a student would call the teacher if one is found
    profNames = ['instructor','teacher','professor']
    for name in profNames:
        if name in luisEntities.lower():
            for addName in profNames:
                if addName not in luisEntities.lower():
                    luisEntities += ',' + addName
        else:
            continue
        break
    if 'ta' in luisEntities.lower():
        luisEntities += ',' + 'teaching assistant'
                    
    
    entAnswer = getIntentAns(luisIntent, luisEntities, courseID, chatWindow)
    if entAnswer == "":
        return
    #botAns = reformQuery(nq) + entAnswer
    botAns = entAnswer
    return(botAns)

# returns a good match to entities answer object  
def getIntentAns(luisIntent, luisEntities, courseID=0, chatWindow=False):    
    count = 0
    answr = ""
    
    entitiesList = luisEntities.lower().split(",")
    catgry = category.objects.get(intent = luisIntent)
    
    #Changes plural to singular
    #lem = WordNetLemmatizer()
    #for ind, ent in enumerate(entitiesList):
    #    entitiesList[ind] = lem.lemmatize(ent)
    
    #Temporary until lemmatizer is fixed
    for ind, ent in enumerate(entitiesList):
        if ent[-1:].lower() == 's':
            entitiesList[ind] = ent[:-1]
    
    if courseID != 0:
        filtAns = botanswers.objects.filter(category_id = catgry.id, course_id = courseID)
    else:
        filtAns = botanswers.objects.filter(category_id = catgry.id)
    
    bestMatch = 0
    
    for m in filtAns:
        Match = 0
        ansLen = len(m.entities)
        for ent in entitiesList:
            if ent.lower() in m.entities.lower():
                Match += 1
        Accuracy = (Match/ansLen)
        if (Accuracy > count or Match > bestMatch) and not Match < bestMatch:
            count = Accuracy
            answr = m.answer
            if Match > bestMatch:
                bestMatch = Match
            
    if answr == "" and chatWindow == True:
        answr = "Sorry, I didn't understand that."
    
    return (answr) 