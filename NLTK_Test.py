import nltk

from nltk.tokenize import word_tokenize

#text = word_tokenize("What are you doing?")

#print(text)

text = "Is that a dog or a cat in the cage?"

def noun(pos):
    return(pos[:2] == 'NN')

def verb(pos):
    return(pos[:2] == 'VB')

def determiner(pos):
    return(pos[:2] == 'DT')

splitText = nltk.word_tokenize(text)

nouns = [word for (word, pos) in nltk.pos_tag(splitText) if noun(pos)]
verbs = [word for (word, pos) in nltk.pos_tag(splitText) if verb(pos)]
determiners = [word for (word, pos) in nltk.pos_tag(splitText) if determiner(pos)] 

print ('Nouns:', nouns)
print ('Verbs:', verbs)
print ('Determiners:', determiners)

# print(nltk.pos_tag("hello"))
