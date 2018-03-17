import csv
import io
from django.http import HttpResponse
from django.contrib.auth.models import User
from CourseGuru_App.models import courseusers

def downloadCSV():
    file = HttpResponse(content_type='text/csv')
    file['Content-Disposition'] = 'attachment; filename=CSVTemplate.csv'
    writer = csv.writer(file)
    writer.writerow(["Username"])
    writer.writerow(["UserName1"])
    writer.writerow(["UserName2"])
    writer.writerow(["UserName3"])
    writer.writerow(["..."])
    return file

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
    str2 = " users were not added to the course because the usernames do not exist: "
    strNotAdded = ""
    notAddedUsers = []
    numUserNotAdded=0
    
    #Adds students according to the csv content. If DictReader is changed code below must be edited.            
    for n in reader:
        try:
            if(User.objects.filter(username = n['username'])):
                addUser = User.objects.get(username = n['username'])
                if (courseusers.objects.filter(user_id = addUser.id, course_id = cid).exists()==False):
                    courseusers.objects.create(user_id = addUser.id, course_id = cid)
            else: 
                notAddedUsers.append(n['username']) 
                numUserNotAdded+=1   
                strNotAdded = str1 + str(numUserNotAdded) + str2
        except KeyError: 
            return 'CSV header error! Please make sure CSV file contain "Username" as the header for all of the usernames.'
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