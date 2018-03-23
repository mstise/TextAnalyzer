import MySQLdb

def load_sql_file():
    db = MySQLdb.connect(host="localhost",  # your host, usually localhost
                         user="duper",  # your username
                         passwd="an2loper",  # your password
                         db="wikidb",
                         charset='utf8')  # name of the data base
    # you must create a Cursor object. It will let
    #  you execute all the queries you need
    cur = db.cursor()

    cur.execute("SELECT cl_to" +
                " FROM categorylinks;")
    print('TEST')
    for row in cur.fetchall():
        print('test')
        non_bytestring = row[0].decode("utf-8")
        print(non_bytestring)
        #tmp_phrase_lst.append(non_bytestring.replace("_", " ").lower())