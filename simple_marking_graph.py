from mpi4py import MPI

# Initialize MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# Example initial marking and transitions
initial_marking = {
    'p1': 1,
    'p2': 0,
    'p3': 0,
    'p4': 0
}
transitions = {
    't1': {
        'input': {'p1': 1},
        'output': {'p2': 1}
    },
    't2': {
        'input': {'p2': 1},
        'output': {'p3': 1}
    },
    't3': {
        'input': {'p3': 2},
        'output': {'p4': 1}
    }
}
# initial_marking = {
#     'p1': 1,
#     'p2': 1,
#     'p3': 0,
#     'p4': 0
# }
# transitions = {
#     't1': {
#         'input': {'p1': 1},
#         'output': {'p3': 1}
#     },
#     't2': {
#         'input': {'p2': 1},
#         'output': {'p3': 1}
#     },
#     't3': {
#         'input': {'p3': 2},
#         'output': {'p4': 1}
#     }
# }

# Function to hash a marking and determine the responsible site
def hash_marking(marking):
    print("hash, the marking is: ", marking)
    marking_str = str(sorted(marking.items()))
    hashed_value = hash(marking_str)
    site = hashed_value % size
    print("the site is: ", site)
    return site

# Function to check if a transition is enabled
def is_enabled(transition, marking):
    print("is_enabled")
    for place, tokens in transition['input'].items():
        if marking.get(place, 0) < tokens:
            print("is_enabled false")
            return False
    print("is_enabled true")
    return True

# Function to fire a transition
def fire_transition(transition, marking):
    print("fire_transition")
    new_marking = marking.copy()
    for place, tokens in transition['input'].items():
        new_marking[place] -= tokens
    for place, tokens in transition['output'].items():
        new_marking[place] = new_marking.get(place, 0) + tokens
    return new_marking

# Function to explore a marking
def explore_marking(marking):
    print("explore_marking")
    new_markings = []
    for transition_name, transition in transitions.items():
        if is_enabled(transition, marking):
            new_marking = fire_transition(transition, marking)
            new_markings.append((new_marking, transition_name))
    return new_markings

# Main logic
if rank == 0:
    # Root site initializes the process
    target_site = hash_marking(initial_marking)
    if target_site == 0:
        markings_to_explore = [initial_marking]
    else:
        comm.send(initial_marking, dest=target_site)
        markings_to_explore = []
else:
    # Other sites wait for exploration requests
    markings_to_explore = []
    marking = comm.recv(source=MPI.ANY_SOURCE)
    if marking is not None:  # Check for termination signal
        markings_to_explore.append(marking)

# Local storage for explored markings and transitions
explored_markings = set()
graph_edges = []  # Pour stocker les transitions entre les marquages

# Limit exploration depth
max_depth = 10
current_depth = 0

# Explore markings
while markings_to_explore and current_depth < max_depth:
    print("while")
    current_marking = markings_to_explore.pop()
    current_depth += 1
    marking_key = tuple(sorted(current_marking.items()))
    if marking_key not in explored_markings:
        explored_markings.add(marking_key)
        new_markings = explore_marking(current_marking)
        for new_marking, transition_name in new_markings:
            target_site = hash_marking(new_marking)
            if target_site == rank:
                markings_to_explore.append(new_marking)
            else:
                comm.send(new_marking, dest=target_site)
            # Enregistrer la transition
            graph_edges.append((marking_key, tuple(sorted(new_marking.items())), transition_name))

# Send termination signal to all processes
if rank == 0:
    for i in range(1, size):
        comm.send(None, dest=i)

# Gather all explored markings and edges at the root site
all_markings = comm.gather(explored_markings, root=0)
all_edges = comm.gather(graph_edges, root=0)

if rank == 0:
    # Merge all markings to construct the global marking graph
    global_markings = set()
    for markings in all_markings:
        global_markings.update(markings)

    # Merge all edges to construct the global graph edges
    global_edges = []
    for edges in all_edges:
        global_edges.extend(edges)

    # Assign unique IDs to markings
    marking_to_id = {marking: f"M{i}" for i, marking in enumerate(sorted(global_markings))}

    # Print the global marking graph
    print("Global Marking Graph:")
    for edge in global_edges:
        source, target, transition = edge
        print(f"{marking_to_id[source]} --({transition})--> {marking_to_id[target]}")

    # Print the values of each node
    print("\nValues of each node:")
    for marking, marking_id in marking_to_id.items():
        print(f"{marking_id}: {dict(marking)}")