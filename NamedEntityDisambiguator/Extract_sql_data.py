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

def append_val(dic, key, val):
    hard_stoplist = ['Artikler med døde links',
                     'Commons-kategori på Wikidata er ens med lokalt link',
                     'Commons-kategori på Wikidata er ens med sidetitel',
                     'Intet lokalt billede og intet billede på Wikidata',
                     'Sider, der bruger automatiske ISBN-henvisninger',
                     'Wikipedia artikler med GND autoritetsdata-ID',
                     'Wikipedia artikler med NDL autoritetsdata-ID',
                     'Wikipedia artikler med BNF autoritetsdata-ID',
                     'Wikipedia artikler med ISNI autoritetsdata-ID',
                     'Wikipedia artikler med LCCN autoritetsdata-ID',
                     'Lokalt billede identisk med Wikidata',
                     'Lokalt billede forskelligt fra Wikidata',
                     'Wikipedia artikler med VIAF autoritetsdata-ID',
                     'Articles with invalid date parameter in template',
                     'Artikler hvor enkelte passager behøver uddybning (samlet liste)',
                     'Artikler med filmpersonhenvisninger fra Wikidata',
                     'Kilder mangler (samlet liste)']

    key = key.lower()
    #val = val.lower()
    val = val.replace("_", " ")
    if val not in hard_stoplist:
        dic.setdefault(key, [])
        tmp = dic[key]
        tmp.append(val)
        dic[key] = tmp
    if key == 'trige':
        print("KEY: " + key + " VAL: " + str(dic[key]))

load_sql_file()