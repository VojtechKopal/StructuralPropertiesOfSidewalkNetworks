import gurobipy as gp
import networkx as nx
import sys
from typing import Generator, List
from graph import Graph, print_edges, read_graph_from_json

def find_all_cycles_in_graph(graph : Graph, cycle_bound : int) -> Generator[List[int], None, None]:
    networkx_graph = nx.Graph()
    networkx_graph.add_edges_from((key, value) for key, values in graph.edges.items() for value in values)

    return nx.simple_cycles(networkx_graph, length_bound=cycle_bound)

def find_feedback_vertex_set_number(graph : Graph, cycle_bound : int) -> int:
    cycles_of_graph = find_all_cycles_in_graph(graph, cycle_bound)
    # I am basically converting the NP-C problem of finding feedback vertex set number to NP-C problem of finding minimal hitting set

    model = gp.Model("Feedback vertex set number")
    vars = dict()
    for node in graph.nodes:
        vars[node] = model.addVar(vtype=gp.GRB.BINARY, name=f"Removal of node {node}")
    
    model.setObjective(gp.quicksum(vars[node] for node in graph.nodes), gp.GRB.MINIMIZE)
    for cycle in cycles_of_graph:
        if len(cycle) < 3:
            continue
        model.addConstr(gp.quicksum(vars[node] for node in cycle) >= 1)
    model.setParam('OutputFlag', True)
    model.optimize()

    return int(model.ObjVal)

if __name__ == '__main__':
    # assert len(sys.argv) == 2
    # file_path = sys.argv[1]
    # graph = read_graph_from_json("D:\\Bachelor\\grenoble_france.json")
    # print(f"p tw {len(graph.nodes)} {graph.get_edge_count()}")
    # print_edges(graph, True)
    #print(f"{file_path} with cycle_bound = {cycle_bound} has FVSN = {find_feedback_vertex_set_number(graph, cycle_bound)}")
    graph = Graph([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], [(1, 2), (2, 3), (3, 4), (4, 5), (5, 1), (1, 6), (2, 7), (3, 8), (4, 9), (5, 10), (6, 8), (8, 10), (10, 7), (7, 9), (9, 6)])
    print(find_feedback_vertex_set_number(graph, None))