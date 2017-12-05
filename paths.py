import os

location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
with open(location + '/.paths', 'r') as paths_file:
  fileshare_root = str.strip(paths_file.readline())
  newest_news = str.strip(paths_file.readline())
  all_external_entities= str.strip(paths_file.readline())
  external_disk_root = str.strip(paths_file.readline())
  wikipedia_article = str.strip(paths_file.readline())
  external_annotated = str.strip(paths_file.readline())
  external_processed_news = str.strip(paths_file.readline())
  external_disambiguated_output = str.strip(paths_file.readline())

def get_fileshare_root_path():
  return fileshare_root

def get_newest_news_path():
  return newest_news

def get_all_external_entities_path():
  return all_external_entities

def get_external_disk_root_path():
  return external_disk_root

def get_wikipedia_article_path():
  return wikipedia_article

def get_external_annotated():
  return external_annotated

def get_external_procesed_news():
  return external_processed_news

def get_external_disambiguated_outputs():
  return external_disambiguated_output