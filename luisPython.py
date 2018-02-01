import requests
import json

#Script to retrieve Luis Intent based on string passed

query = 'How are you doing?'

try:
	r = requests.get('https://westus.api.cognitive.microsoft.com/luis/v2.0/apps/ee579764-9ebf-44fd-a904-e3353a691b7e?subscription-key=a0d35b39c3874ec1b05ff5bececfa7eb&verbose=true&timezoneOffset=0&q=%s' % query)
	#print(r.json())
	jsonTxt = json.loads(r.text)
	print(jsonTxt['topScoringIntent']['intent'])
		#for x in jsonTxt:
			#print("%s: %s" % (x, jsonTxt[x]))

except Exception as e:
    print("Error")
