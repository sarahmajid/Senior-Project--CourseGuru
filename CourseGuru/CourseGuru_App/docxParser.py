import re, string
import nltk

from CourseGuru_App.models import botanswers

from nltk.corpus import stopwords
from nltk.tokenize.moses import MosesDetokenizer

from docx import Document
from docx.document import Document as _Document 
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.table import _Cell, Table
from docx.text.paragraph import Paragraph

#Function checks if blocks are paragraphs or tables
def iterBlockItems(parent):
    
    if isinstance(parent, _Document):
        parent_element = parent.element.body
    elif isinstance(parent, _Cell):
        parent_element = parent._tc
    else:
        raise ValueError("Could not find either.")
    
    for c in parent_element.iterchildren(): 
        if isinstance(c, CT_P):
            a = Paragraph(c, parent)
            yield a
        elif isinstance(c, CT_Tbl):
            b = Table(c, parent)
            yield b
          
def parsedToDB(data, header, cid, catID, fileid):
    detokenizer = MosesDetokenizer()
    regex = re.compile('[^a-zA-Z0-9 \n\.]')
    
    dbAnswer = header + data
    data = data.replace('<br>',' ')
    header = header.replace("-",'')
    data = regex.sub('', data)
    data_list = nltk.word_tokenize(data)
    data = [word for word in data_list if word not in stopwords.words('english')]
    detokenizer.detokenize(data, return_str=True)
    data = " ".join(data)    
    dbInfo = (header + data).lower()
    botanswers.objects.create(answer = dbAnswer, rating = 0, category_id = catID.id, entities = dbInfo, course_id = cid, file_id = fileid)
 
def docxParser(docxFile, cid, catID, fileid, docType):
               
    document = Document(docxFile)
            
    header = ""
    data = ""
    
    for n in iterBlockItems(document):
        #newHead = False
        if isinstance(n, Paragraph):
            for wInd, words in enumerate(n.runs):
                if words.bold:
                    if re.match(r'^\s*$', words.text) or words.text == ':':
                        exit
                    elif wInd > 0:
                        if n.runs[wInd - 1].text in header:
                            header = header + ' '.join(words.text.split())      
                            #newHead = True
                        #else:
                        #    print("THIS WOULD HAVE BEEN A HEADER: " + words.text)
                    else:
                        if data != "" and header != "":
                            while(header[-1:] == ':' or header[-1:] == ' '):
                                header = header[:-1]
                            #header = header + ': '  
                            #UNCOMMENT THIS LINE FOR TESTING
                            #####print(header + data + '\n')
                            #COMMENT THIS LINE FOR TESTING
                            parsedToDB(data, header, cid, catID, fileid)
                        data = ""
                        header = ' '.join(words.text.split())         
                        #newHead = True
            #identifying Headings 
            if (n.style.name == 'Heading 1' or n.style.name == 'Heading 2' or n.style.name == 'Heading 3'):
                #if data != "":
                if data != "" and header != "":
                    #UNCOMMENT THIS LINE FOR TESTING
                    #####print(header + data + '\n')
                    #COMMENT THIS LINE FOR TESTING
                    parsedToDB(data, header, cid, catID, fileid)
                data = ""
                header = ' '.join(n.text.split())    
                while(header[-1:] == ':' or header[-1:] == ' '):
                    header = header[:-1]
                header = header + ': '    
            else:
                #Checking for blank lines
                if n.text=="":
                    exit            
                else:
                    #Grab text if it is not in the header
                    tempHeader = header
                    tempText = ' '.join(n.text.split())
                    while(tempHeader[-1:] == ':' or tempHeader[-1:] == ' '):
                        tempHeader = tempHeader[:-1]
                    while(tempText[-1:] == ':' or tempText[-1:] == ' '):
                        tempText = tempText[:-1]
                    if not tempText in tempHeader:
                        tempText = ' '.join(n.text.split())
                        data = data + '<br>' + tempText
                
        elif isinstance(n, Table) and data == "":
            #number of columns in the table 
            numCols=len(n.columns)
            #number of rows in the table 
            numRows=len(n.rows)
            
          
            i = 0 
            data = ""
            while i <numRows:
                j=0
                while j<numCols:
                    check = ' '.join((n.table.cell(i, j)).text.split())
                    if check != ' ' and check != '': 
                        if data == "":
                            data = '<br>' + check
                        elif j > 0:
                            data = data + ' -- ' + check
                        else:
                            data = data + check
                    if j == numCols-1:
                        data = data + '<br>'
                    j+=1
                i+=1
            #COMMENT THIS LINE FOR TESTING
            #####print(header + data)
            #COMMENT THIS LINE FOR TESTING
            parsedToDB(data, header, cid, catID, fileid)
            data = ""
    
    if header != "" and data != "":
        #COMMENT THIS LINE FOR TESTING
        #####print(header + data)
        #COMMENT THIS LINE FOR TESTING
        parsedToDB(data, header, cid, catID, fileid)
        data = ""

