import google

def google_scraper(mention, list_of_related_mentions):
    related_mentions = ""
    for men in list_of_related_mentions[:-1]:
        related_mentions += "\"" + men + "\" OR "
    if len(list_of_related_mentions) > 0:
        related_mentions += "\"" + list_of_related_mentions[-1] + "\""
    site = "site:https://dk.linkedin.com/in OR site:https//:dk.linkedin.com/company"

    search_string = related_mentions + " " + mention + " " + site

    return google.search(search_string, lang='dk')

#search_results = google.search('“FREDERIKSHAVN” OR “Poul” OR “Ole Damgaard Jensen” OR “Maritime Ship Supply” OR “Skibshandler Damsgaard” Poul-Ole Damgaard Jensen site:https://dk.linkedin.com/in OR site:https://dk.linkedin.com/company', lang='dk')
#item = next(search_results)
#print(item)
#print(next(search_results))



#google_scraper('test', ["nymand", "olsen"])