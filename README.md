# Amesite Chat Responder

#### Table of Contents 

1. [Description](#description) 
2. [Built With](#builtWith)
3. [Required Installations](#requiredInst)
4. [Setup](#setup) 
5. [Deployment](#deployment)

## Description 
The purpose of Amesite Chat Responder (ACR) is to have students become more involved in the educational system. This application will provide a chatbot feature for all users to interact with. Users can ask the chatbot logistical and procedural questions, allowing them to have more time to accomplish other tasks. ACR provides users the ability to ask and answer questions based on the courses they have access to. Users can post a question within the course page for other users to answer at any given time. 

## Built With
1. Python 3.6 Programing Language 
1. Django 2.0 Framework 
1. JavaScript
1. HTML/CSS
1. Bootstrap
1. LUIS API

## Required Installations 
Run the following commands in cmd terminal:
1. Install python 3.6 from https://www.python.org/downloads/
2. pip install django==2.0
3. pip install -U nltk 
4. pip install pdfminer3k 
5. pip install python-docx
6. pip install celery==3.1.24
7. pip install billiard 
8. pip install requests
9. pip install psycopg2 
10. pip install botocore
11. pip install redis
12. pip install python-pptx
13. pip install django-cleanup
14. pip install -U spacy 
15. pip install pywin32
16. in cmd type python
	import nltk	
	nltk.download()
	Once the download window appears. 
	Download: (under CORPA) stopwords, words, (under MODEL) moses_sample, perluniprops, and punkt. 
	Once the download window appears click DOWNLOAD button.
17. python -m spacy download en
18. download redis from https://redis.io/download


## Setup 
1. Make sure you have installed all of the required installations. 
2. Create a folder where you will store this project. 
3. Edit the django settings file according to comments in the file. 
4. Change the LUIS endpoints in botFunctions file and catQuestion as needed.
5. You should create and train the following intents within your LUIS API: Assignment, Greetings, Lecture, Syllabus, and Other 

## Deployment
1. Open cmd prompt and navigate to where you stored the django project folder. 
2. Type the following command: python manage.py makemigrations 
3. Type the following command: python manage.py migrate 
4. In the database edit the category table with the following data: Greetings, Syllabus,  Assignment, Lecture, and Other.
5. Type the following command to run the django project: python manage.py runserver.
6. Open Browser window and type the following in the URL space: 127.0.0.1:8000.
7. You should now see the Amesite Chat Responder Login page. 
8. For asynchronous tasks run the exe redis file, open 2 separate cmd windows.
    In the first cmd window type the following command: celery -A CourseGuru worker -l info.
    In the other cmd window type the following command: celery -A CourseGuru beat -l Debug,

   


