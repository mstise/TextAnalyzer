import MySQLdb
import shelve

def load_sql_file():
    category_dict = shelve.open('NamedEntityDisambiguator/dbs/category_dict')
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
                append_val(category_dict, entity, category)

def append_val(dic, key, val):
    hard_stoplist = ['artikler med døde links',
                     'commons-kategori på wikidata er ens med lokalt link',
                     'commons-kategori på wikidata er ens med sidetitel',
                     'intet lokalt billede og intet billede på wikidata',
                     'sider, der bruger automatiske isbn-henvisninger',
                     'wikipedia artikler med gnd autoritetsdata-id',
                     'wikipedia artikler med ndl autoritetsdata-id',
                     'wikipedia artikler med bnf autoritetsdata-id',
                     'wikipedia artikler med isni autoritetsdata-id',
                     'wikipedia artikler med lccn autoritetsdata-id',
                     'lokalt billede identisk med wikidata',
                     'lokalt billede forskelligt fra wikidata',
                     'wikipedia artikler med viaf autoritetsdata-id',
                     'articles with invalid date parameter in template',
                     'artikler hvor enkelte passager behøver uddybning (samlet liste)',
                     'artikler med filmpersonhenvisninger fra wikidata',
                     'kilder mangler (samlet liste)']

    key = key.lower()
    val = val.lower()
    val = val.replace("_", " ")
    if val not in hard_stoplist:
        dic.setdefault(key, [])
        tmp = dic[key]
        tmp.append(val)
        dic[key] = tmp

load_sql_file()