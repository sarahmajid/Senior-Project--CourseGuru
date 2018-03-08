from docx import *
import re

file = Document('path/syllabus.docx')

for par in file.paragraphs:
    for words in par.runs:
        if words.bold:
            if re.match(r'^\s*$', words.text) or words.text == ':':
                exit
            else:
                temp = words.text
                while(temp[-1:] == ':' or temp[-1:] == ' '):
                    temp = temp[:-1]
                print (temp)

