'''
Created on Feb 2, 2018

@author: Scott
'''
from pdfminer.pdfparser import PDFParser, PDFDocument
#===============================================================================
# from pdfminer.pdfpage import PDFPage
#===============================================================================
# From PDFInterpreter import both PDFResourceManager and PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
#from pdfminer.pdfdevice import PDFDevice
# Import this to raise exception whenever text extraction from PDF is not allowed
#from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.layout import LAParams, LTTextBox, LTTextLine
from pdfminer.converter import PDFPageAggregator

import re

#===============================================================================
# my_file = (r'E:\Libraries\Wayne State\Winter2018\CSC 4996\Projects\Senior-Project--CourseGuru\docParser\ExamplePDF.pdf')
# fp = open(my_file, "rb")
# 
# parser = PDFParser(fp)
# doc = PDFDocument()
# parser.set_document(doc)
# doc.set_parser(parser)
# doc.initialize('')
# rsrcmgr = PDFResourceManager()
# laparams = LAParams()
# #Required to define seperation of text within pdf
# laparams.char_margin = 1
# laparams.word_margin = 1
# 
# #Device takes LAPrams and uses them to parse individual pdf objects
# device = PDFPageAggregator(rsrcmgr, laparams=laparams)
# interpreter = PDFPageInterpreter(rsrcmgr, device)
# extracted_text = ''
# 
# for page in doc.get_pages():
#     interpreter.process_page(page)
#     layout = device.get_result()
#     for lt_obj in layout:
#         if isinstance(lt_obj, LTTextBox) or isinstance(lt_obj, LTTextLine):
#             extracted_text += lt_obj.get_text()
#===============================================================================



test = re.search("prof:(.*)", "test:otherdata\r\nprof:name goes here\r\nprof:test", re.MULTILINE)
profName = test.group(1)
print(test.group(1))
import sys

#sys.stdout.buffer.write(extracted_text.encode('utf8'))
