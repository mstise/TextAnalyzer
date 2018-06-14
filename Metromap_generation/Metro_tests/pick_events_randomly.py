'''
This script is for picking random events from each test case, to test in user-evaluated tests
'''
import random
import numpy as np
random.seed(10)
np.random.seed(10)
import shelve


#final_clusters = shelve.open('../permdbs/final_clusters')

def print_random_clusters(case):
    #clusters = list(final_clusters[case])
    clusters = find_clusters(case)
    chosen_clusters = []
    max = 5
    if len(clusters) < max:
        max = len(clusters)
    for i in range(0, max):
        rnd_idx = random.randint(0, len(clusters) - 1)
        chosen_clusters.append(clusters[rnd_idx])
        del clusters[rnd_idx]
    print(case + ': ' + str(chosen_clusters))

def find_clusters(case):
    alllines = open('MMs/' + case + '.txt').readlines()
    clusters = []
    for line in alllines:
        if line[0:10] == 'clusternr:':
            clusters.append(line.replace('clusternr:', '').replace('\n', '').replace(' ', '').replace('*', ''))
    return clusters

print_random_clusters('Aalborg_Portland')
print_random_clusters('Birgit_Hansen')
print_random_clusters('Industri')
print_random_clusters('Per_Michael_Johansen')
print_random_clusters('Thomas_Kastrup')
print_random_clusters('Karneval')
print_random_clusters('Aab')
print_random_clusters('Frederikshavn')
print_random_clusters('Socialdemokratiet')
