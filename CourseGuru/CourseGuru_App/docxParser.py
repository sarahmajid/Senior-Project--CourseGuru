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