#!/usr/bin/python
import MySQLdb

db = MySQLdb.connect(host="localhost",    # your host, usually localhost
                     user="duper",         # your username
                     passwd="an2loper",  # your password
                     db="wikidb",
                     charset='utf8')        # name of the data base

# you must create a Cursor object. It will let
#  you execute all the queries you need
cur = db.cursor()

def category_words(titles):
    phrase_lst = []
    hard_stoplist = ['Artikler med døde links',
                'Commons-kategori på Wikidata er ens med lokalt link',
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
                'Kilder mangler (samlet liste)',]

    #soft_stoplist = ['Artikler hvor enkelte passager behøver uddybning siden',
    #                 'Kilder mangler siden']

    for title in titles:
        tmp_phrase_lst = []
        title = title.upper()
        # Use all the SQL you like
        cur.execute("SELECT cl_to" +
                    " FROM categorylinks" +
                    " WHERE cl_sortkey = '" + title + "'" +
                    " OR cl_sortkey LIKE '%\\n" + title + "'" +
                    " OR cl_sortkey LIKE '" + title + "\\n%'" +
                    " OR cl_sortkey LIKE '%\\n" + title + "\\n%';")

        # print all the first cell of all the rows
        for row in cur.fetchall():
            non_bytestring = row[0].decode("utf-8")
            tmp_phrase_lst.append(non_bytestring.replace("_", " "))

        is_not_banned = lambda x: x not in hard_stoplist
        #is_not_contained = lambda x: x
        tmp_phrase_lst = list(filter(is_not_banned, tmp_phrase_lst))
        phrase_lst.extend(tmp_phrase_lst)

    return phrase_lst

print(category_words(["ANDERS FOGH RASMUSSEN"]))
db.close()