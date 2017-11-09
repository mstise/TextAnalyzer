import networkx as nx
import copy


# Calculates the weighted degrees for all nodes in the graph
def weighted_degree_calculations(graph):
    non_taboo_degrees = []
    for n in graph.nodes_iter():
        if not graph.node[n]["entity"] and not graph.node[n]["taboo"]:
            degree = 0
            for neighbor in graph.neighbors(n):
                degree += graph.get_edge_data(n, neighbor)['weight']
            non_taboo_degrees.append([n, degree])
    return sorted(non_taboo_degrees, key=lambda node: node[1])


def min_degree_for_all_solutions(graph):
    min_degree = 0
    min_degree_graph = None
    remaining_nodes = [node for node in graph.node if not graph.node[node]["entity"]
                       and not graph.node[node]["taboo"]]
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
    # Pre processing
    for n in graph.nodes_iter():
        if graph.node[n]["entity"]:
            temp_closest = []
            for x in graph.nodes_iter():
                if not graph.node[x]["entity"]:
                    # Calculate distance to all mentions
                    temp_closest.append([n, x, nx.dijkstra_path_length(graph, n, x)])
            temp_closest = sorted(temp_closest, key=lambda node: node[2], reverse=True)
            # Keep the closest 5
            closest_entities.append(temp_closest[:5])
    # Main loop
    solution = copy.deepcopy(graph)
    min_degree = weighted_degree_calculations(graph)[0][1]
    # Determine taboo entity nodes
    for n in graph.nodes_iter():
        if graph.node[n]["entity"] and len(graph.neighbors(n)) == 1 and not graph.node[graph.neighbors(n)[0]]["taboo"]:
            graph.node[graph.neighbors(n)[0]]["taboo"] = True
    while len([node for node in graph.node if not graph.node[node]["entity"]
               and not graph.node[node]["taboo"]]) != 0:
        # Remove lowest weighted degree
        graph.remove_node(weighted_degree_calculations(graph)[0][0])
        # Check if minimum weighted degree increased
        new_min_degree = weighted_degree_calculations(graph)[0][1]
        if new_min_degree > min_degree:
            min_degree = new_min_degree
            solution = copy.deepcopy(graph)
        # Determine taboo entity nodes
        for n in graph.nodes_iter():
            if graph.node[n]["entity"] and len(graph.neighbors(n)) == 1\
                    and not graph.node[graph.neighbors(n)[0]]["taboo"]:
                graph.node[graph.neighbors(n)[0]]["taboo"] = True
    # Post-processing phase
    result_degree, result_graph = min_degree_for_all_solutions(solution)


G = nx.Graph()
G.add_node(1, key='entity_name1', entity=True, taboo=False)
G.add_node(2, key='entity_name2', entity=False, taboo=False)
G.add_node(3, key='entity_name3', entity=False, taboo=False)
G.add_node(4, key='entity_name4', entity=False, taboo=False)
G.add_node(5, key='entity_name5', entity=False, taboo=False)
G.add_edge(1, 2, weight=0.5)
G.add_edge(1, 3, weight=0.6)
G.add_edge(1, 4, weight=0.7)
G.add_edge(1, 5, weight=0.8)
G.add_edge(2, 3, weight=0.7)
G.add_edge(2, 4, weight=0.7)
G.add_edge(3, 4, weight=0.7)
graph_disambiguation_algorithm(G)
