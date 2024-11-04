from doctest import TestResults
import sys
import networkx as nx  # type: ignore
from Encoder import Encoder
import matplotlib.pyplot as plt  # type: ignore

# Initialize the encoder
enc = Encoder()

def getFilterNodeList(nodes, start_vertex, end_vertex):
    # Filter nodes based on start and end vertices
    filtered_nodes = [node for node in nodes if node.startswith(start_vertex) or node.startswith(end_vertex)]
    return filtered_nodes

def is_hamiltonian_path(path, nodes):
    # Check if path length is equal to the number of unique nodes
    if len(path) != len(nodes):
        return False
    
    # Check if the path contains all nodes without repetition
    visited = set(path)
    return len(visited) == len(nodes)  # Ensure all nodes are visited

def AssembleNAnneal(graph, nodes, edges, start_vertex, end_vertex):
    latest_path = []  # To store the latest path

    def backtrack(current_path):
        nonlocal latest_path  # Allow modification of latest_path from inner function
        print(f"Current path: {current_path}")  # Debugging line

        if len(current_path) == len(nodes) and current_path[-1] == end_vertex:
            return [current_path[:]]  # Found a Hamiltonian path

        paths = []
        last_node = current_path[-1]

        for neighbor in graph.successors(last_node):
            if neighbor not in current_path:  # Check if not visited
                current_path.append(neighbor)
                paths.extend(backtrack(current_path))  # Recursive call
                current_path.pop()  # Backtrack to explore other paths

        # Update latest_path with the current path if it’s longer
        if len(current_path) > len(latest_path):
            latest_path = current_path[:]

        return paths

    return backtrack([start_vertex]), latest_path  # Return latest_path

class TestResults:
    def __init__(self, nodes, edges, filtered_paths):
        self.nodes = nodes
        self.edges = edges
        self.filtered_paths = filtered_paths

def main():
    file_path = 'Networks/cities.txt'
    graph = nx.DiGraph()

    try:
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                print(f"Processing line: '{line}'")
                parts = line.split()
                if len(parts) == 3:  # Weight provided
                    u, v, w = parts[0], parts[1], parts[2]
                    try:
                        w = float(w)
                    except ValueError:
                        print(f"Error converting weight for line: '{line}'")
                        continue
                    graph.add_edge(u, v, weight=w)
                elif len(parts) == 2:  # No weight provided, set default weight
                    u, v = parts[0], parts[1]
                    graph.add_edge(u, v, weight=1.0)
                else:
                    print(f"Skipping malformed line: {line}")

        print("Graph loaded with edges:", graph.edges(data=True))

        if len(sys.argv) < 4:
            print("Error: Please provide start and end vertices.")
            return exit(1)

        start_vertex = str(sys.argv[2]).upper()
        end_vertex = str(sys.argv[3]).upper()

        nodes = enc.encodeNodes(graph)
        edges = enc.encodeEdges(graph, nodes)  # Add this line to ensure edges are defined

        if start_vertex not in nodes or end_vertex not in nodes:
            print(f"Error: Could not identify start vertex '{start_vertex}' or end vertex '{end_vertex}'")
            return exit(1)

        nx.draw_circular(graph, with_labels=True)
        plt.savefig('graphs/graph.png')
        plt.clf()

        node_names = getFilterNodeList(nodes, start_vertex, end_vertex)

        filtered_paths, latest_path = AssembleNAnneal(graph, nodes, edges, start_vertex, end_vertex)

        results = TestResults(nodes, edges, filtered_paths)

        if results.filtered_paths and is_hamiltonian_path(results.filtered_paths[0], nodes):
            print("\nTHERE IS A HAMILTONIAN PATH " + str(results.filtered_paths[0]))
        else:
            print("\nTHERE IS NOT A HAMILTONIAN PATH:"+ str(latest_path))
            
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
