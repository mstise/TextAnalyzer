import networkx as nx
import copy
# from NamedEntityDisambiguator.Construct_mention_entity import construct_ME_graph
# from datetime import datetime


# Calculates the weighted degrees for all non taboo nodes in the graph
def non_taboo_weighted_degree_calculations(graph):
    non_taboo_degrees = []
    for n in graph.nodes():
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
    for n in graph.nodes():
        degree = 0
        for neighbor in graph.neighbors(n):
            degree += graph.get_edge_data(n, neighbor)['weight']
        if degree != 0:
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
    print("Graph mentions:")
    for node in graph.nodes():
        if not graph.node[node]["entity"]:
            print("    " + graph.node[node]["key"])
    print("Graph entities:")
    for node in graph.nodes():
        if graph.node[node]["entity"]:
            print("    " + graph.node[node]["key"])

    result_list = []
    for node in graph.nodes():
        if len(graph.neighbors(node)) == 0:
            result_list.append([graph.node[node]["key"], None])
            graph.remove_node(node)

    # closest_entities = []
    # mentions = 0
    # # Pre processing
    # # print('pre-processing started at: ' + str(datetime.now()))
    # for n in graph.nodes():
    #     if graph.node[n]["entity"]:
    #         temp_closest = []
    #         for x in graph.nodes():
    #             if not graph.node[x]["entity"]:
    #                 # Calculate distance to all mentions
    #                 if nx.has_path(graph, n, x):
    #                     temp_closest.append([n, x, nx.dijkstra_path_length(graph, n, x)])
    #         distance = 0
    #         for x in temp_closest:
    #             distance += x[2]*x[2]
    #         closest_entities.append([n, distance])
    #     else:
    #         mentions += 1
    # # Keep the closest 5
    # closest_entities.sort(key=lambda x: x[1])
    # for node in closest_entities[:-(mentions * 2)]:
    #     graph.remove_node(node[0])


        
    # # Test
    # import warnings
    # import matplotlib.pyplot as plt
    # warnings.filterwarnings("ignore")
    # node_labels = {}
    # counter = 0
    # for node in graph.nodes():
    #     if graph.node[node]["entity"]:
    #         node_labels[counter] = ("ENTITY: " + graph.node[node]['key'])
    #     else:
    #         node_labels[counter] = ("MENTION: " + graph.node[node]['key'])
    #     counter += 1
    #
    # nx.draw(graph, nx.circular_layout(graph))
    # nx.draw_networkx_labels(graph, nx.circular_layout(graph), node_labels)
    # nx.draw_networkx_edge_labels(G, nx.circular_layout(graph))
    # plt.axis('off')
    # plt.show()



    # Main loop
    # print('main loop started at: ' + str(datetime.now()))
    solution = copy.deepcopy(graph)
    min_degree = weighted_degree_calculations(graph)[0][1]
    # Determine taboo entity nodes
    for n in graph.nodes():
        if not graph.node[n]["entity"] and len(graph.neighbors(n)) == 1 and not graph.node[graph.neighbors(n)[0]]["taboo"]:
            graph.node[graph.neighbors(n)[0]]["taboo"] = True
    while len([node for node in graph.node if graph.node[node]["entity"] and not graph.node[node]["taboo"]]) != 0:
        # Remove lowest weighted degree non taboo
        # print('removed a node at: ' + str(datetime.now()))
        graph.remove_node(non_taboo_weighted_degree_calculations(graph)[0][0])
        # Determine taboo entity nodes
        for n in graph.nodes():
            if not graph.node[n]["entity"] and len(graph.neighbors(n)) == 1 and not graph.node[graph.neighbors(n)[0]]["taboo"]:
                graph.node[graph.neighbors(n)[0]]["taboo"] = True
        # Check if minimum weighted degree increased
        new_min_degree = weighted_degree_calculations(graph)[0][1]
        if new_min_degree > min_degree:
            min_degree = new_min_degree
            solution = copy.deepcopy(graph)
    # Post-processing phase
    # print('post-processing started at: ' + str(datetime.now()))

    for node in solution.nodes():
        if len(solution.neighbors(node)) == 0:
            result_list.append([solution.node[node]["key"], None])
            #print("mention not found")
    for node in solution.nodes():
        if not solution.node[node]["entity"]:
            if len(solution.neighbors(node)) > 0:
                edges = solution.edges(node)
                max_weight = 0
                max_edge = None
                for edge in edges:
                    weight = solution[edge[0]][edge[1]]["weight"]
                    if weight > max_weight:
                        max_weight = weight
                        max_edge = edge
                result_list.append([solution.node[max_edge[0]]["key"], solution.node[max_edge[1]]["key"]])
                #print("mention disambiguated")

    # result_degree, result_graph = min_degree_for_all_solutions(solution)
    # for edge in result_graph.edge:
    #     if not graph.node[edge]["entity"]:
    #         if len(result_graph.neighbors(edge)) > 0:
    #             result_list.append([result_graph.node[edge]["key"], result_graph.node[result_graph.neighbors(edge)[0]]["key"]])
    result_list.sort(key=lambda x: x[0])

    # print("this is graph AFTER: ")
    # for node in solution.nodes():
    #     print(str(solution.node[node]["key"]))

    return result_list

# import time

# start = time.time()
# G = construct_ME_graph()
# mid = time.time()
# test = graph_disambiguation_algorithm(G)
# end = time.time()
# print(mid-start)
# print(end-mid)
# G = nx.Graph()
# G.add_node(0, key='anders fogh rasmussen', entity=False, taboo=False)
# G.add_node(1, key='anders fogh rasmussen', entity=True, taboo=False)
# G.add_node(2, key=':no:anders fogh rasmussen', entity=True, taboo=False)
# G.add_node(3, key='anders fogh rasmussen#rådgiver for den ukrainske præsident', entity=True, taboo=False)
# G.add_node(4, key='ritt bjerregaard', entity=False, taboo=False)
# G.add_node(5, key='ritt bjerregaard', entity=True, taboo=False)
# G.add_node(6, key='i have no neighbors', entity=False, taboo=False)
# G.add_edge(1, 0, weight=4.210)
# G.add_edge(2, 0, weight=0.001)
# G.add_edge(3, 0, weight=0.001)
# G.add_edge(5, 4, weight=1.078)
# G.add_edge(1, 5, weight=0.068)
# import matplotlib.pyplot as plt
# node_labels = {}
# counter = 0
# for node in G.nodes():
#     if G.node[node]["entity"]:
#         node_labels[counter] = ("ENTITY: " + G.node[node]['key'])
#     else:
#         node_labels[counter] = ("MENTION: " + G.node[node]['key'])
#     counter += 1
# nx.draw(G, nx.circular_layout(G))
# nx.draw_networkx_labels(G, nx.circular_layout(G), node_labels, font_size=16)
# plt.axis('off')
# plt.show()
# graph_disambiguation_algorithm(copy.deepcopy(G))
