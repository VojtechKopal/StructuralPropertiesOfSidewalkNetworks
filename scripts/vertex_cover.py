import gurobipy as gp
from typing import Dict
from graph import Graph, read_graph_from_json
import sys

def find_vertex_cover_number(graph : Graph) -> int:
    model = gp.Model("Vertex cover number")
    vars : Dict[int, gp.Var] = dict()
    for [vertex, neighbours] in graph.edges.items():
        vars[vertex] = model.addVar(vtype=gp.GRB.BINARY, name=f"Vertex set contains node {vertex}")
        for neigbour in neighbours:
            if (neigbour not in vars):
                continue
            model.addConstr(vars[vertex] + vars[neigbour] >= 1)
            
    
    model.setObjective(gp.quicksum(vars[node] for node in graph.nodes), gp.GRB.MINIMIZE)
    model.setParam('OutputFlag', False)
    model.optimize()

    for [vertex, var] in vars.items():
       print(f"${vertex} : ${var.X}")

    return int(model.ObjVal)

if __name__ == '__main__':
    # assert len(sys.argv) == 2
    # file_path = sys.argv[1]
    # graph = read_graph_from_json(file_path)
    # print(f"{file_path} has VCN = {find_vertex_cover_number(graph)}")
    graph = Graph([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], [(1, 2), (2, 3), (3, 4), (4, 5), (5, 1), (1, 6), (2, 7), (3, 8), (4, 9), (5, 10), (6, 8), (8, 10), (10, 7), (7, 9), (9, 6)])
    print(find_vertex_cover_number(graph))