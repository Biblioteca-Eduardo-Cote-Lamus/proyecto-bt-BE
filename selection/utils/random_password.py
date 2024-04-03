import random
import string

def make_random_password(length=8, special_chars=True, digits=True, upper_case=True, lower_case=True):

    special_char = ""
    digits_char = ""
    upper_case_char = ""
    lower_case_char = ""

    if special_chars:
        special_char = string.punctuation
    if digits:
        digits_char = string.digits
    if upper_case:
        upper_case_char = string.ascii_uppercase
    if lower_case:
        lower_case_char = string.ascii_lowercase
    
    return "".join(random.choices(special_char+ digits_char + upper_case_char + lower_case_char , k=length))