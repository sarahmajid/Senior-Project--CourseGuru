import csv
import io

from django.http import HttpResponse
from django.contrib.auth.models import User
from django.core.mail import send_mail

from CourseGuru_App.models import courseusers
from CourseGuru import settings

def downloadCSV():
    file = HttpResponse(content_type='text/csv')
    file['Content-Disposition'] = 'attachment; filename=CSVTemplate.csv'
    writer = csv.writer(file)
    writer.writerow(["Email"])
    writer.writerow(["User1 Email"])
    writer.writerow(["User2 Email"])
    writer.writerow(["User3 Email"])
    writer.writerow(["..."])
    return file
def sendEmailExistingUser(courseName, email):
    send_mail(subject='You Have Been Added To ' + courseName, 
              message='Hello there, you have been added to ' + courseName + 'please click the link to be directed to the login page.', 
              from_email=settings.EMAIL_HOST_USER, 
              recipient_list=email, 
              fail_silently =False)
    
def sendEmailNonExistingUser(courseName, email):
    send_mail('You Have Been Added To ' + courseName, 
              'Hello there, you have been added to ' + courseName + '.\nHowever our records indicate that you do not currently have an account. Please click the following link to be directed to a page where you can create an account.', 
              from_email=settings.EMAIL_HOST_USER, 
              recipient_list=email, 
              fail_silently =False)
    
def readCSV(csvFile, cid):
    csvF = csvFile.read().decode()
    #sniffing for the delimiter in csv
    sniffer = csv.Sniffer().sniff(csvF)         
    #reading csv using DictReader     
    reader = csv.DictReader(((io.StringIO(csvF))), delimiter=sniffer.delimiter)   
    #converts all field names to lowercase
    reader.fieldnames = [header.strip().lower() for header in reader.fieldnames]
           
    #variable initialization 
    str1 = "The following "
    str2 = " users will need to create an account: "
    strNotAdded = ""
    notAddedUsers = []
    numUserNotAdded=0
    
    #Adds students according to the csv content. If DictReader is changed code below must be edited.            
    for n in reader:
        try:
            if(User.objects.filter(email = n['email'])):
                addUser = User.objects.get(email = n['email'])
                if (courseusers.objects.filter(user_id = addUser.id, course_id = cid).exists()==False):
                    courseusers.objects.create(user_id = addUser.id, course_id = cid)
            else: 
                notAddedUsers.append(n['email']) 
                numUserNotAdded+=1   
                strNotAdded = str1 + str(numUserNotAdded) + str2
        except KeyError: 
            return 'CSV header error! Please make sure CSV file contain "Email" as the header for all of the emails.'
    #creates a list of none existing users.         
    if(len(notAddedUsers)>0):
        for n in notAddedUsers:
            if n != notAddedUsers[len(notAddedUsers)-1]:
                strNotAdded += n + ", "
            else:
                if (len(notAddedUsers)==1):
                    strNotAdded += n + "."
                    return strNotAdded
                else:
                    strNotAdded += "and " + n +"."
                    return strNotAdded
    else: 
        strNotAdded = "All Users Added Successfully!"        
        return strNotAdded