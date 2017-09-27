with open('.paths', 'r') as paths_file:
  fileshare_root = str.strip(paths_file.readline())
  newest_news = str.strip(paths_file.readline())
  external_disk = str.strip(paths_file.readline())

def get_fileshare_root_path():
  return fileshare_root

def get_newest_news_path():
  return newest_news

def get_external_disk_path():
  return external_disk
