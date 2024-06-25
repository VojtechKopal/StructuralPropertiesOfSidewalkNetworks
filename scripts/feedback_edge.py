from graph import Graph, read_graph_from_json, decompose
import sys

def find_feedback_edge_set_number(graph : Graph) -> int:
    return graph.get_edge_count() - len(graph.nodes) + 1

if __name__ == '__main__':
    assert len(sys.argv) == 2
    file_path = sys.argv[1]
    graph = read_graph_from_json(file_path)
    print(f"{file_path} has FESN = {sum(find_feedback_edge_set_number(component) for component in decompose(graph))}")
