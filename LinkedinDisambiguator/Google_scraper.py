import google

def google_scraper(mention, list_of_related_mentions):
    related_mentions = ""
    for men in list_of_related_mentions[:-1]:
        related_mentions += "\"" + men + "\" OR "
    if len(list_of_related_mentions) > 0:
        related_mentions += "\"" + list_of_related_mentions[-1] + "\""
    site = "site:https://dk.linkedin.com/in OR site:https//:dk.linkedin.com/company"

    search_string = related_mentions + " " + mention + " " + site

    print(next(google.search(search_string, lang='dk')))

google_scraper('test', [])