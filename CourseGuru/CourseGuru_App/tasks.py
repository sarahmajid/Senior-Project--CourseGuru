import time
from CourseGuru.celery import app
from celery import task
from CourseGuru_App.luisRun import publishLUIS
 
 
@task
def queuePublish():
    time.sleep(20)
    publishLUIS()
    