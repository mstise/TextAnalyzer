import os
import xml.etree.ElementTree
import paths

def format_text(text):
    if text[-1] != '.' or text[-2] != '.':
        text = text + '.'
    return text

def readXML(node):
    global body
    global header
    tag = node.tag[38:]
    if (tag == "p"):
        if (isinstance(node.text, str) and len(str(node.text)) > 1):
            if len(body) > 0 and body[-1] != " ":
                body += " "
            body += format_text(str(node.text))
    elif (tag == "hl1"):
        header = format_text(str(node.text))
    for child in node:
        readXML(child)

body = ""
header = ""

for subdir, dirs, files in os.walk(paths.get_newest_news_path()):
    if (subdir[-10:] == "/TabletXML"):
        for filename in os.listdir(subdir):
            test = os.listdir(paths.get_external_procesed_news())
            if (filename[-4:] == ".xml" and not any(file[:-4] == filename[:-4] for file in os.listdir(paths.get_external_procesed_news()))):
                readXML(xml.etree.ElementTree.parse(subdir + '/' + filename).getroot())
                if body == "":
                    continue
                with open(paths.get_external_procesed_news() + "/" + str(filename[:-4]) + ".txt", "w") as text_file:
                    text_file.write((header + " " + body))
                body = ""
                header = ""