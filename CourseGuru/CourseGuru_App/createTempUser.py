from django.contrib.auth.models import User

from CourseGuru_App.models import courseusers
from CourseGuru_App.sendEmail import sendEmailNonExistingUser


def autoCredential():
    genCredential = User.objects.make_random_password(8)
    print(genCredential)
    return genCredential  

def createUser(userEmail, courseId, courseName):
    notRegistered = 'No-Credential'
    userName = autoCredential()
    while userName == User.objects.filter(username = userName).exists():
        userName = autoCredential()
    password = autoCredential()
    addUser = User.objects.create_user(userName, userEmail, password) 
    addUser.first_name = notRegistered
    addUser.last_name = notRegistered
    addUser.status = notRegistered
    addUser.save()
    addUser = User.objects.get(email = userEmail)
    courseusers.objects.create(user_id = addUser.id, course_id = courseId)
    sendEmailNonExistingUser(courseName, userEmail, userName, password)

