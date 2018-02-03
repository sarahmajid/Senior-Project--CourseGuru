'''
Created on Feb 2, 2018

@author: Scott
'''
import os
from pdfminer.pdfparser import PDFParser, PDFDocument
#===============================================================================
# from pdfminer.pdfpage import PDFPage
#===============================================================================
# From PDFInterpreter import both PDFResourceManager and PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice
# Import this to raise exception whenever text extraction from PDF is not allowed
#from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.layout import LAParams, LTTextBox, LTTextLine
from pdfminer.converter import PDFPageAggregator

my_file = (r'E:\Libraries\Wayne State\Winter2018\CSC 4996\Projects\Senior-Project--CourseGuru\docParser\ExamplePDF.pdf')
fp = open(my_file, "rb")

parser = PDFParser(fp)
doc = PDFDocument()
parser.set_document(doc)
doc.set_parser(parser)
doc.initialize('')
rsrcmgr = PDFResourceManager()
laparams = LAParams()
laparams.char_margin = 1.0
laparams.word_margin = 1.0
device = PDFPageAggregator(rsrcmgr, laparams=laparams)
interpreter = PDFPageInterpreter(rsrcmgr, device)
extracted_text = ''

for page in doc.get_pages():
    interpreter.process_page(page)
    layout = device.get_result()
    for lt_obj in layout:
        if isinstance(lt_obj, LTTextBox) or isinstance(lt_obj, LTTextLine):
            extracted_text += lt_obj.get_text()

hello = extracted_text

import sys

sys.stdout.buffer.write(extracted_text.encode('utf8'))
