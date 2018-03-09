'''
Created on Mar 8, 2018

@author: Andriy Marynovskyy
'''
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
            if n.style.name == 'Heading 1':
        
                #print("Heading:")
                #storing the position of the heading
                categoryPos.append(parPosition)
                #storing the heading 
                header.append(n.text)
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
        #if statement to check if the text contains : for splitting also header[-1] will give you the last added header
        #    which is the correct header since this is sequential. 
                #data under the heading
                #print("Body:")
                #print(parPosition)
                else:
                    answer.append(n.text)
                    headerAnswer.append(header[-1]+ " " + n.text)
                    parPosition+=1
                    print(n.text)
                
        elif isinstance(n, Table):
            #number of columns in the table 
            numCols=len(n.columns)
            #number of rows in the table 
            numRows=len(n.rows)
            #print(numCols)
            #print(numRows)
            #tables position within the document according to paragraphs
            #print(parPosition)
            tblPosition=parPosition
    #using number of columns and rows in the table data can be stored various ways in the database.    
            #tableData.append(header[-1])
            i = 0 
            while i <numRows:
                j=0
                while j<numCols:
                    tableData.append((n.table.cell(i, j)).text)
                    j+=1
                    #===========================================================
                    # if j != numCols-1:
                    #     #trying to figure out go to join all the cells for a particular row into 1 index 
                    #     tableData.appand()
                    #     tableData.append((' '.join(n.table.cell(i, j)).text))
                    # else:
                    #     tableData.append((n.table.cell(i, j)).text)
                    #     j+=1
                    #===========================================================
                i+=1
            #below prints table content cell by cell 
            #for row in n.rows:
            #    for cell in row.cells:
            #        print(cell.text)

    
    for n in headerAnswer: 
        print(n)
    
    for n in tableData:
        print(n)
    
    #obtains Heading positions and text 
  #=============================================================================
  #   for i in [i for i, paragraph in enumerate(document.paragraphs) if paragraph.style.name == 'Heading 1']:
  #           categoryPos.append(i)
  #           categoryPosHeading.append(document.paragraphs[i].text)
  # 
  #=============================================================================
    
    #getting heading and content according to categoryPos
    #===========================================================================
    # i=0 
    # while i <len(categoryPos)-1:
    #     #Getting the first paragraph of the docx as the first category, also retrieving the content up to first heading 1
    #     if i == 0:
    #         header.append(document.paragraphs[i].text)
    #         data.append(document.paragraphs[i:categoryPos[i]])
    #     header.append(document.paragraphs[categoryPos[i]].text)
    #     data.append(document.paragraphs[categoryPos[i]:categoryPos[i+1]])
    #     i+=1       
    #===========================================================================
        
#    for n in data: 
#        for j in n: 
            
    
    #     #For Testing 
    #Prints all Headers 
    #for n in header: 
    #    print(n) 
    #prints all data under headers
    #for n in data: 
    #    print(n)
            #print(j.table)  