import re

def cut_brackets(text):
    return re.sub(r'\{[^}]*\}', '', text)

def make_parentheses_for_regex_list(names):
    new_names = []
    for name in names:
        new_name = make_parentheses_for_regex_text(name)
        new_names.append(new_name)
    return new_names

def make_parentheses_for_regex_text(name):
    new_name = name.replace('(', '\(')
    new_name = new_name.replace(')', '\)')
    return new_name

def unmake_parentheses_for_regex(name):
    new_name = name.replace('\(', '(')
    new_name = new_name.replace('\)', ')')
    return new_name

def unmake_parentheses_for_regex_list(names):
    return [unmake_parentheses_for_regex(name) for name in names]

def strip_chars(string):
    removed_characters = '.,:;<>!?(){}[]\"\'-\n'
    for char in removed_characters:
        string = string.strip(char)
    return string

def split_and_delete_special_characters(string):
    split = string.split(' ')
    result = []

    for part in split:
        new_string = part
        old_string = "old"
        while new_string != old_string:
            old_string = new_string
            new_string = strip_chars(new_string)
        result.append(new_string.lower())
    return result