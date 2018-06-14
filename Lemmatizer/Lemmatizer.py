import os

def lemmatize(idirpath, odirpath):
    counter = 0
    for doc in os.listdir(idirpath):
        if counter % 500 == 0:
            print(str(counter))
        idocpath = idirpath + '/' + doc
        odocpath = odirpath + '/' + doc
        os.system("./cstlemma -L -eU -p+ -q- -t- -f'1/flexrules' -B'$w' -l- -b'$w' -d'dict' -u -c'$b1[[$b~1]?$B]$s' -i " + idocpath + " -o " + odocpath)
        counter += 1

lemmatize('../Metromap_generation/Processed_news', '../Metromap_generation/Lemmatized')