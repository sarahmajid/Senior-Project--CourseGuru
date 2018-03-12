'''
Created on Mar 11, 2018

@author: Andriy Marynovskyy
'''
import re 
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

def passwordValidator(password):
    passRegCheck = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)"
    if (len(password)<8): 
        errorMsg = 'Your password must be at least 8 characters long.'
        return errorMsg
    elif ((re.search(passRegCheck, password))==None):
        errorMsg = "Your password must contain one uppercase character, one lowercase character, and at least one number!"
        return errorMsg
    else:
        return None
    
def emailValidator(email):
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False        