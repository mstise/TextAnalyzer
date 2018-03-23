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
        entity_row = row[1].decode("utf-8")
        if category != None and category != '' and entity_row != None and entity_row != '':
            entities = []
            for entity in [s.strip() for s in entity_row.splitlines()]:
                entities.append(entity)
            for entity in entities:
                append_val(phrase_dict, entity, category)
                if entity == 'TRIGE':
                    print(str(category))
                #print(entity.lower() + " : ")# + str(phrase_dict[entity.lower()]))
        #tmp_phrase_lst.append(non_bytestring.replace("_", " ").lower())
    #print('TRIGE: ' + str(phrase_dict['trige']))

def append_val(dic, key, val, default = []):
    key = key.lower()
    val = val.lower()
    dic.setdefault(key, default)
    tmp = dic[key]
    tmp.append(val)
    dic[key] = tmp
    print("KEY: " + key + " VAL: " + str(dic[key]))

load_sql_file()