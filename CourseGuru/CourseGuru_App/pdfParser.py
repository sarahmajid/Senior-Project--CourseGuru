'''
Created on Mar 8, 2018

@author: Andriy Marynovskyy
'''
import tempfile
import nltk

from pdfminer.pdfparser import PDFParser, PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter, process_pdf
from pdfminer.layout import LAParams, LTTextBoxHorizontal
from pdfminer.converter import PDFPageAggregator, HTMLConverter
from pdfminer.pslexer import delimiter
#from pdfminer.pdfpage import PDFPage

from io import BytesIO

from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize.moses import MosesDetokenizer

from CourseGuru_App.models import keywords
from CourseGuru_App.models import courseinfo
from CourseGuru_App.models import botanswers

def pdfToText(request):
#    Create empty string for text to be extracted into
    extracted_text = '' 
    test = ''
    #When button is clicked we parse the file
    if request.method == "POST":
        #Sets myfile to the selected file on page and reads it
        myfile = request.FILES.get("syllabusFile").file.read()
              
        #Create temporary file in read and write binary mode
        f = tempfile.TemporaryFile('r+b')
        f.write(myfile)
  
        #Sets the cursor back to 0 in f to be parsed and sets the documents and parser
        f.seek(0)
        parser = PDFParser(f)
        doc = PDFDocument()
        parser.set_document(doc)
        doc.set_parser(parser)
        doc.initialize('')
        rsrcmgr = PDFResourceManager()
        #sets parameters for analysis 
        laparams = LAParams()
              
        #Required to define separation of text within pdf
        laparams.char_margin = 1
        laparams.word_margin = 1
              
        #Device takes LAPrams and uses them to parse individual pdf objects
        device = PDFPageAggregator(rsrcmgr, laparams=laparams)
        #device = HTMLConverter(rsrcmgr, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)
              
        for page in doc.get_pages():
            interpreter.process_page(page)
            layout = device.get_result()
            for lt_obj in layout:
                if isinstance(lt_obj, LTTextBoxHorizontal):
                    extracted_text += lt_obj.get_text() 
        textFile = pullInfo(extracted_text)   
        f.close() 
    return textFile


#will need a more robust way
def pullInfo(file):
     
## = for Testing Purposes 
    keyWordObj = keywords.objects.exclude(categoryKeyWords=None)
    subKeyWords = keywords.objects.exclude(subCategoryKeyWords=None)
    keyWords = []
    #parallel arrays to store the keywords found and their positions 
    keyPositions = []
    keyWordPositions = []

    subCat = []
     
    subCatkeyPosition = [] 
    subCatWordPosition = []
    header=[]
    data=[]
 
    space = nltk.tokenize.SpaceTokenizer()
    pdfWord = space.tokenize(file)
    pdfWords = []
     
    #strips the '\n' character from the list of elements 
    for n in pdfWord: 
        pdfWords.append(n.strip())
     
    for n in keyWordObj:
        keyWords.append(n.categoryKeyWords)
    for n in subKeyWords:
        subCat.append(n.subCategoryKeyWords)
         
                
    #join two word elements into one such as [Teaching, assistant] into [Teaching assistant] in main Category
    i=0
    while i<len(pdfWords)-1:
        for n in keyWords:
            temp = pdfWords[i] + " " + pdfWords[i+1]
            #if re.match((n + r"^\:|\;$"), temp, re.IGNORECASE):
            if ((n+':')==temp):
                pdfWords[i] = pdfWords[i]+ " " + pdfWords[i+1]
                del pdfWords[i+1]
        i+=1           
         
    #join two word elements into one such as [Office, Hours] into [Office Hours] sub categories
    i=0
    while i<len(pdfWords)-1:
        for n in subCat:
            temp = pdfWords[i] + " " + pdfWords[i+1]
            #if re.match((n + r"^\:|\;$"), temp, re.IGNORECASE):
            if ((n+':')==temp):
                pdfWords[i] = pdfWords[i]+ " " + pdfWords[i+1]
                del pdfWords[i+1]
        i+=1   
        
    # finding all the key word positions 
    i=0    
    while i<len(pdfWords)-1:
        for n in keyWords:
            if pdfWords[i].__contains__(n):  
                keyPositions.append(i)
                keyWordPositions.append(n)   
        i+=1 
                 
    # sub category location finder     
    i=0    
    while i<len(pdfWords)-1:
        for m in subCat: 
            if pdfWords[i].__contains__(m):
                subCatkeyPosition.append(i)
                subCatWordPosition.append(m)  
        i+=1 
        
    numKeyWordsFound=len(set(subCatWordPosition))
    
    #structuring text and storing it into the database table as ex: Instructors Name | John Doe    
    i=0
    while i<len(keyPositions)-1:
        j=0
        if keyPositions[i] < subCatkeyPosition[-1]:
            while j<=len(subCatkeyPosition)-1:
                if (keyPositions[i] < subCatkeyPosition[j] and subCatkeyPosition[j] < keyPositions[i+1] and j==(numKeyWordsFound-1)):
                    header.append(keyWordPositions[i]+' '+subCatWordPosition[j]) 
                    data.append(pdfWords[subCatkeyPosition[j]:keyPositions[i+1]-1])
#                     keywords.objects.create(intent = (keyWordPositions[i]+' '+subCatWordPosition[j]), data = (pdfWords[(subCatkeyPosition[j]+1):keyPositions[i+1]-1]))
                    j+=1
                    numKeyWordsFound+=numKeyWordsFound
                        
                elif (keyPositions[i] < subCatkeyPosition[j] and subCatkeyPosition[j] <= keyPositions[i+1]):
                    header.append(keyWordPositions[i]+' '+subCatWordPosition[j]) 
                    ##crash here if only one sub cat name found
                    data.append(pdfWords[subCatkeyPosition[j]:subCatkeyPosition[j+1]])
#                    keywords.objects.create(intent = (keyWordPositions[i]+' '+subCatWordPosition[j]), data = (pdfWords[(subCatkeyPosition[j]+1):subCatkeyPosition[j+1]]))
                    j+=1
                     
                else: 
                    j+=1
            i+=1
        else: 
            header.append(pdfWords[keyPositions[i]])
            data.append(pdfWords[(keyPositions[i]+1):keyPositions[i+1]])
#            keywords.objects.create(intent = (keyWordPositions[i]), data = (pdfWords[(keyPositions[i]+1):keyPositions[i+1]]))
            i+=1
        
    #For Testing 
    for n in header: 
        print(n) 
    for n in data: 
        print(n)   
 
#Will need once finished setting all key words        
    #to end of file    
    keyPositions.append(len(pdfWords))
    # loops through the key positions and puts data into appropriate rows according to intent name 
#===============================================================================
#     i=0
#     while i <len(keyPositions)-1:      
#         intent = keyWordObj.get(intent = keyWordPositions[i])
#         intent.infoData=(pdfWords[(keyPositions[i]+1):keyPositions[i+1]])
#         b = pdfWords[keyPositions[i]]
#         a=(pdfWords[(keyPositions[i]+1):keyPositions[i+1]])
# #        print(intent.infoData)
#         intent.save()
#         i+=1
#===============================================================================
    return(pdfWords)


def pdfToHTML(pdfFile):
         
    f = tempfile.TemporaryFile('r+b')
    f.write(pdfFile)
     
    resourceManager = PDFResourceManager()
    retstr = BytesIO()
    laparams = LAParams()
       
    device = HTMLConverter(resourceManager, codec='utf-8', laparams=laparams)
    
    file = open(f, 'rb')
    interp = PDFPageInterpreter(resourceManager, device)
    maxpages = 0
    caching = True
    pagenos=set()
     
    htmlFile = process_pdf(resourceManager, device, file, pagenos=None, maxpages=0)
     
    file.close()
    device.close()
    #return text
    return htmlFile
         
#    return render(request, 'CourseGuru_App/parse.html')
