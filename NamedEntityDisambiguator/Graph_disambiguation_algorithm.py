import networkx as nx
import copy
#from NamedEntityDisambiguator.Construct_mention_entity import construct_ME_graph


# Calculates the weighted degrees for all non taboo nodes in the graph
def non_taboo_weighted_degree_calculations(graph):
    non_taboo_degrees = []
    for n in graph.nodes_iter():
        if graph.node[n]["entity"] and not graph.node[n]["taboo"]:
            degree = 0
            for neighbor in graph.neighbors(n):
                degree += graph.get_edge_data(n, neighbor)['weight']
            non_taboo_degrees.append([n, degree])
    if len(non_taboo_degrees) > 0:
        return sorted(non_taboo_degrees, key=lambda node: node[1])
    else: return [[0, 0]]


# Calculates the weighted degrees for all nodes in the graph
def weighted_degree_calculations(graph):
    degrees = []
    for n in graph.nodes_iter():
        degree = 0
        for neighbor in graph.neighbors(n):
            degree += graph.get_edge_data(n, neighbor)['weight']
        degrees.append([n, degree])
    if len(degrees) > 0:
        return sorted(degrees, key=lambda node: node[1])
    else: return [[0, 0]]


def min_degree_for_all_solutions(graph):
    min_degree = 0
    min_degree_graph = None
    remaining_nodes = [node for node in graph.node if graph.node[node]["entity"] and not graph.node[node]["taboo"]]
    if len(remaining_nodes) == 0:
        min_degree = weighted_degree_calculations(graph)[0][1]
        min_degree_graph = copy.deepcopy(graph)
    else:
        for edge in remaining_nodes:
            new_graph = copy.deepcopy(graph)
            new_graph.remove_node(edge)
            new_min_degree, new_min_graph = min_degree_for_all_solutions(new_graph)
            if min_degree < new_min_degree:
                min_degree = new_min_degree
                min_degree_graph = new_min_graph
    return min_degree, min_degree_graph


def graph_disambiguation_algorithm(graph):
    closest_entities = []
    mentions = 0
    # Pre processing
    for n in graph.nodes_iter():
        if graph.node[n]["entity"]:
            temp_closest = []
            for x in graph.nodes_iter():
                if not graph.node[x]["entity"]:
                    # Calculate distance to all mentions
                    temp_closest.append([n, x, nx.dijkstra_path_length(graph, n, x)])
            distance = 0
            for x in temp_closest:
                distance += x[2]*x[2]
            closest_entities.append([n, distance])
        else:
            mentions += 1
    # Keep the closest 5
    closest_entities.sort(key=lambda x: x[1])
    for node in closest_entities[:-(mentions * 5)]:
        graph.remove_node(node[0])
    # Main loop
    solution = copy.deepcopy(graph)
    min_degree = weighted_degree_calculations(graph)[0][1]
    # Determine taboo entity nodes
    for n in graph.nodes_iter():
        if not graph.node[n]["entity"] and len(graph.neighbors(n)) == 1 and not graph.node[graph.neighbors(n)[0]]["taboo"]:
            graph.node[graph.neighbors(n)[0]]["taboo"] = True
    while len([node for node in graph.node if graph.node[node]["entity"] and not graph.node[node]["taboo"]]) != 0:
        # Remove lowest weighted degree non taboo
        graph.remove_node(non_taboo_weighted_degree_calculations(graph)[0][0])
        # Determine taboo entity nodes
        for n in graph.nodes_iter():
            if not graph.node[n]["entity"] and len(graph.neighbors(n)) == 1 and not graph.node[graph.neighbors(n)[0]]["taboo"]:
                graph.node[graph.neighbors(n)[0]]["taboo"] = True
        # Check if minimum weighted degree increased
        new_min_degree = weighted_degree_calculations(graph)[0][1]
        if new_min_degree > min_degree:
            min_degree = new_min_degree
            solution = copy.deepcopy(graph)
    # Post-processing phase
    result_degree, result_graph = min_degree_for_all_solutions(solution)
    result_list = []
    for edge in result_graph.edge:
        if not graph.node[edge]["entity"]:
            result_list.append([edge, result_graph.neighbors(edge)[0]])
    return result_list

import time

#start = time.time()
#G = construct_ME_graph()
#mid = time.time()
#test = graph_disambiguation_algorithm(G)
#end = time.time()
#print(mid-start)
#print(end-mid)
G = nx.Graph()
G.add_node(0, key='anders fogh rasmussen', entity=False, taboo=False)
G.add_node(1, key='anders fogh rasmussen', entity=True, taboo=False)
G.add_node(2, key=':no:anders fogh rasmussen', entity=True, taboo=False)
G.add_node(3, key='anders fogh rasmussen#rådgiver for den ukrainske præsident', entity=True, taboo=False)
G.add_node(4, key='ritt bjerregaard', entity=False, taboo=False)
G.add_node(5, key='ritt bjerregaard', entity=True, taboo=False)
G.add_edge(1, 0, weight=4.210)
G.add_edge(2, 0, weight=0.001)
G.add_edge(3, 0, weight=0.001)
G.add_edge(5, 4, weight=1.078)
G.add_edge(1, 5, weight=0.068)
var = graph_disambiguation_algorithm(G)
print(var)
print("Hello world!")
