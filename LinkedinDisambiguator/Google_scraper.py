import google
from random import uniform
from time import sleep


# import urllib
# import simplejson

def google_scraper(mention, list_of_related_mentions):
    related_mentions = ""
    for men in list_of_related_mentions[:-1]:
        related_mentions += "\"" + men + "\" OR "
    if len(list_of_related_mentions) > 0:
        related_mentions += "\"" + list_of_related_mentions[-1] + "\""
    site = "site:https://dk.linkedin.com/in OR site:https://dk.linkedin.com/company"

    search_string = related_mentions + " " + mention + " " + site

    # query = urllib.parse.urlencode({'q' : search_string})
    # url = 'http://ajax.googleapis.com/ajax/services/search/web?v=1.0&%s' % (query)
    # search_results = urllib.request.urlopen(url)
    # json = simplejson.loads(search_results.read())
    # results = json['responseData']['results']

    return google.search(search_string, lang='dk', pause=uniform(5, 10))


# search_results = google.search('“FREDERIKSHAVN” OR “Poul” OR “Ole Damgaard Jensen” OR “Maritime Ship Supply” OR “Skibshandler Damsgaard” Poul-Ole Damgaard Jensen site:https://dk.linkedin.com/in OR site:https://dk.linkedin.com/company', lang='dk')
# item = next(search_results)
# print(item)
# print(next(search_results))



#results = google_scraper('Lisa Sandager Ramlow',
#                         ["AutoBranchen Danmark", "Autobranchen", "Danmarks adm", "Golf'er", "Jesper Brix",
#                          "Lars Løkke Rasmussens", "Lisa Sandager Ramlow", "Torben Lund Kudsk",
#                          "autoforhandler Pedersen & Nielsen", "christiansborg"])

#for result in results:
#    print(result)
