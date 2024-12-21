# # # mpiexec -n 4 python distributed_petri_net.py
# # # "C:\Program Files\Microsoft MPI\Bin\mpiexec.exe" -n 4 python distributed_petri_net.py
 
["P1", "P2", "P3"]
{
    "T1": {"input": {"P1": 1}, "output": {"P2": 1}},
    "T2": {"input": {"P2": 1}, "output": {"P3": 1}},
    "T3": {"input": {"P2": 1}, "output": {"P3": 1}},
    "T4": {"input": {"P3": 1}, "output": {"P1": 1}}
}
{"P1": 3, "P2": 0, "P3": 0}


# # class PetriNet:
# #     def __init__(self, places, transitions, initial_marking):
# #         """
# #         Initialize the Petri Net.
# #         :param places: List of place names.
# #         :param transitions: List of transitions. Each transition is a dict with 'input' and 'output'.
# #         :param initial_marking: List of initial tokens in each place.
# #         """
# #         self.places = places
# #         self.transitions = transitions
# #         self.initial_marking = initial_marking

# #     def fire_transition(self, marking, transition):
# #         """
# #         Fire a transition if possible.
# #         :param marking: Current marking.
# #         :param transition: Transition to fire.
# #         :return: New marking or None if the transition is not enabled.
# #         """
# #         input_places = transition['input']
# #         output_places = transition['output']
# #         new_marking = marking[:]

# #         # Check if the transition is enabled
# #         for place, tokens in input_places.items():
# #             index = self.places.index(place)
# #             if new_marking[index] < tokens:
# #                 return None

# #         # Update tokens for input and output places
# #         for place, tokens in input_places.items():
# #             index = self.places.index(place)
# #             new_marking[index] -= tokens

# #         for place, tokens in output_places.items():
# #             index = self.places.index(place)
# #             new_marking[index] += tokens

# #         return new_marking



# # def hash_function(marking, num_nodes):
# #     """
# #     Hash a marking to determine the responsible node.
# #     :param marking: Current marking.
# #     :param num_nodes: Total number of nodes.
# #     :return: Node index responsible for the marking.
# #     """
# #     return hash(str(marking)) % num_nodes



# # from mpi4py import MPI

# # def explore_marking(marking, petri_net):
# #     """
# #     Explore reachable markings from a given marking.
# #     :param marking: Current marking.
# #     :param petri_net: Petri Net object.
# #     :return: List of new markings.
# #     """
# #     reachable_markings = []
# #     for transition in petri_net.transitions:
# #         new_marking = petri_net.fire_transition(marking, transition)
# #         if new_marking:
# #             reachable_markings.append(new_marking)
# #     return reachable_markings

# # def distributed_exploration(petri_net):
# #     """
# #     Distributed computation of the marking graph.
# #     :param petri_net: Petri Net object.
# #     """
# #     comm = MPI.COMM_WORLD
# #     rank = comm.Get_rank()
# #     size = comm.Get_size()

# #     if rank == 0:
# #         # Initial marking
# #         initial_marking = petri_net.initial_marking
# #         target_node = hash_function(initial_marking, size)
# #         comm.send(initial_marking, dest=target_node)
# #         print(f"Site 0 sent initial marking {initial_marking} to site {target_node}")

# #     explored_markings = set()
# #     while True:
# #         if rank != 0:
# #             # Receive a marking to explore
# #             marking = comm.recv(source=MPI.ANY_SOURCE)
# #             if marking == "DONE":
# #                 break

# #             if tuple(marking) not in explored_markings:
# #                 explored_markings.add(tuple(marking))
# #                 new_markings = explore_marking(marking, petri_net)
# #                 for new_marking in new_markings:
# #                     target_node = hash_function(new_marking, size)
# #                     comm.send(new_marking, dest=target_node)

# #         else:
# #             # Send "DONE" signal to all nodes
# #             for i in range(1, size):
# #                 comm.send("DONE", dest=i)
# #             break

# #     # Collect results
# #     if rank != 0:
# #         comm.send(list(explored_markings), dest=0)
# #     else:
# #         marking_graph = set()
# #         for i in range(1, size):
# #             partial_results = comm.recv(source=i)
# #             marking_graph.update(partial_results)
# #         print("Final Marking Graph:", marking_graph)



# from mpi4py import MPI

# class PetriNet:
#     def __init__(self, places, transitions, initial_marking):
#         self.places = places
#         self.transitions = transitions
#         self.initial_marking = initial_marking

#     def fire_transition(self, marking, transition):
#         input_places = transition['input']
#         output_places = transition['output']
#         new_marking = marking[:]

#         # Check if the transition is enabled
#         for place, tokens in input_places.items():
#             index = self.places.index(place)
#             if new_marking[index] < tokens:
#                 return None

#         # Update tokens for input and output places
#         for place, tokens in input_places.items():
#             index = self.places.index(place)
#             new_marking[index] -= tokens

#         for place, tokens in output_places.items():
#             index = self.places.index(place)
#             new_marking[index] += tokens

#         return new_marking

# def hash_function(marking, num_nodes):
#     return hash(str(marking)) % num_nodes

# def explore_marking(marking, petri_net):
#     reachable_markings = []
#     for transition in petri_net.transitions:
#         new_marking = petri_net.fire_transition(marking, transition)
#         if new_marking:
#             reachable_markings.append(new_marking)
#     return reachable_markings

# def distributed_exploration(petri_net):
#     comm = MPI.COMM_WORLD
#     rank = comm.Get_rank()
#     size = comm.Get_size()

#     if rank == 0:
#         initial_marking = petri_net.initial_marking
#         target_node = hash_function(initial_marking, size)
#         comm.send(initial_marking, dest=target_node)
#         print(f"Site 0 sent initial marking {initial_marking} to site {target_node}")

#     explored_markings = set()
#     while True:
#         if rank != 0:
#             marking = comm.recv(source=MPI.ANY_SOURCE)
#             if marking == "DONE":
#                 break

#             if tuple(marking) not in explored_markings:
#                 explored_markings.add(tuple(marking))
#                 new_markings = explore_marking(marking, petri_net)
#                 for new_marking in new_markings:
#                     target_node = hash_function(new_marking, size)
#                     comm.send(new_marking, dest=target_node)

#         else:
#             for i in range(1, size):
#                 comm.send("DONE", dest=i)
#             break

#     if rank != 0:
#         comm.send(list(explored_markings), dest=0)
#     else:
#         marking_graph = set()
#         for i in range(1, size):
#             partial_results = comm.recv(source=i)
#             marking_graph.update(partial_results)
#         print("Final Marking Graph:", marking_graph)

# # Example usage with a simple Petri Net
# if __name__ == "__main__":
#     # Example Petri Net definition
#     places = ['p1', 'p2']
#     transitions = [
#         {'input': {'p1': 1}, 'output': {'p2': 1}},
#         {'input': {'p2': 1}, 'output': {'p1': 1}}
#     ]
#     initial_marking = [1, 0]

#     petri_net = PetriNet(places, transitions, initial_marking)
#     distributed_exploration(petri_net)



from mpi4py import MPI

class PetriNet:
    def __init__(self, places, transitions, initial_marking):
        self.places = places
        self.transitions = transitions
        self.initial_marking = initial_marking

    def fire_transition(self, marking, transition):
        input_places = transition['input']
        output_places = transition['output']
        new_marking = marking[:]

        # Check if the transition is enabled
        for place, tokens in input_places.items():
            index = self.places.index(place)
            if new_marking[index] < tokens:
                return None

        # Update tokens for input and output places
        for place, tokens in input_places.items():
            index = self.places.index(place)
            new_marking[index] -= tokens

        for place, tokens in output_places.items():
            index = self.places.index(place)
            new_marking[index] += tokens

        return new_marking

def hash_function(marking, num_nodes):
    return hash(str(marking)) % num_nodes

def explore_marking(marking, petri_net):
    reachable_markings = []
    for transition in petri_net.transitions:
        new_marking = petri_net.fire_transition(marking, transition)
        if new_marking:
            reachable_markings.append(new_marking)
    return reachable_markings

def distributed_exploration(petri_net):
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    if rank == 0:
        initial_marking = petri_net.initial_marking
        target_node = hash_function(initial_marking, size)
        comm.send(initial_marking, dest=target_node)
        print(f"Site 0 sent initial marking {initial_marking} to site {target_node}")

    explored_markings = set()
    while True:
        if rank != 0:
            marking = comm.recv(source=MPI.ANY_SOURCE)
            if marking == "DONE":
                break

            if tuple(marking) not in explored_markings:
                explored_markings.add(tuple(marking))
                print(f"Process {rank} exploring marking: {marking}")
                new_markings = explore_marking(marking, petri_net)
                print(f"Process {rank} found new markings: {new_markings}")

                for new_marking in new_markings:
                    target_node = hash_function(new_marking, size)
                    print(f"Process {rank} sending new marking {new_marking} to site {target_node}")
                    comm.send(new_marking, dest=target_node)

        else:
            for i in range(1, size):
                comm.send("DONE", dest=i)
            break

    if rank != 0:
        comm.send(list(explored_markings), dest=0)
    else:
        marking_graph = set()
        for i in range(1, size):
            partial_results = comm.recv(source=i)
            marking_graph.update(partial_results)
        print("Final Marking Graph:", marking_graph)

# Example Petri Net definition
if __name__ == "__main__":
    places = ['p1', 'p2']
    transitions = [
        {'input': {'p1': 1}, 'output': {'p2': 1}},  # Transition 1 (p1 -> p2)
        {'input': {'p2': 1}, 'output': {'p1': 1}}   # Transition 2 (p2 -> p1)
    ]
    initial_marking = [1, 0]

    petri_net = PetriNet(places, transitions, initial_marking)
    distributed_exploration(petri_net)

