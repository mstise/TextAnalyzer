import re

def cut_brackets(text):
    return re.sub(r'\{[^}]*\}', '', text)

def make_parentheses_for_regex_list(names):
    for name in names:
        new_name = make_parentheses_for_regex_text(name)
        names.remove(name)
        names.append(new_name)

def make_parentheses_for_regex_text(name):
    new_name = name.replace('(', '\(')
    new_name = new_name.replace(')', '\)')
    return new_name

def unmake_parentheses_for_regex(name):
    new_name = name.replace('\(', '(')
    new_name = new_name.replace('\)', ')')
    return new_name