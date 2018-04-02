from __future__ import absolute_import, unicode_literals

from CourseGuru.celery import app
from celery import task
from CourseGuru_App.luisRun import publishLUIS, trainLUIS
import time

 
@task
def queuePublish():
    trainLUIS()
    print('Waiting 10 minutes for LUIS training to complete.')
    time.sleep(600)
    publishLUIS()
    #print('Published!')