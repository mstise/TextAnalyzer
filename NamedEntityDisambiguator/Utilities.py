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

def convert_danish_letters(string):
    string = string.replace('\\xe6', 'æ')
    string = string.replace('\\xc6', 'Æ')
    string = string.replace('\\xf8', 'ø')
    string = string.replace('\\xd8', 'Ø')
    string = string.replace('\\xe5', 'å')
    string = string.replace('\\xc5', 'Å')
    string = string.replace('\\xf4', 'ô')
    return string

def convert_danish_letters_list(strings):
    resulting_list = []
    for string in strings:
        resulting_list.append(convert_danish_letters(string))
    return resulting_list