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
        #parent_element = parent._Document__body._body
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
        
    
    #call the function to check the block is a paragraph or a table
    for n in iterBlockItems(document):
        if isinstance(n, Paragraph):
            print(n.text)
        elif isinstance(n, Table):
            for row in n.rows:
                for cell in row.cells:
                    print(cell.text)

    
    categoryPos = [] 
    categoryPosHeading = []
    categoryPos1 = [] 
    categoryPosHeading1 = []
    header = []
    data = []
    
    
    #obtains Heading positions and text 
    for i in [i for i, paragraph in enumerate(document.paragraphs) if paragraph.style.name == 'Heading 1']:
            categoryPos.append(i)
            categoryPosHeading.append(document.paragraphs[i].text)
  
    
    #getting heading and content according to categoryPos
    i=0 
    while i <len(categoryPos)-1:
        #Getting the first paragraph of the docx as the first category, also retrieving the the content up to first heading 1
        if i == 0:
            header.append(document.paragraphs[i].text)
            data.append(document.paragraphs[i:categoryPos[i]])
        header.append(document.paragraphs[categoryPos[i]].text)
        data.append(document.paragraphs[categoryPos[i]:categoryPos[i+1]])
        i+=1        
    
    #     #For Testing 
    for n in header: 
        print(n) 
    for n in data: 
        for j in n:
            print(j.text)
            #print(j.table)  