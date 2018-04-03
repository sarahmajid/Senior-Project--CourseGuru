from django.core.mail import send_mail

from CourseGuru import settings


def sendEmailExistingUser(courseName, email):
    send_mail(subject='You Have Been Added To ' + courseName, 
              message='Hello there, you have been added to ' + courseName + ' \nPlease click the link to be directed to the login page.' + ' \nLINK: http://127.0.0.1:8000', 
              from_email=settings.EMAIL_HOST_USER, 
              recipient_list=[email], 
              fail_silently =False)
     
def sendEmailNonExistingUser(courseName, email, username, password):
    send_mail('You Have Been Added To ' + courseName, 
              'Hello there, you have been added to ' + courseName
               + '.\nHowever our records indicate that you do not currently have an account. Please login with the provided credentials.\nWhen you log in edit click on the "Hi ' 
               + username + '!" message and select "Edit Account" to change your account information. \nUSERNAME: ' + username + '\n'+
               'PASSWORD: '+ password + '\nLINK: http://127.0.0.1:8000', 
              from_email=settings.EMAIL_HOST_USER, 
              recipient_list=[email], 
              fail_silently =False)
    