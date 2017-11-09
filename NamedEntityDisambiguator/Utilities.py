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