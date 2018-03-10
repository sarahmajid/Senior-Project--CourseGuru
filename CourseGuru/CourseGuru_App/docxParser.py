'''
Created on Mar 8, 2018

@author: Andriy Marynovskyy

'''
 
import re
import nltk

from nltk.corpus import stopwords

from docx import Document
from docx.document import Document as _Document 
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.table import _Cell, Table
from docx.text.paragraph import Paragraph
from django.utils.lorem_ipsum import paragraph

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
            
def docxParser(docxFile):
               
    document = Document(docxFile)
            
    categoryPos = [] 
    header = []
    answer = []   
    headerAnswer = [] 
    
    tableData = [] 
    
    #call the function to check the block is a paragraph or a table
    #obtains position of each paragraph or table 
    parPosition = 0 
    tblPosition = 0
    for n in iterBlockItems(document):
        if isinstance(n, Paragraph):
            #getting the heading paragraphs 
            if n.style.name == 'Heading 2':
                #storing the position of the heading
                categoryPos.append(parPosition)
                #storing the heading 
                header.append(re.sub('[^A-Za-z0-9]+', '', (n.text)))
                #print(parPosition)
                parPosition+=1
                print(n.text)
            #takes the first line as the initial header
            else:
                if parPosition == 0:
                    header.append(n.text)
                    parPosition+=1
                    print(n.text)
                elif n.text=="":
                    throwAway = n.text             
                else:
                    answer.append(n.text)
                    headerAnswer.append(header[-1]+ "|" + n.text)
                    parPosition+=1
                    print(n.text)
                
        elif isinstance(n, Table):
            #number of columns in the table 
            numCols=len(n.columns)
            #number of rows in the table 
            numRows=len(n.rows)

            tblPosition=parPosition
            i = 0 
            while i <numRows:
                j=0
                while j<numCols:
                    tableData.append((n.table.cell(i, j)).text)
                    j+=1
                i+=1

    for n in headerAnswer: 
        print(n)
    
    for n in tableData:
        print(n)
        
    for n in answer: 
        print(n)
