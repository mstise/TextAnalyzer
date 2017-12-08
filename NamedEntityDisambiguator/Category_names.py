#!/usr/bin/python
import MySQLdb
import threading

class myThread (threading.Thread):
    phrase_dic = {}
    def __init__(self, threadID, titles, hard_stoplist):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.titles = titles
        self.hard_stoplist = hard_stoplist
    def run(self):
        self.phrase_dic = query_phase(self.titles, self.hard_stoplist)

def split_list(lst, parts=1):
    length = len(lst)
    return [ lst[i*length // parts: (i+1)*length // parts]
             for i in range(parts) ]

def query_phase(titles, hard_stoplist):
    db = MySQLdb.connect(host="localhost",  # your host, usually localhost
                         user="duper",  # your username
                         passwd="an2loper",  # your password
                         db="wikidb",
                         charset='utf8')  # name of the data base

    # you must create a Cursor object. It will let
    #  you execute all the queries you need
    cur = db.cursor()

    phrase_dic = {}
    for title in titles:
        tmp_phrase_lst = []
        title_uppered = title.upper()
        title_uppered = title_uppered.replace("'", "\\'")
        # Use all the SQL you like
        cur.execute("SELECT cl_to" +
                    " FROM categorylinks" +
                    " WHERE cl_sortkey = '" + title_uppered + "'" +
                    " OR cl_sortkey LIKE '%\\n" + title_uppered + "'" +
                    " OR cl_sortkey LIKE '" + title_uppered + "\\n%'" +
                    " OR cl_sortkey LIKE '%\\n" + title_uppered + "\\n%';")

        # print all the first cell of all the rows
        for row in cur.fetchall():
            non_bytestring = row[0].decode("utf-8")
            tmp_phrase_lst.append(non_bytestring.replace("_", " ").lower())

        is_not_banned = lambda x: x not in hard_stoplist
        #is_not_contained = lambda x: x
        tmp_phrase_lst = list(filter(is_not_banned, tmp_phrase_lst))
        phrase_dic[title.lower()] = tmp_phrase_lst
    #print(str(phrase_dic))
    db.close()
    return phrase_dic

def category_words(titles):
#    db = MySQLdb.connect(host="localhost",  # your host, usually localhost
#                         user="duper",  # your username
#                         passwd="an2loper",  # your password
#                         db="wikidb",
#                         charset='utf8')  # name of the data base

    # you must create a Cursor object. It will let
    #  you execute all the queries you need
#    cur = db.cursor()

    phrase_dic = {}
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
    # Create new threads
    lsts = split_list(titles, parts=8)
    threads = []
    threads.append(myThread(1, lsts[0], hard_stoplist))
    threads.append(myThread(2, lsts[1], hard_stoplist))
    threads.append(myThread(3, lsts[2], hard_stoplist))
    threads.append(myThread(4, lsts[3], hard_stoplist))
    threads.append(myThread(5, lsts[4], hard_stoplist))
    threads.append(myThread(6, lsts[5], hard_stoplist))
    threads.append(myThread(7, lsts[6], hard_stoplist))
    threads.append(myThread(8, lsts[7], hard_stoplist))

    # Start new Threads
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    for thread in threads:
        for key in thread.phrase_dic.keys():
            phrase_dic[key] = thread.phrase_dic[key]

#    for title in titles:
#        tmp_phrase_lst = []
#        title_uppered = title.upper()
#        title_uppered = title_uppered.replace("'", "\\'")
#        # Use all the SQL you like
#        cur.execute("SELECT cl_to" +
#                    " FROM categorylinks" +
#                    " WHERE cl_sortkey = '" + title_uppered + "'" +
#                    " OR cl_sortkey LIKE '%\\n" + title_uppered + "'" +
#                    " OR cl_sortkey LIKE '" + title_uppered + "\\n%'" +
#                    " OR cl_sortkey LIKE '%\\n" + title_uppered + "\\n%';")

        # print all the first cell of all the rows
#        for row in cur.fetchall():
#            non_bytestring = row[0].decode("utf-8")
#            tmp_phrase_lst.append(non_bytestring.replace("_", " ").lower())

#        is_not_banned = lambda x: x not in hard_stoplist
        #is_not_contained = lambda x: x
#        tmp_phrase_lst = list(filter(is_not_banned, tmp_phrase_lst))
#        phrase_dic[title.lower()] = tmp_phrase_lst
    #print(str(threads[0].isAlive()))
    return phrase_dic

#print("Here are results: " + str(category_words(["Ritt Bjerregaard", "ANDERS FOGH RASMUSSEN"])))