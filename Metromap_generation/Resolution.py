import os
from datetime import date

def resolutionize(dirpath, sdate=date(2014, 1, 1), edate=date.today(), resolution='month'):
    valid_filenames = []
    for filename in os.listdir(dirpath):
        file_date = get_date(filename)
        if sdate <= file_date and file_date <= edate:
            valid_filenames.append(filename)
    valid_filenames = sorted(valid_filenames, key=lambda f: get_date(f))

    cluster_date = get_date(valid_filenames[0])
    clusters = [[]]
    for i in range(0, len(valid_filenames)):
        if compare_dates(get_date(valid_filenames[i]), cluster_date, resolution):
            cluster_date = get_date(valid_filenames[i])
            clusters.append([])
        clusters[-1].append(valid_filenames[i])
    return clusters

def get_date(filename):
    file_number = filename.split('_')[-2]
    return date(int(file_number[0:4]), int(file_number[4:6]), int(file_number[6:8]))

def compare_dates(file_date, cluster_date, resolution):
    if resolution == 'day':
        if file_date.day > cluster_date.day:
            return True
    if resolution == 'month':
        if file_date.month > cluster_date.month:
            return True
    if resolution == 'year':
        if file_date.year > cluster_date.year:
            return True
    return False

#resolutionize('Example_documents')