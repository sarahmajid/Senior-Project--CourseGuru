
import json
import urllib
from urllib.request import urlopen
from json2html import *
from urllib.request import *
import requests
import browser_cookie3


#response = requests.get("https://canvas.wayne.edu/api/v1/courses",verify=True,)
#print(response.text)

url = 'https://canvas.wayne.edu/api/v1/courses'
# urll = 'https://academica.aws.wayne.edu/cas/login?service=https%3A%2F%2Fcanvas.wayne.edu%2Flogin%2Fcas'


cookies = browser_cookie3.chrome()
s = requests.get(url, cookies = cookies)
print(s.content)
