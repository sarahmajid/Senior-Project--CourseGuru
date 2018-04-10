import csv
import io

from django.http import HttpResponse
from django.contrib.auth.models import User

from CourseGuru_App.models import courseusers
from CourseGuru_App.sendEmail import sendEmailExistingUser
from CourseGuru_App.createUsersFunctions import createTempUser

def downloadCSV():
    file = HttpResponse(content_type='text/csv')
    file['Content-Disposition'] = 'attachment; filename=CSVTemplate.csv'
    writer = csv.writer(file)
    writer.writerow(["Email", "Status"])
    writer.writerow(["User1 Email", "TA"])
    writer.writerow(["User2 Email", "Student"])
    writer.writerow(["User3 Email", "Student"])
    writer.writerow(["...", "..."])
    return file
    
def readCSV(csvFile, courseId, courseName):
    csvF = csvFile.read().decode()
    #sniffing for the delimiter in csv
    sniffer = csv.Sniffer().sniff(csvF)         
    #reading csv using DictReader     
    reader = csv.DictReader(((io.StringIO(csvF))), delimiter=sniffer.delimiter)   
    #converts all field names to lowercase
    reader.fieldnames = [header.strip().lower() for header in reader.fieldnames]
           
    #variable initialization 
    str1 = "The following "
    str2 = " users will need to edit their account information: "
    str3 = " We have created accounts for them and sent them their login credentials, requesting they edit their account information."
    strNotAdded = ""
    notAddedUsers = []
    notAddedUsersStat = []
    addedUsers = []
    numUserNotAdded=0
    
    #Adds students according to the csv content. If DictReader is changed code below must be edited.            
    for n in reader:
        try:
            if(User.objects.filter(email = n['email'])):
                addUser = User.objects.get(email = n['email'])
                if (courseusers.objects.filter(user_id = addUser.id, course_id = courseId).exists()==False):
                    courseusers.objects.create(user_id = addUser.id, course_id = courseId)
                    addedUsers.append(n['email'])
            else: 
                if n['email'] not in notAddedUsers: 
                    notAddedUsers.append(n['email'])
                    notAddedUsersStat.append(n['status']) 
                    numUserNotAdded+=1   
                    strNotAdded = str1 + str(numUserNotAdded) + str2
        except KeyError: 
            return 'CSV header error! Please make sure CSV file contain "Email" as the header for all of the emails.'
    
    #sending out emails to the added users  
    for n in addedUsers: 
        userInfo = User.objects.get(email = n)
        sendEmailExistingUser(courseName, userInfo)
    for i, n in enumerate(notAddedUsers): 
        createTempUser(n, courseId, courseName, notAddedUsersStat[i])
    
    #creates a list of none existing users.         
    if(len(notAddedUsers)>0):
        for n in notAddedUsers:
            if n != notAddedUsers[len(notAddedUsers)-1]:
                strNotAdded += n + ", "
            else:
                if (len(notAddedUsers)==1):
                    strNotAdded += n + "." + str3
                    return strNotAdded
                else:
                    strNotAdded += "and " + n +"." + str3
                    return strNotAdded
    else: 
        strNotAdded = "All Users Added Successfully!"        
        return strNotAdded