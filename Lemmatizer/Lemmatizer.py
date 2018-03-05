from nltk.stem import snowball
import os
import re
import paths

def stemmer(string_input):
    stemmer = snowball.DanishStemmer()
    pattern = re.compile('[?!.,:;%()\"\'´`/]+', re.UNICODE)
    string_input = pattern.sub('', string_input)
    result = ''
    for word in string_input.split():
        result += ' '
        result += stemmer.stem(word)
    return result

for filename in os.listdir(paths.get_external_procesed_news()):
    stemmed_document_text = ''
    with open(paths.get_external_procesed_news() + '/' + filename, 'r') as f:
        stemmed_document_text = stemmer(f.read())
    with open(paths.get_stemmed_path() + "/" + filename, "w") as text_file:
        text_file.write(stemmed_document_text)