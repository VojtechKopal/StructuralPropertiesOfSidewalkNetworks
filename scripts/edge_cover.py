import gurobipy as gp
from typing import Dict, Tuple
from graph import Graph, read_graph_from_json
import sys

def find_edge_cover_number(graph : Graph) -> int:
    model = gp.Model("Edge cover number")
    vars : Dict[Tuple[int, int], gp.Var] = dict()
    ctr = 0
    for [vertex, neighbours] in graph.edges.items():
        if not neighbours:
            ctr += 1
            print(f"ctr: {ctr}")
            continue
        for neighbour in neighbours:
            if ((vertex, neighbour) in vars):
                continue
            edge_variable = model.addVar(vtype=gp.GRB.BINARY, name=f"Edge set contains edge {vertex} -- {neighbour}")
            vars[(vertex, neighbour)] = edge_variable
            vars[(neighbour, vertex)] = edge_variable
        model.addConstr(gp.quicksum(vars[(vertex, neighbour)] for neighbour in neighbours) >= 1)

    print(model.NumConstrs)        
    model.setObjective(gp.quicksum(var for key, var in vars.items() if key[0] <= key[1]), gp.GRB.MINIMIZE)
    model.setParam('OutputFlag', False)
    model.optimize()

    # for [edge, var] in vars.items():
    #     if (edge[0] < edge[1]):
    #         print(f"${edge} : ${var.X}")

    return int(model.ObjVal)

if __name__ == '__main__':
    assert len(sys.argv) == 2
    file_path = sys.argv[1]
    graph = read_graph_from_json(file_path)
    print(f"{file_path} has ECN = {find_edge_cover_number(graph)}")
    #graph = Graph([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], [(1, 2), (2, 3), (3, 4), (4, 5), (5, 1), (1, 6), (2, 7), (3, 8), (4, 9), (5, 10), (6, 8), (8, 10), (10, 7), (7, 9), (9, 6)])
    #print(find_edge_cover_number(graph))