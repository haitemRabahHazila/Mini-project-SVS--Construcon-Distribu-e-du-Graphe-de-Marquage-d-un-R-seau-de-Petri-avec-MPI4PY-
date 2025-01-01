from mpi4py import MPI
import hashlib
import json
import networkx as nx
import matplotlib.pyplot as plt
from pybloom_live import BloomFilter

# Initialize MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# Function to hash a marking
def hash_marking(marking):
    marking_str = json.dumps(marking, sort_keys=True)
    hashed_value = int(hashlib.sha256(marking_str.encode()).hexdigest(), 16)
    site = hashed_value % size
    return site

# Function to check if a transition is enabled
def is_enabled(transition, marking):
    for place, tokens in transition['input'].items():
        if marking.get(place, 0) < tokens:
            return False
    return True

# Function to fire a transition
def fire_transition(transition, marking):
    new_marking = marking.copy()
    for place, tokens in transition['input'].items():
        new_marking[place] -= tokens
    for place, tokens in transition['output'].items():
        new_marking[place] = new_marking.get(place, 0) + tokens
    return new_marking

# Function to explore a marking
def explore_marking(marking):
    new_markings = []
    for transition_name, transition in transitions.items():
        if is_enabled(transition, marking):
            new_marking = fire_transition(transition, marking)
            new_markings.append((new_marking, transition_name))
    return new_markings

# Function to visualize the marking graph
def visualize_marking_graph(graph):
    pos = nx.spring_layout(graph)
    plt.figure(figsize=(8, 6))
    nx.draw_networkx_nodes(graph, pos, node_size=2000, node_color='lightblue')
    nx.draw_networkx_edges(graph, pos, arrowstyle='->', arrowsize=20, edge_color='gray')
    edge_labels = nx.get_edge_attributes(graph, 'label')
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels, font_color='red')
    node_labels = {node: dict(node) for node in graph.nodes()}
    nx.draw_networkx_labels(graph, pos, labels=node_labels, font_size=12, font_color='black')
    plt.title("Global Marking Graph of the Petri Net")
    plt.axis('off')
    plt.show()

# Main logic
if rank == 0:
    # Interface utilisateur
    initial_marking = {'p1': 1, 'p2': 0}
    transitions = {
        't1': {'input': {'p1': 1}, 'output': {'p2': 1}},
        't2': {'input': {'p2': 1}, 'output': {'p1': 1}}
    }
    
    # Envoyer les transitions à tous les sites
    transitions = comm.bcast(transitions, root=0)
    
    # Root site initializes the process
    target_site = hash_marking(initial_marking)
    if target_site == 0:
        markings_to_explore = [initial_marking]
    else:
        comm.send(initial_marking, dest=target_site)
        markings_to_explore = []
else:
    # Recevoir les transitions du site 0
    transitions = comm.bcast(None, root=0)
    
    # Other sites wait for exploration requests
    markings_to_explore = []
    marking = comm.recv(source=MPI.ANY_SOURCE)
    markings_to_explore.append(marking)

# Bloom Filter pour stocker les marquages explorés
bloom_filter = BloomFilter(capacity=1000000, error_rate=0.0001)

# Local storage for explored markings and edges
local_graph = nx.DiGraph()

# Limite de profondeur d'exploration
max_depth = 10
current_depth = 0

# Explore markings
while markings_to_explore and current_depth < max_depth:
    current_marking = markings_to_explore.pop()
    current_depth += 1
    marking_key = tuple(sorted(current_marking.items()))
    if marking_key not in bloom_filter:
        bloom_filter.add(marking_key)
        local_graph.add_node(marking_key, marking=current_marking)
        new_markings = explore_marking(current_marking)
        for new_marking, transition_name in new_markings:
            new_marking_key = tuple(sorted(new_marking.items()))
            local_graph.add_edge(marking_key, new_marking_key, label=transition_name)
            target_site = hash_marking(new_marking)
            if target_site == rank:
                markings_to_explore.append(new_marking)
            else:
                comm.send(new_marking, dest=target_site)

# Gather all local graphs at the root site
all_graphs = comm.gather(local_graph, root=0)

if rank == 0:
    # Merge all local graphs to construct the global marking graph
    global_graph = nx.DiGraph()
    for graph in all_graphs:
        global_graph.update(graph.nodes(data=True), graph.edges(data=True))

    # Visualize the global marking graph
    visualize_marking_graph(global_graph)