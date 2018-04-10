import os

def snap():
    os.system("./snap/bigclam -o:snap/snapout/ -c:2 -i:snap/edges.txt -l:snap/labels.txt")