from typing import Generator, Set, Dict, Iterable, Tuple, List
import json

class Graph:
    nodes : Set[int]
    edges : Dict[int, Set[int]]

    def __init__(self, nodes : Iterable[int], edges : Iterable[Tuple[int, int]]) -> None:
        self.nodes = set(nodes)
        self.edges = {node : set() for node in nodes}
        for (u_node, v_node) in edges:
            if u_node == v_node:
                continue

            self.edges[u_node].add(v_node)
            self.edges[v_node].add(u_node)
    
    def __str__(self) -> str:
        return self.nodes.__str__() + self.edges.__str__()
    
    def get_edge_count(self) -> int:
        return sum([len(neighbours) for (_, neighbours) in self.edges.items()]) // 2

def read_graph_from_json(json_file_path : str) -> Graph:
    with open(json_file_path, 'r') as f:
        read_graph = json.load(f)

    return Graph(read_graph['nodes'], read_graph['edges'])

def get_number_of_isolated_vertices(graph : Graph) -> int:
    return sum(1 for neighborhood in graph.edges.values() if len(neighborhood) == 0)

def bfs_explore(graph : Graph, node : int) -> Graph:
    g = Graph([], [])
    queue = [node]
    g.nodes = set(queue)
    g.edges = {node : graph.edges[node]}

    while queue:
        current_node = queue.pop(0)
        node_neighbours = graph.edges[current_node]
        g.edges[current_node] = node_neighbours
        for node in node_neighbours:
            if node in g.nodes:
                continue
            queue.append(node)
            g.nodes.add(node)

    return g


def bfs_is_connected(graph : Graph, node : int) -> bool:
    visited : Set[int] = set()
    queue = [node]

    while queue:
        current_node = queue.pop(0)
        node_neighbours = graph.edges[current_node]
        for node in node_neighbours:
            if node in visited:
                return False
            queue.append(node)
            visited.add(node)

    return True

def decompose(graph : Graph) -> Generator[Graph, None, None]:
    visited = set()

    for node in graph.nodes:
        if node in visited:
            continue

        component = bfs_explore(graph, node)
        visited = visited.union(component.nodes)
        yield component


def get_connection_matrix(graph : Graph) -> Tuple[Dict[int, int], List[List[bool]]]:
    number_of_nodes = len(graph.nodes)

    returned_dictionary = dict()
    connection_matrix = [[False] * number_of_nodes] * number_of_nodes

    for index, node in enumerate(graph.nodes):
        returned_dictionary[node] = index
        for neighbour_node in graph.edges[node]:
            if neighbour_node not in returned_dictionary:
                continue

            neighbour_index = returned_dictionary[neighbour_node]
            connection_matrix[index][neighbour_index] = connection_matrix[neighbour_index][index] = True

    return returned_dictionary, connection_matrix

def is_acyclic_connected(graph : Graph) -> bool:
    for i in graph.nodes:
        return bfs_is_connected(graph, i)
    
    return True


def is_acyclic(graph : Graph) -> bool:
    print("here")
    return all(is_acyclic_connected(component) for component in decompose(graph))

def print_edges(graph : Graph, simplify=False):
    def number_generator() -> Generator[int, None, None]:
        x = 0
        while (True):
            x += 1
            yield x

    sequence_generator = number_generator()
    translate = dict()

    def get_or_add(x : int) -> int:
        if x not in translate.keys():
            translate[x] = next(sequence_generator)
        return translate[x]

    for vertex, neighbours in graph.edges.items():
        translated_vertex = get_or_add(vertex) if simplify else vertex
        for neighbor in neighbours:
            translated_neighbor = get_or_add(neighbor) if simplify else neighbor
            if translated_vertex < translated_neighbor:
                print(translated_vertex, translated_neighbor)
    

