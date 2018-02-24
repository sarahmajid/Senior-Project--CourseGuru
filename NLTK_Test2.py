import nltk
from nltk.tokenize import word_tokenize

query = "How much is this assignment worth?"

def reformQuery(query):

    #Splits words out into list
    wordSplit = nltk.word_tokenize(query)
    #Adds word type to each item in list
    typeSplit = nltk.pos_tag(wordSplit)

    quesmark = [ind for ind, elem in enumerate(typeSplit) if elem[1] == '.']

    while(quesmark):
        typeSplit.remove(typeSplit[quesmark[0]])
        quesmark = [ind for ind, elem in enumerate(typeSplit) if elem[1] == '.']              

    print(typeSplit)
    
    wordFound = [ind for ind, elem in enumerate(typeSplit) if elem[1] == 'WP' or elem[1] == 'WRB']
    if wordFound:
        typeSplit.remove(typeSplit[wordFound[0]])
        wordFound = [ind for ind, elem in enumerate(typeSplit) if elem[1] == 'VBZ' or elem[1] == 'VBP' ]
        if wordFound:
            typeSplit = typeSplit[1:] + [typeSplit[0]]
    else:
        wordFound = [ind for ind, elem in enumerate(typeSplit) if elem[1] == 'VBZ']
        if wordFound:
            typeSplit[1], typeSplit[0] = typeSplit[0], typeSplit[1]

    return ' '.join([elem[0] for elem in typeSplit]).capitalize()

answer = reformQuery(query)
print(answer)

