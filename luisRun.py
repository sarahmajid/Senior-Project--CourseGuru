import luisAuthor
import json

query = "test this query with luis authoring"

data = {}
data = [{"text": query,
         "intentName": "Name",
         "entityLabels": [] }]

with open('./utterances.json','w') as outfile:
    json.dump(data,outfile)

luisAuthor.addUtterance()
