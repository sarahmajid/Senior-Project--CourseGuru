import csv
import io

from django.http import HttpResponse
from django.contrib.auth.models import User

from CourseGuru_App.models import courseusers
from CourseGuru_App.sendEmail import sendEmailExistingUser
from CourseGuru_App.createUsersFunctions import createTempUser
from CourseGuru_App.validate import emailValidator

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

def restructString(strMessage, userList):
    if (len(userList)==1):
        strMessage += userList[0]+ "."
    elif (len(userList)==2):  
        strMessage += userList[0]+ " and " + userList[1]
    else:
        for n in userList:
            if n != userList[len(userList)-1]:
                strMessage += n + ", "
            else:
                if (len(userList)==1):
                    strMessage += n + "."
                else:
                    strMessage += "and " + n +"."
    return strMessage

def readCSV(csvFile, courseId, courseName):
    
    #variable initialization 
    strNotAdded = "We were not able to add the following user(s) because the status of the email provided did not match the status of the user: "
    strCreatedUser = "We have created accounts and sent login credentials, via email, for the following user(s) requesting that they edit their account information as soon as possible. "
    strExistingUser = "We have added the following users to the course: "
    csvHeaderError = 'CSV header error! Please make sure CSV file contain "Email" and "Status" as the header for all of the rows'
    csvCountError = 'CSV file must not contain more than 1,000 rows of data.' 
    notAddedUsers = []
    createdUsers = []
    createdUsersStat = []
    addedUsers = []
    
    csvF = csvFile.read().decode()
    #sniffing for the delimiter in csv
    sniffer = csv.Sniffer().sniff(csvF)         
    #reading csv using DictReader     
    reader = csv.DictReader(((io.StringIO(csvF))), delimiter=sniffer.delimiter)   
        
    #check if file contains more then 1,000 rows
    count = len(list(reader))  
    if count>1000:
        return (csvCountError)
    else:
        csvFile.seek(0) 
        csvF = csvFile.read().decode()
        #sniffing for the delimiter in csv
        sniffer = csv.Sniffer().sniff(csvF)         
        #reading csv using DictReader     
        reader = csv.DictReader(((io.StringIO(csvF))), delimiter=sniffer.delimiter)
        
    #converts all field names to lowercase
    reader.fieldnames = [header.strip().lower() for header in reader.fieldnames]

    #    Adds students according to the csv content. If DictReader is changed code below must be edited.            
    for n in reader:
        try:
            if(User.objects.filter(email = n['email'], status = n['status']) and emailValidator(n['email']) == True):
                addUser = User.objects.get(email = n['email'])
                #if addUser.email == n['email'] and addUser.status == n['status']:
                if (courseusers.objects.filter(user_id = addUser.id, course_id = courseId).exists()==False):
                    courseusers.objects.create(user_id = addUser.id, course_id = courseId)    
                    addedUsers.append(n['email'])
            elif (User.objects.filter(email = n['email']) and emailValidator(n['email']) == True):
            #elif addUser.email == n['email'] and addUser.status != n['status'] and n['status'] != '':
                addUser = User.objects.get(email = n['email'])
                if addUser.email == n['email'] and addUser.status != n['status'] and n['status'] != '':
                    if n['email'] not in notAddedUsers: 
                        notAddedUsers.append(n['email'])
            else:
                if emailValidator(n['email']) == True: 
                    if n['email'] not in createdUsers: 
                        createdUsers.append(n['email'])
                        createdUsersStat.append(n['status']) 
        except KeyError: 
            return (csvHeaderError)
    
    #sending out emails to the added users  
    for n in addedUsers: 
        userInfo = User.objects.get(email = n)
        sendEmailExistingUser(courseName, userInfo)
    for i, n in enumerate(createdUsers): 
        createTempUser(n, courseId, courseName, createdUsersStat[i])
    
    #creates a list of none existing users.         
    if len(notAddedUsers)>0:
        strNotAdded = restructString(strNotAdded, notAddedUsers)
    else:
        strNotAdded = ''

    if len(createdUsers)>0:
        strCreatedUser = restructString(strCreatedUser, createdUsers)
    else: 
        strCreatedUser = '' 
    
    if len(addedUsers)>0:    
        strExistingUser = restructString(strExistingUser, addedUsers)
    else: 
        strExistingUser = ''   
         
   
    
    return (strNotAdded, strCreatedUser, strExistingUser)