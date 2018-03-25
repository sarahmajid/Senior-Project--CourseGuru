'''
Created on Mar 24, 2018

@author: Andriy Marynovskyy
'''
from pptx import Presentation

def parsePPTX(file, cid, catID, fileid):
    parseFile = Presentation(file)
    
    for slide in parseFile.slides:
        for shape in slide.shapes:
            if hasattr(shape, "text"):
                print(shape.text)
                 
                
    #===========================================================================
    # for slide in parseFile.slides:
    #     for shape in slide.shapes:
    #         if not shape.has_text_frame:
    #             for paragraph in shape.text_frame.paragraphs:
    #                 for run in paragraph.runs:
    #                     print(run.text)
    #===========================================================================
    file.close()
