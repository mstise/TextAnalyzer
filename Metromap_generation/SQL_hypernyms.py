import MySQLdb
import warnings
import shelve
import os

secondrank = False

def run():
    warnings.filterwarnings('ignore', category=MySQLdb.Warning)
    db = MySQLdb.connect(host="localhost",  # your host, usually localhost
                         user="duper",  # your username
                         passwd="an2loper",  # your password
                         db="ontology",
                         charset='utf8')  # name of the data base
    # you must create a Cursor object. It will let
    #  you execute all the queries you need
    cur = db.cursor()
    #load_word_dic(cur)

    doc2terms = shelve.open("dbs/doc2terms")
    counter = -1
    #for doc in doc2terms.keys():
    for doc in os.listdir('Lemmatized'):
        counter += 1
        print(counter)
        #if counter > 10000:
        #    break
        terms = doc2terms[doc]
        results, rank2lemma = load_sql_hypernyms(terms, cur)
        create_rank_doc(doc, rank2lemma, 'Ranked')
        terms.extend(results)
        terms = list(set(terms))
        doc2terms[doc] = terms

def load_sql_hypernyms(top50words, cur):
    results = set()
    rank2lemma = {}

    where_clause = " WHERE ws.word_id = w.id AND"
    startmarker = 0
    for i in range(0, len(top50words)):
        word = top50words[i]
        if word[:2] == '*w' or word[:2] == '*r' or i > 30 or banned(word):
            if i == startmarker:
                startmarker += 1
            continue
        if i == startmarker:
            where_clause += " (w.form = '" + word + "'"
        else:
            where_clause += " OR w.form = '" + word + "'"
    if where_clause[-3:] == 'AND': #top50words is "empty"
        return results, rank2lemma
    where_clause += ")"#;"

    query_clause = "(SELECT ws.synset_id, w.form" + " FROM wordsenses ws, words w" + where_clause + ')'

    cur.execute("SELECT" +
                    " a.form as val, b.form as syn" +
                " FROM" +
                        query_clause + " as a" +
                    " INNER JOIN " +
                        "(SELECT w.form, ws.synset_id" +
                        " FROM wordsenses ws, words w "
                        " WHERE w.id = ws.word_id) as b" +
                    " ON a.synset_id = b.synset_id" +
                " WHERE a.form != b.form;")

    syns = cur.fetchall()
    for row in syns:
        if len(row[1].split(' ')) == 1 and unbanned_row(row): #Only 1-word words
            results.add('*f' + row[1].lower())
            append_row(rank2lemma, row)

    results = get_firstrank_hypernyms(top50words, cur, results, rank2lemma)

    if secondrank:
        results = get_firstrank_hypernyms(list(results), cur, results, rank2lemma)

    return list(results), rank2lemma

def get_firstrank_hypernyms(words, cur, prev, rank2lemma):
    firstranks = prev.copy()
    if len(prev) == 0:
        return firstranks

    where_clause = " WHERE ws.word_id = w.id AND r.synsets_id = ws.synset_id AND r.name2 = 'has_hyperonym' AND s.id = r.value AND"
    startmarker = 0
    for i in range(0, len(words)):
        word = words[i]
        if word[:2] == '*w' or word[:2] == '*r' or i > 30 or banned(word):
            if i == startmarker:
                startmarker += 1
            continue
        if i == startmarker:
            where_clause += " (w.form = '" + word + "'"
        else:
            where_clause += " OR w.form = '" + word + "'"
    where_clause += ")"#;"

    query_clause = "(SELECT ws.word_id, ws.synset_id, w.form, r.name2, s.label, s.id" + " FROM wordsenses ws, words w, relations r, synsets s" + where_clause + ')'

    cur.execute("SELECT" +
                    " a.form as val, b.form as syn" +
                " FROM" +
                        query_clause + " as a" +
                    " INNER JOIN " +
                        "(SELECT w.form, ws.synset_id" +
                        " FROM wordsenses ws, words w"
                        " WHERE w.id = ws.word_id) as b" +
                    " ON a.id = b.synset_id" +
                " WHERE a.form != b.form;")

    rankresults = cur.fetchall()
    for row in rankresults:
        if len(row[1].split(' ')) == 1 and row[1] != 'TOP' and unbanned_row(row): #Only 1-word words, and that there is no more upper words
            firstranks.add('*f' + row[1].lower())
            append_row(rank2lemma, row)
    return firstranks

def append_row(rank2lemma, row):
    lemma = row[0].lower()
    rank = row[1].lower()
    rank2lemma.setdefault(rank, [])
    tmp = rank2lemma[rank]
    if lemma not in tmp:
        tmp.append(lemma)
        rank2lemma[rank] = tmp

def unbanned_row(row):
    rank = row[1].lower()
    if rank in ['person', 'hoved', 'menneske', 'individ', 'mand', 'm/k\'er']:
        return False
    else:
        return True

def banned(word):
    if 'ł' in word or 'ż' in word or '\'' in word or '/' in word:
        return True
    else:
        return False

def create_rank_doc(doc, rank2lemma, dest):
    f_dest = open(dest + '/' + doc, 'w')
    for rank in rank2lemma.keys():
        lemmas = rank2lemma[rank]
        lemma_string = create_lemma_string(lemmas)
        f_dest.write(rank + '\t' + lemma_string + '\n')

def create_lemma_string(lemmas):
    lemma_string = '['
    for lemma in lemmas:
        lemma_string += lemma + ', '
    lemma_string = str(lemma_string[:-2]) + ']'
    return str(lemma_string)



run()