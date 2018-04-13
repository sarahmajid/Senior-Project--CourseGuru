from django.core.mail import send_mail

from CourseGuru import settings

    
def sendEmailExistingUser(courseName, userInfo):
    send_mail(subject='You Have Been Added To ' + courseName, 
              message='Hello ' + userInfo.first_name +  ',\n\nYou now have access to ' + courseName + ' within the AmesiteChatResponder application.' + 
              '\nThe link provided below will redirect you to the login page.' +
               '\n\nLINK: http://127.0.0.1:8000', 
              from_email=settings.EMAIL_HOST_USER, 
              recipient_list=[userInfo.email], 
              fail_silently =False)
     
def sendEmailNonExistingUser(courseName, email, username, password):
    send_mail('You Have Been Added To ' + courseName, 
              'Hello, \n\nYou now have access to ' + courseName
               + ' within the AmesiteChatResponder application.\nHowever, our records indicate that this email is not associated with any existing account.' +
               'So we created an account for you. Please login with the username and password provided below.'+
               '\n\nOnce logged in, please edit your account information. You can do so by simply clicking on the greeting message "Hi ' 
               + username + '!" then click on the "Edit Account" option from the drop-down menu. You will then be redirected to a page where you can edit your account information.' + 
               '\n\nUSERNAME: ' + username + '\nPASSWORD: ' + password + '\nLINK: http://127.0.0.1:8000', 
              from_email=settings.EMAIL_HOST_USER, 
              recipient_list=[email], 
              fail_silently =False)
    