import nltk
from nltk.tokenize import word_tokenize

#query = "How much is assignment #5 worth of my grade?"
query = "What is the name of the required textbook?"

def reformQuery(query):

    #Splits words out into list
    wordSplit = nltk.word_tokenize(query)
    #Adds word type to each item in list
    typeSplit = nltk.pos_tag(wordSplit)

    for (i, elem) in enumerate(typeSplit):
        if elem[1] == ('PRP$'):
            typeSplit[i] = ('your','PRP$')
        elif elem[1] == ('PRP'):
            typeSplit[i] = ('you','PRP')

    for (i, elem) in enumerate(typeSplit):
        if elem[1] == ('MD') and typeSplit[i+1][1] == ('PRP'):
            typeSplit[i+1], typeSplit[i] = typeSplit[i], typeSplit[i+1]
            

    quesmark = [ind for ind, elem in enumerate(typeSplit) if elem[1] == '.']

    print(typeSplit)

    #Removes question marks from the query
    while(quesmark):
        typeSplit.remove(typeSplit[quesmark[0]])
        quesmark = [ind for ind, elem in enumerate(typeSplit) if elem[1] == '.']              
 
    wordFound = [ind for ind, elem in enumerate(typeSplit) if elem[1] == 'WP' or elem[1] == 'WRB']
    if wordFound:
        typeSplit.remove(typeSplit[wordFound[0]])
        wordFound = [ind for ind, elem in enumerate(typeSplit) if elem[1] == 'VBZ' or elem[1] == 'VBD']
        if wordFound:
            typeSplit = typeSplit[1:]
            #typeSplit.insert(len(typeSplit), ('is', 'VBZ'))
        else:
            wordFound = [ind for ind, elem in enumerate(typeSplit) if elem[1] == 'VBP']
            if wordFound:
                typeSplit.insert(len(typeSplit), typeSplit[wordFound[0]])
                typeSplit = typeSplit[1:]
    else:
        wordFound = [ind for ind, elem in enumerate(typeSplit) if elem[1] == 'VBZ']
        if wordFound:
            typeSplit[1], typeSplit[0] = typeSplit[0], typeSplit[1]

    if typeSplit[0] == ('is', 'VBZ'):
        typeSplit = typeSplit[1:]

    return ' '.join([elem[0] for elem in typeSplit]).capitalize() + ': '

answer = reformQuery(query)
print(answer)

