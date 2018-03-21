from __future__ import absolute_import, unicode_literals

from CourseGuru.celery import app
from celery import task
from CourseGuru_App.luisRun import publishLUIS

 
@task
def queuePublish():
    publishLUIS()
    #print('Published!')