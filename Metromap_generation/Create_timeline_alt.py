#!/usr/bin/python
import random
import numpy as np
random.seed(10)
np.random.seed(10)
import shelve
from Metromap_generation.Resolution import resolutionize
from itertools import groupby
from Metromap_generation.TopicSummarization.Topic_summarization import topic_summarization
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from Metromap_generation.TimelineUtils import get_rec_disamb_pairs
from itertools import chain

def collapse_to_string(lst):
    return ' '.join(lst)

####################################################################################################################################
                                    #            SAVING            #                                                               #
                                    #                              #                                                               #
                                    ################################                                                               #
#load_adj = True        #False: Creates new adjacency matrix from docs (skal være False hvis paper_epsilon = True)                 #
#load_tf_idf = True      #False: Creates new mapping between target docs to tf-idf                                                 #
#load_W = True          #False: Cluster words by gradient descent                                                                  #
                                                                                                                                   #
####################################################################################################################################
                                    #       Cluster-Options        #                                                               #
                                    #                              #                                                               #
                                    ################################                                                               #
                                                                                                                                   #                                                                                           #
group_size = 3 #how many timelines?                                                                                                #
resetter = 0.001  #Resets to this value, if update is below it.                                                                    #
#resetter can take the following values:                                                                                           #
#resetter = 0.001 works best for now (paper_epsilon will have to be false in this case)                                            #
#resetter = 10**(-8) #This seems to be too low, and makes updates too large for convergence                                        #
#resetter = 0 # In this case, the divide by zero is handled by taking highest seen value to date (updates too large here as well)  #
paper_epsilon = False #If false the epsilon is used directly as threshold for clustering, with resetter-value                      #
#paper_noisify = False #Introduce noise in graph according to paper. This slows down the approach considerably (for litte dataset atleast)
earliest_date = False #doesnt work that well tho...picks best if false




#
########################################################################################################################

example_run = 'Socialdemokratiet'#
def run2():
    partitioned_docs, _ = resolutionize('example_documents/' + example_run, resolution='month')
    clusters2term = shelve.open("dbs/clusters2term")
    cluster2resolution = shelve.open("dbs/cluster2resolution")
    clusters2headlines = shelve.open("dbs/zclusters2headlines")
    dis2rec = shelve.open("dbs/dis2rec")
    cluster2ents = shelve.open("dbs/cluster2ents")#
    cluster2allents = shelve.open("dbs/cluster2allents")
    tmpshelve = shelve.open("dbs/tmpshelve")

    import time
    print("Topic summarization begins: " + time.strftime("%H:%M:%S"))
    ts = topic_summarization(clusters2term, clusters2headlines, cluster2resolution, partitioned_docs, dis2rec)
    tmpshelve['mydict'] = ts
    #ts = tmpshelve['mydict']
    print("Topic summarization ends: " + time.strftime("%H:%M:%S"))
    # collect ent2clusters here to see later whether a entity is only found on one resolution.
    getcluster2allents(cluster2allents, ts, disamb_path='Disambiguated')
    ranked_ents = importance_rank_ents(cluster2allents)
    ent2clusters = mk_ent2clusters(cluster2ents, clusters2term)
    ents = list(ent2clusters.keys())
    date2clu_total = {}
    for ent in ents:
        #print('hh')
        cluster_earlydate_tuples = sorted(get_early_ent_dates(ent, ent2clusters, ts, earliest_date), key=lambda x: x[1])
        earlydates = [tuple[1] for tuple in cluster_earlydate_tuples]
        # if the entity is only placed on 1 resolution, then it is not of interest
        if len(set(earlydates)) < 2 or '#' in ent:
            ent2clusters[ent] = []
            continue
        grouped_clu_date_tuples = groupby(cluster_earlydate_tuples, key=lambda x: x[1])
        date2clu_per_ent = {} #
        for grp_tuple in grouped_clu_date_tuples:
            clusters = []
            cluster_tuples = list(grp_tuple[1])
            for cluster_tuple in cluster_tuples:
                clusters.append(cluster_tuple[0])
            date2clu_per_ent[str(grp_tuple[0])] = clusters
            date2clu_total.setdefault(str(grp_tuple[0]), [])
            date2clu_total[str(grp_tuple[0])].extend(clusters)
        true_ent_name = find_true_ent(ent)
        if true_ent_name == '*wfrederikshavn':
            print('fount')
        split_ent2clusters = split_ent(true_ent_name, clusters2term, date2clu_per_ent)
        #split_ent2clusters = minimize_lines(true_ent_name, split_ent2clusters, cluster_earlydate_tuples)
        split_ent2clusters = minimize_lines_totally(true_ent_name, split_ent2clusters, cluster_earlydate_tuples)
        del ent2clusters[ent]
        repopulate_ent2clusters(ent2clusters, split_ent2clusters)
    #b
    limit_ents_to_l_per_clu(ent2clusters, ts, dis2rec, l=4)
    ent2clusters = limit_clus_per_date_to_l(ent2clusters, cluster2allents, date2clu_total, ranked_ents, l=3)
    ent2clusters = minimize_lines_again(ent2clusters, ts)
    for ent in ent2clusters:
        for cluster in ent2clusters[ent]:
            append(cluster2ents, cluster, ent)


    create_javadoc(cluster2ents, ts, clusters2term)

def minimize_lines_again(ent2clusters, ts):#after deleting some lines it is possible to minize these even more (This is kind of a hacky solution. An overall minimization can be done at this point rather than doing the current two-step solution)
    split_ents = set([ent.split('#')[0] for ent in ent2clusters if '#' in ent])
    return_ent2clusters = {ent: ent2clusters[ent] for ent in [ent2 for ent2 in ent2clusters if '#' not in ent2] }
    for ent in split_ents:
        split_ent2clusters = {split_ent: ent2clusters[split_ent] for split_ent in [ent2 for ent2 in ent2clusters if ent + '#' in ent2 or ent == ent2] }
        fullent2clusters = {}
        for split_ent in split_ent2clusters:
            fullent2clusters.setdefault(split_ent.split('#')[0], [])
            fullent2clusters[split_ent.split('#')[0]].extend(split_ent2clusters[split_ent])
        cluster_earlydate_tuples = sorted(get_early_ent_dates(ent, fullent2clusters, ts, earliest_date), key=lambda x: x[1])
        earlydates = [tuple[1] for tuple in cluster_earlydate_tuples]
        if len(set(earlydates)) < 2:
            continue
        split_ent2clusters = minimize_lines_totally(ent, split_ent2clusters, cluster_earlydate_tuples)
        for split_ent in split_ent2clusters:
            return_ent2clusters[split_ent] = split_ent2clusters[split_ent]
    return return_ent2clusters


def limit_clus_per_date_to_l(ent2clusters, cluster2allents, date2clu_total, ranked_ents, l=4):
    #First convert from ent2clusters to clusters2ent
    cluster2ents = reverse_dict(ent2clusters)

    clu2score = {}
    ranked_clusters = []
    for date in date2clu_total.keys():
        curr_dateClusters = set(cluster2ents.keys()).intersection(date2clu_total[date]) #This is done because the clusters in date2clu might have been removed by this point in timeline creation. (cluster2ents holds the newest updated clusters)
        if len(curr_dateClusters) > l:
            for cluster in curr_dateClusters:
                score = 0
                for ent in cluster2allents[cluster]:
                    if ent in list(ranked_ents[:10]): #We score clusters only if it contains ents in top 10 ents
                        score += 1
                clu2score[cluster] = score
            ranked_clusters.extend(sorted(curr_dateClusters, key=lambda x: clu2score[x], reverse=True)[:l])
        else:
            ranked_clusters.extend(curr_dateClusters)
    return_cluster2ents = {}
    for cluster in cluster2ents:
        if cluster in ranked_clusters:
            return_cluster2ents[cluster] = cluster2ents[cluster]
        else:
            return_cluster2ents[cluster] = []

    non_deleteables =[] #this is solely for collecting those with # in the dataset
    #convert back to ent2clusters
    return_ent2clusters = {}
    for cluster in return_cluster2ents:
        for ent in return_cluster2ents[cluster]:
            if '#' in ent and ent.split('#')[0] not in non_deleteables:
                non_deleteables.append(ent.split('#')[0])
            return_ent2clusters.setdefault(ent, [])
            append(return_ent2clusters, ent, cluster)
    #Remove entities which are not connected to anything other than 1 cluster
    for ent in return_ent2clusters:
        if ent.split('#')[0] in non_deleteables and ent.split('#')[0] in return_ent2clusters: #just so we dont remove those with # that seems to only have one cluster
            continue
        if len(return_ent2clusters[ent]) == 1:
            return_ent2clusters[ent] = []
    return return_ent2clusters

def importance_rank_ents(cluster2allents):
    allents = []
    for ents in cluster2allents.values():
        allents.extend(ents)
    from collections import Counter
    c = Counter(allents)
    ranked_ents = sorted(list(c.keys()), key=lambda x: c[x], reverse=True)
    return ranked_ents



def getcluster2allents(cluster2allents, ts, disamb_path):
    for cluster in ts:
        if len(ts[cluster]) == 0:
            continue
        filename = ts[cluster][0][2]
        rec_disamb_pairs = get_rec_disamb_pairs(filename, disamb_path)
        cluster2allents.setdefault(cluster, [])
        for rec_disamb_pair in rec_disamb_pairs:
            if rec_disamb_pair[1].lower() == 'none':
                ent_to_append = '*r' + rec_disamb_pair[0].lower()
            else:
                ent_to_append = rec_disamb_pair[1].lower().replace('w.', '*w')
            append(cluster2allents, cluster, ent_to_append)

def find_true_ent(ent):
    if len(ent.split('*r')) <= 2: #if ent='w.hej du':1, if ent='r.hej du':2
        return ent
    return '*r' + ent.split('*r')[1]

def minimize_lines(ent, split_ent2clusters, cluster_earlydate_tuples):
    return_split_ent2clusters = {}
    cluster_date_dic = {}
    skippable_splits = []
    for tuple in cluster_earlydate_tuples:
        cluster_date_dic[tuple[0]] = tuple[1]

    split_ent_clus_tuples = sorted(list(split_ent2clusters.items()), key=lambda x: int(x[0].split('#')[1]) if len(x[0].split('#')) == 2 else 0)
    counter = 0
    for i in range(0, len(split_ent_clus_tuples)):
        split_ent1, clus1 = split_ent_clus_tuples[i]
        dates1 = list([cluster_date_dic[clu] for clu in clus1])
        if split_ent1 not in skippable_splits:
            if counter == 0:
                return_split_ent2clusters[ent] = list(clus1)
            else:
                return_split_ent2clusters[ent + '#' + str(counter)] = list(clus1)
            skippable_splits.append(split_ent1)
            for j in range(i + 1, len(split_ent_clus_tuples)):
                split_ent2, clus2 = split_ent_clus_tuples[j]
                if split_ent2 not in skippable_splits:
                    dates2 = list([cluster_date_dic[clu] for clu in clus2])
                    if all(map(lambda x: latererdate_pred(x, dates1), dates2)): #if all clus2 are a later date than all of clus1
                        if counter == 0:
                            return_split_ent2clusters[ent].extend(clus2)
                        else:
                            return_split_ent2clusters[ent + '#' + str(counter)].extend(clus2)
                        skippable_splits.append(split_ent2)
                        dates1.extend(dates2)
            counter += 1
    return return_split_ent2clusters

def minimize_lines_totally(ent, split_ent2clusters, cluster_earlydate_tuples):
    return_split_ent2clusters = {}
    cluster_date_dic = {}
    skippable_splits = []
    for tuple in cluster_earlydate_tuples:
        cluster_date_dic[tuple[0]] = tuple[1]

    split_ent_clus_tuples = sorted(list(split_ent2clusters.items()), key=lambda x: int(x[0].split('#')[1]) if len(x[0].split('#')) == 2 else 0)
    counter = 0
    for i in range(0, len(split_ent_clus_tuples)):
        split_ent1, clus1 = split_ent_clus_tuples[i]
        dates1 = list([cluster_date_dic[clu] for clu in clus1])
        if split_ent1 not in skippable_splits:
            if counter == 0:
                return_split_ent2clusters[ent] = list(clus1)
            else:
                return_split_ent2clusters[ent + '#' + str(counter)] = list(clus1)
            skippable_splits.append(split_ent1)
            for j in range(i + 1, len(split_ent_clus_tuples)):
                split_ent2, clus2 = split_ent_clus_tuples[j]
                if split_ent2 not in skippable_splits:
                    dates2 = list([cluster_date_dic[clu] for clu in clus2])
                    if all(map(lambda x: x not in dates1, dates2)): #if all clus2-dates are not in clus1-dates
                        if counter == 0:
                            return_split_ent2clusters[ent].extend(clus2)
                        else:
                            return_split_ent2clusters[ent + '#' + str(counter)].extend(clus2)
                        skippable_splits.append(split_ent2)
                        dates1.extend(dates2)
            counter += 1
    return return_split_ent2clusters

def latererdate_pred(x, dates):
    for date in dates:
        if int(x) <= int(date):
            return False
    return True

def repopulate_ent2clusters(ent2clusters, split_ent2clusters):
    for ent in split_ent2clusters.keys():
        ent2clusters[ent] = split_ent2clusters[ent]


def limit_ents_to_l_per_clu(ent2clusters, ts, dis2rec, l=5):
    ent2ts_score = create_ent2tsscore(ent2clusters, ts, dis2rec)
    newclusters2ent = {}
    for ent in ent2clusters:
        for cluster in ent2clusters[ent]:
            newclusters2ent.setdefault(cluster, [])
            newclusters2ent[cluster].append(ent)
    tmpent2clus = {}
    for cluster in newclusters2ent:
        try:
            newclusters2ent[cluster] = sorted(newclusters2ent[cluster], key=lambda x: ent2ts_score[x.split('#')[0]], reverse=True)[:l]
        except:
            print('dsg')#
        for ent in newclusters2ent[cluster]:
            tmpent2clus.setdefault(ent, [])
            tmpent2clus[ent].append(cluster)

    for ent in tmpent2clus:
        ent2clusters[ent] = tmpent2clus[ent]

def create_ent2tsscore(ent2clusters, ts, dis2rec):#
    ent2ts_score = {}
    for ent in ent2clusters.keys():
        if ent in dis2rec:
            for cluster in ent2clusters[ent]:
                for rec in dis2rec[ent]:
                    scores = [score_sent[0] for score_sent in ts[cluster] if rec[2:] in score_sent[1].lower().replace(',','').replace('(','').replace(')','').replace(':','').replace('.','').split(' ')]
                    ent2ts_score.setdefault(ent, 0)
                    ent2ts_score[ent] += np.sum(scores)#
        else:
            for cluster in ent2clusters[ent]:
                scores = [score_sent[0] for score_sent in ts[cluster] if ent[2:] in score_sent[1].lower().replace(',','').replace('(','').replace(')','').replace(':','').replace('.','').split(' ')]
                ent2ts_score.setdefault(ent, 0)
                ent2ts_score[ent] += np.sum(scores)
    return ent2ts_score

def get_early_ent_dates(ent, ent2clusters, ts, earliest_date):
    if earliest_date:
        top_5_triples_per_cluster = [(i, ts[i]) for i in ent2clusters[ent]]
        early_ent_dates = []
        for value in top_5_triples_per_cluster:
            clusterid = value[0]
            top_5_triples = value[1]
            top_5_triples.sort(key=lambda x: x[2].split('_')[-2])
            early_ent_dates.append((clusterid, top_5_triples[0][2].split('_')[-2]))
        return early_ent_dates
    else:
        #print(str(ent2clusters[ent]))
        top_5_triples_per_cluster = [(i, ts[i]) for i in ent2clusters[ent] if len(ts[i]) > 0]
        best_ent_dates = []
        for value in top_5_triples_per_cluster:
            clusterid = value[0]
            #print(str(value))
            #l
            best_ent_dates.append((clusterid, value[1][0][2].split('_')[-2]))
        return best_ent_dates

# this split clusters on the same entity on the same date as well as coupling later clusters to correct split_ent
def split_ent(ent, clusters2term, date2clu_per_ent, threshold = 0.30):
    sorted_date = sorted(list(date2clu_per_ent.keys()))
    cand_tfidfs, cluster2tfidx, tfidx2cluster = create_vectors(clusters2term, date2clu_per_ent, sorted_date)
    similarities = cosine_similarity(cand_tfidfs)
    similar_indicies = np.array(np.nonzero(similarities > threshold))
    split_ent2clusters = {}
    split_cluster2ent = {}
    primary_cluster = '' #this is the first cluster associated with the ents without #
    # startup runthrough of first date to initialize start-ents
    candidate_counter = 0
    for cluster in date2clu_per_ent[sorted_date[0]]:
        if candidate_counter == 0:
            #candidate2terms[ent] = clusters2term[cluster]
            split_ent2clusters.setdefault(ent, [])
            split_ent2clusters[ent].append(cluster)
            split_cluster2ent[cluster] = ent
            primary_cluster = cluster
        else:
            new_ent = ent + '#' + str(candidate_counter)
            #candidate2terms[new_ent] = clusters2term[cluster]
            split_ent2clusters.setdefault(new_ent, [])
            split_ent2clusters[new_ent].append(cluster)
            split_cluster2ent[cluster] = new_ent
        candidate_counter += 1

    # runthrough of rest of dates
    for date in sorted_date[1:]:
        curr_date_clus = []
        for cluster in date2clu_per_ent[date]:
            cluster_indices = np.argwhere(similar_indicies==cluster2tfidx[cluster])
            releant_indices = []
            for tuple in cluster_indices:
                if tuple[0] == 0:
                    releant_indices.append(tuple[1])
            best_similarity_val = 0
            best_tfidf_idx = -1
            for i in releant_indices:
                tfidf_idx = similar_indicies[1, i]
                if similar_indicies[0, i] == similar_indicies[1, i]:
                    continue
                similarity_val = similarities[cluster2tfidx[cluster], tfidf_idx]
                if similarity_val > best_similarity_val:
                    best_similarity_val = similarity_val
                    best_tfidf_idx = tfidf_idx
            if best_tfidf_idx == -1:
                similar_cluster = primary_cluster  #since not even one is above threshold, this will force it to the main entity line (without #)
            else:
                similar_cluster = str(tfidx2cluster[str(best_tfidf_idx)])
            if similar_cluster in split_cluster2ent.keys():
                if similar_cluster in curr_date_clus:
                    candidate_counter = add_alternative(candidate_counter, cluster, ent, split_cluster2ent,
                                           split_ent2clusters)
                    continue
                split_cluster2ent[cluster] = split_cluster2ent[similar_cluster]
                split_ent2clusters[split_cluster2ent[similar_cluster]].append(cluster)
            elif cluster not in split_cluster2ent.keys():
                candidate_counter = add_alternative(candidate_counter, cluster, ent, split_cluster2ent,
                                                    split_ent2clusters)
            if similar_cluster == primary_cluster:
                curr_date_clus.append(primary_cluster)
            curr_date_clus.append(cluster)
    return split_ent2clusters


def add_alternative(candidate_counter, cluster, ent, split_cluster2ent, split_ent2clusters):
    new_ent = ent + '#' + str(candidate_counter)
    split_cluster2ent[cluster] = new_ent
    split_ent2clusters.setdefault(new_ent, [])
    split_ent2clusters[new_ent].append(cluster)
    candidate_counter += 1
    return candidate_counter


def create_vectors(clusters2term, date2clu, sorted_date):
    candidate_representations = []
    cluster2tfidx = {}
    tfidx2cluster = {}
    counter = 0
    for date in sorted_date:
        for cluster in date2clu[date]:
            candidate_representations.append(collapse_to_string([tuple[0] for tuple in clusters2term[cluster]]))
            cluster2tfidx[str(cluster)] = counter
            tfidx2cluster[str(counter)] = cluster
            counter += 1
    vectorizer = TfidfVectorizer()
    X_train = vectorizer.fit_transform(candidate_representations)
    return X_train, cluster2tfidx, tfidx2cluster

def mk_ent2clusters(cluster2ents, clusters2term):
    ent2clusters = {}
    for i in clusters2term.keys():
        cluster2ents.setdefault(i, [])
        clusterterms = clusters2term[i]
        sorted_clusterterms = sorted(clusterterms, key=lambda tup: tup[1], reverse=True)
        ent_counter = 0
        for termtuple in sorted_clusterterms:
            if (termtuple[0][:2] == '*w' or termtuple[0][:2] == '*r'):
                ent2clusters.setdefault(termtuple[0], [])
                if i not in ent2clusters[termtuple[0]]:
                    ent2clusters[termtuple[0]].append(i)
                    ent_counter += 1
    #print(str(ent2clusters))
    return ent2clusters

def cluster2entsfix(sorted_clusters, cluster2ents):
    ents2clusters = reverse_dict(cluster2ents)
    ents = []
    for cluster in sorted_clusters:
        for ent in cluster2ents[cluster]:
            if ent not in ents:
                ents.append(ent)
                if ent + '#1' in ents:
                    tmp = ents2clusters[ent + '#1']
                    ents2clusters[ent + '#1'] = ents2clusters[ent]
                    ents2clusters[ent] = tmp
                elif ent + '#2' in ents:
                    tmp = ents2clusters[ent + '#2']
                    ents2clusters[ent + '#2'] = ents2clusters[ent]
                    ents2clusters[ent] = tmp
                elif ent + '#3' in ents:
                    tmp = ents2clusters[ent + '#3']
                    ents2clusters[ent + '#3'] = ents2clusters[ent]
                    ents2clusters[ent] = tmp
                elif ent + '#4' in ents:
                    tmp = ents2clusters[ent + '#4']
                    ents2clusters[ent + '#4'] = ents2clusters[ent]
                    ents2clusters[ent] = tmp
                elif ent + '#5' in ents:
                    tmp = ents2clusters[ent + '#5']
                    ents2clusters[ent + '#5'] = ents2clusters[ent]
                    ents2clusters[ent] = tmp
                elif ent + '#6' in ents:
                    tmp = ents2clusters[ent + '#6']
                    ents2clusters[ent + '#6'] = ents2clusters[ent]
                    ents2clusters[ent] = tmp
                elif ent + '#7' in ents:
                    tmp = ents2clusters[ent + '#7']
                    ents2clusters[ent + '#7'] = ents2clusters[ent]
                    ents2clusters[ent] = tmp
                elif ent + '#8' in ents:
                    tmp = ents2clusters[ent + '#8']
                    ents2clusters[ent + '#8'] = ents2clusters[ent]
                    ents2clusters[ent] = tmp
                elif ent + '#9' in ents:
                    tmp = ents2clusters[ent + '#9']
                    ents2clusters[ent + '#9'] = ents2clusters[ent]
                    ents2clusters[ent] = tmp
    return reverse_dict(ents2clusters)

def create_javadoc(cluster2ents, ts, clusters2term):
    f = open('/home/duper/Documents/NewsClustering/GUI/src/com/company/1.txt', 'w')
    count_list = []
    for cluster in cluster2ents.keys():
        if len(cluster2ents[cluster]) > 0:
            count_list.append(cluster)
    f.write(str(len(count_list)) + '\n')
    #sorted_clusters = sort_clusters_by_date(ts)
    clusters = [cluster for cluster in list(ts.keys()) if len(ts[cluster]) > 0]
    sorted_clusters = sorted(clusters, key=lambda x: best_date_of_top_5_triples(ts[x]))
    cluster2ents = cluster2entsfix(sorted_clusters, cluster2ents)
    save_sorted = shelve.open('permdbs/final_clusters')
    save_sorted[example_run] = [cluster for cluster in list(set(sorted_clusters).intersection(list(cluster2ents.keys()))) if len(cluster2ents[cluster]) > 0]
    for i in sorted_clusters:
        if i not in cluster2ents or len(cluster2ents[i]) == 0:
            continue
        #f.write(str(len(ts[i]) + 3) + '\n') #num summaries
        clusternr_string = str(i)
        if clusters2term[i][0][1] != -1:
            clusternr_string += '*' #show that cluster origins from multiple documents
        full_summary = 'clusternr: ' + clusternr_string + '\n'
        counter = 1
        for summary in ts[i]:
            if counter > 3:
                break
            # if len(summary) == 4:
            #     full_summary += str(counter) + ': ' + summary[2].split('_')[-2] + ' ' + '[' + str(summary[0]) + ', ' + summary[2].split('_')[-1] + ', ' + summary[1].replace('\n', '') + ', ' + summary[3] + ']\n'#summary[1] + '\n'
            # else:
            #     full_summary += str(counter) + ': ' + summary[2].split('_')[-2] + ' ' + '[' + str(summary[0]) + ', ' + summary[2].split('_')[-1] + ', ' + summary[1].replace('\n', '') + ']\n'
            if len(summary) == 4:
                full_summary += str(counter) + ': ' + summary[1].replace('\n', '') + '\n'#summary[1] + '\n'
            else:
                full_summary += str(counter) + ': ' + summary[1].replace('\n', '') + '\n'
            counter += 1
        cluster_words = [term[0] for term in list(clusters2term[i]) if term[0][:2] != '*f']
        fcluster_words = [term[0] for term in list(clusters2term[i]) if term[0][:2] == '*f']
        #full_summary += str(cluster_words) + '\n'
        #full_summary += str(fcluster_words) + '\n'
        #counter += 2
        f.write(str(counter) + '\n')
        f.write(full_summary)
        cdate = best_date_of_top_5_triples(ts[str(i)])
        f.write(str(cdate[0:4]) + '\n')
        f.write(str(cdate[4:6]) + '\n')
        f.write(str(cdate[6:8]) + '\n')
        ents = list(set(cluster2ents[i]))
        f.write(str(len(ents)) + '\n')
        for ent in ents:
            f.write(ent[2:] + '\n')
    f.close()

def early_date_of_top_5_triples(top_5_triples):
    top_5_triples.sort(key=lambda x: x[2].split('_')[-2])
    return top_5_triples[0][2].split('_')[-2]
def best_date_of_top_5_triples(top_5_triples):
    return top_5_triples[0][2].split('_')[-2]

def reverse_dict(ones2twos):
    twos2ones = {}
    for one in ones2twos:
        for two in ones2twos[one]:
            twos2ones.setdefault(two, [])
            append(twos2ones, two, one)
    return twos2ones

def append(dic, key, val):
    tmp = dic[key]
    tmp.append(val)
    dic[key] = tmp
if __name__ == "__main__":
    run2()