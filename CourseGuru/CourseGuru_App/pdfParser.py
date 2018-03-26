import nltk
import re

from pdfminer.pdfparser import PDFParser, PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.layout import LAParams, LTTextBoxHorizontal
from pdfminer.converter import PDFPageAggregator#,HTMLConverter
#from pdfminer.pdfpage import PDFPage
#from io import BytesIO
#from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
#from nltk.stem import WordNetLemmatizer
from nltk.tokenize.moses import MosesDetokenizer
from CourseGuru_App.models import keywords
#from CourseGuru_App.models import courseinfo
from CourseGuru_App.models import botanswers

from pdfminer.converter import TextConverter
from io import StringIO


#testing PRP
#def pdfToText(file):
def pdfToText(file, cid, catID, fileid, docType):
    
    if docType == 'Syllabus':
        #Create empty string for text to be extracted into
        keyWordObj = keywords.objects.exclude(categoryKeyWords=None)
        
        keyWords = []
        for n in keyWordObj:
            keyWords.append(n.categoryKeyWords)
        extracted_text = '' 
    
        #Sets the cursor back to 0 in f to be parsed and sets the documents and parser
        file.seek(0)
        parser = PDFParser(file)
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
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        
        ansArray = []     
         
    #testing PRP
    #    botSearchArray = []
           
        for page in doc.get_pages():
            print('New Page')
            interpreter.process_page(page)
            layout = device.get_result()
            for lt_obj in layout:
                #if isinstance(lt_obj, LTTextBox) or isinstance(lt_obj, LTTextLine):
                if isinstance(lt_obj, LTTextBoxHorizontal):
                    extracted_text = lt_obj.get_text()
                    #change \n to <br>
                    filtText = re.sub('\\n', '<br>', extracted_text)
                    #getting rid of unicode characters 
                    filtText = re.sub('\\uf0b7|\\uf020', '', filtText)
                    #getting rid on any extra spaces
                    filtText = re.sub(' +', ' ', filtText)
                    added = False
                    
                    for n in keyWords:
                        if (n.lower() in filtText.lower()) and (added == False) and (len(n) > 2 ):
                            ansArray.append(filtText)
                            keyWords.remove(n)
                            added=True
                        elif (len(n) < 3) and (re.match(('[a-zA-Z]*' + re.escape(n) +'[a-zA-Z]*'), filtText) != None):
                            if (n in filtText) and (added == False):
                                ansArray.append(filtText)
                                keyWords.remove(n)
                                added=True
    
                        elif(n.lower() in filtText.lower()) and (added == True):
                            keyWords.remove(n)
                            
                    if (len(ansArray) > 0) and (added == False):
                        #checking for empty lines or lines with just a page number
                        if (filtText != ' <br>') and (re.match('[0-9]* <br>', filtText) == None):
                            ansArray[-1] = ansArray[-1] + ' ' + filtText
                        
                    elif len(ansArray)==0: 
                        ansArray.append('Course Information: ' + filtText)
        
        for n in ansArray: 
            restructForDB(n, cid, catID, fileid)
    #        botSearchArray.append(restructForDB(n))         
                   
        file.close() 
        #return textFile
    
    
    elif docType == 'Assignment':
        #Sets the cursor back to 0 in f to be parsed and sets the documents and parser
        file.seek(0)
        parser = PDFParser(file)
        doc = PDFDocument()
        parser.set_document(doc)
        doc.set_parser(parser)
        doc.initialize('')
        rsrcmgr = PDFResourceManager()
        #sets parameters for analysis 
        laparams = LAParams()
        retstr = StringIO()
              
        device = TextConverter(rsrcmgr, retstr, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)

        #num = False
        data = ""
        for page in doc.get_pages():
            read_position = retstr.tell()
            interpreter.process_page(page)
            retstr.seek(read_position, 0)
            page_text = retstr.read()
            page_text = re.sub('\\n', ' <br> ', page_text)
            page_text = re.sub('\\uf0b7|\\uf020|\\ufb01|\\uf8ff', '?', page_text)
            #print('CHECK: ' + page_text)
            
            for word in page_text.split():
                skip = False
                if len(word) < 4:
                    for ind, c in enumerate(word):
                        if c.isdigit() and ind < len(word)-1:
                            if word[ind+1] == '.':
                                #print(data)
                                parsedToDB(data, cid, catID, fileid)     
                                data = 'Question ' + word
                                #num = True
                                skip = True
                                break
                if skip == False:
                    if data == "":
                        data = word
                    else:
                        data = data + ' ' + word

        if data != "":
            #print(data)
            parsedToDB(data, cid, catID, fileid)        
                   
        file.close() 
        
from CourseGuru_App.models import document

def parsedToDB(data, cid, catID, fileid): 
    file = document.objects.get(id = fileid)
    fileName = file.file_name
    fileName = fileName.split(".")[0]   
    
    detokenizer = MosesDetokenizer()
    regex = re.compile('[^a-zA-Z0-9 \n\.]')
    data = data.replace('\x00', ' ')
    dbAnswer = data
    data = fileName + ' ' + data
    data = data.replace('<br>',' ')
    data = regex.sub('', data)
    data_list = nltk.word_tokenize(data)
    data = [word for word in data_list if word not in stopwords.words('english')]
    detokenizer.detokenize(data, return_str=True)
    dbInfo = " ".join(data)    
    botanswers.objects.create(answer = dbAnswer, rating = 0, category_id = catID.id, entities = dbInfo, course_id = cid, file_id = fileid)
 

def restructForDB (text, cid, catID, fileid): 
    detokenizer = MosesDetokenizer() 
    dbAnswer = text 
    botSearch = text.replace('<br>', '')
    rgx = re.compile('[^a-zA-Z0-9 \n\.]')
    
    botSearch = rgx.sub('', botSearch)
    searchList = nltk.word_tokenize(botSearch, 'english')
    
    botSearch = [word for word in searchList if word not in stopwords.words('english')]
    
    detokenizer.detokenize(botSearch, return_str=True)
    botSearch = ' '.join(botSearch)
    botSearch = botSearch.lower()
    
    botanswers.objects.create(answer = dbAnswer, rating = 0, category_id = catID.id, entities = botSearch, course_id = cid, file_id = fileid)

