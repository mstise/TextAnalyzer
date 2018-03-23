import MySQLdb

def load_sql_file():
    phrase_dict = {}
    db = MySQLdb.connect(host="localhost",  # your host, usually localhost
                         user="duper",  # your username
                         passwd="an2loper",  # your password
                         db="wikidb",
                         charset='utf8')  # name of the data base
    # you must create a Cursor object. It will let
    #  you execute all the queries you need
    cur = db.cursor()

    cur.execute("SELECT cl_to, cl_sortkey" +
                " FROM categorylinks;")

    for row in cur.fetchall():
        category = row[0].decode("utf-8")
        entity = row[1].decode("utf-8")
        if category != None and category != '' and entity != None and entity != '':
            phrase_dict[entity.lower()] = category.lower()
            print(entity + " : " + phrase_dict[entity.lower()])
        #tmp_phrase_lst.append(non_bytestring.replace("_", " ").lower())
    #print('Henrik 7: ' + phrase_dict['henrik 7'])

load_sql_file()