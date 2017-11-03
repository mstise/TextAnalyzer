import os

location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
with open(location + '/.paths', 'r') as paths_file:
  fileshare_root = str.strip(paths_file.readline())
  newest_news = str.strip(paths_file.readline())
  external_disk = str.strip(paths_file.readline())
  external_disk_root = str.strip(paths_file.readline())
  wikipedia_article = str.strip(paths_file.readline())

def get_fileshare_root_path():
  return fileshare_root

def get_newest_news_path():
  return newest_news

def get_external_disk_path():
  return external_disk

def get_external_disk_root_path():
  return external_disk_root

def get_wikipedia_article_path():
  return wikipedia_article