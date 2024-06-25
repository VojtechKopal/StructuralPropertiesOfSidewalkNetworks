#!/bin/env python3

import argparse as ap
import json
from osmnx import graph_from_place, plot_graph as ox_plot_graph, project_graph
import networkx as nx
import matplotlib.pyplot as plt
from typing import Iterable, Tuple, Dict, Set

class SeparateCircleExeption(Exception):
    def __init__(self, nodes : Set[int], *args: object) -> None:
        super().__init__(*args)
        self.nodes = nodes

    nodes : Set[int]

"""
    Fetches data of sidewalks from place given by place_name
"""
def get_osm_graph(place_name : str) -> nx.MultiDiGraph:
    custom_filters = ['["highway"~"footway|path|steps"]','["foot"~"yes|designated"]']
    graph_parts = [graph_from_place(place_name, network_type='all', retain_all=True, simplify=True, custom_filter=custom_filter) for custom_filter in custom_filters]
    
    return nx.compose_all(graph_parts)

"""
    Converts the complex directioned multigraph from OSM data to simple list of nodes and edges
"""
def extract_nodes_and_edges(graph : nx.MultiDiGraph) -> Tuple[Set[int], Set[Tuple[int, int]]]:
    nodes : Set[int] = {tup[0] for tup in graph.nodes(data=True)}
    edges : Set[Tuple[int, int]] = {(tup[0], tup[1]) for tup in graph.edges(data=True)} | {(tup[1], tup[0]) for tup in graph.edges(data=True)}
    return nodes, edges

"""
    Plots a simple graph given by nodes and edges
"""
def plot_graph(nodes : Iterable[int], edges : Iterable[Tuple[int, int]]):
    graph = nx.Graph()
    graph.add_nodes_from(nodes)
    graph.add_edges_from(edges)
    nx.draw(graph, with_labels=False, node_size=20, node_color='b', edge_color='gray', linewidths=0.3)
    plt.show()

"""
    Visualization of OSM data
""" 
def visualize_osm_data(graph : nx.MultiDiGraph):
    ox_plot_graph(project_graph(graph))
    plt.show()  
  
"""
    Filters nodes of degree two from nodes list, the edge is filtered of edges from or to these nodes
"""  
def filter_degree_two_nodes(nodes : Set[int], edges : Set[Tuple[int, int]]) -> Tuple[Iterable[int], Iterable[Tuple[int, int]]]:
    assert (all(map(lambda x : x >= 0, nodes)))
    new_node_counter = 0
    node_connections : Dict[int, Set[int]] = {node: set() for node in nodes}
    for edge in edges:
        node_connections[edge[0]].add(edge[1])
        node_connections[edge[1]].add(edge[0])

    def deg(node : int) -> int:
        return len(node_connections[node])

    def seek(start : int, current : int) -> Tuple[int, int]:
        if (deg(current) != 2):
            return start, current
        
        visited = set()
        
        previous = start 

        while (deg(current) == 2):
            visited.add(current)
            if (current == start):
                raise SeparateCircleExeption(visited)
            next_node = next((neighbor for neighbor in node_connections[current] if neighbor != previous))
            previous = current
            current = next_node

        return previous, current

    new_nodes : Set[int] = set()
    new_edges : Set[Tuple[int, int]] = set()

    for node in nodes:
        if (deg(node) != 2):
            new_nodes.add(node)
            new_edges.update((node, neighbor) for neighbor in node_connections[node] if neighbor in new_nodes)
            new_edges.update((neighbor, node) for neighbor in node_connections[node] if neighbor in new_nodes)
            continue
        neighbor1, neighbor2 = node_connections[node]
        try: 
            (pred_new_neighbor1, new_neighbor1), (pred_new_neighbor2, new_neighbor2) = seek(node, neighbor1), seek(node, neighbor2)
        except SeparateCircleExeption as e:
            nodes = nodes - e.nodes
            new_node1 = new_node_counter = new_node_counter - 1
            new_node2 = new_node_counter = new_node_counter - 1
            new_nodes.add(new_node1)
            new_nodes.add(new_node2)
            new_edges.add((new_node1, new_node2))
            new_edges.add((new_node2, new_node1))
            continue

        if new_neighbor1 == new_neighbor2:
            new_nodes.add(pred_new_neighbor1)
            new_nodes.add(pred_new_neighbor2)
            new_edges.add((new_neighbor1, pred_new_neighbor1))
            new_edges.add((pred_new_neighbor1, new_neighbor1))
            new_edges.add((new_neighbor1, pred_new_neighbor2))
            new_edges.add((pred_new_neighbor2, new_neighbor1))
            new_edges.add((pred_new_neighbor1, pred_new_neighbor2))
            new_edges.add((pred_new_neighbor2, pred_new_neighbor1))
        elif new_neighbor2 in node_connections[new_neighbor1]:
            new_node = new_node_counter = new_node_counter - 1
            new_nodes.add(new_neighbor1)
            new_nodes.add(new_neighbor2)
            new_nodes.add(new_node)
            new_edges.add((new_neighbor1, new_node))
            new_edges.add((new_node, new_neighbor1))
            new_edges.add((new_neighbor2, new_node))
            new_edges.add((new_node, new_neighbor2))
        else:
            new_nodes.add(new_neighbor1)
            new_nodes.add(new_neighbor2)
            new_edges.add((new_neighbor1, new_neighbor2))
            new_edges.add((new_neighbor2, new_neighbor1))

    return new_nodes, new_edges

"""
    Writes a graph into JSON file
"""
def write_simple_graph_to_file(file_name : str, nodes : Iterable[int], edges : Iterable[Tuple[int, int]]):
    written_object = {
        "nodes" : list(nodes),
        "edges" : list(edges)
    }
    with open(file_name, 'w+') as f:
        json.dump(written_object, f)

def main():
    parser = ap.ArgumentParser(description="Converter of sidewalks to graphs")
    parser.add_argument('--filterDegreeTwo', action='store_true', help='Enable filtering for degree two nodes')
    parser.add_argument('--outputFile', type=str, help='Output file name')
    parser.add_argument('--input', type=str, help='Prompt for OSM')
    parser.add_argument('--visualize', action='store_true', help='Enable plotting the graph')
    parser.add_argument('--visualizeOSM', action='store_true', help='Enable plotting of the actual map')
    
    args = parser.parse_args()
    
    filter_degree_two : bool = args.filterDegreeTwo
    visualize : bool = args.visualize
    visualize_osm : bool = args.visualizeOSM
    input_prompt : str | None = args.input
    output_file : str | None = args.outputFile
    
    place_name = input("Place on planet Earth") if input_prompt is None else input_prompt
    
    osm_graph : nx.MultiDiGraph = get_osm_graph(place_name)
    
    if (visualize_osm):
        visualize_osm_data(osm_graph)

    
    nodes, edges = extract_nodes_and_edges(osm_graph)
    
    if filter_degree_two:
        print("Filtering degree two")
        nodes, edges = filter_degree_two_nodes(nodes, edges)
    
    if (visualize):
        plot_graph(nodes, edges)
        
    if (output_file):
        write_simple_graph_to_file(output_file, nodes, edges)
    

if __name__ == "__main__":
    main()




