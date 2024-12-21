import tkinter as tk
from tkinter import ttk, messagebox
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches  # Import to use custom shapes for nodes


# Function to create the marking graph
def create_marking_graph():
    try:
        # Retrieve user input
        places = eval(places_entry.get())  # Ensure it's a list
        if not isinstance(places, list):
            raise ValueError("Places must be entered as a Python list, e.g., ['P1', 'P2', 'P3'].")

        initial_marking = eval(initial_marking_entry.get())  # Ensure it's a dictionary
        if not isinstance(initial_marking, dict):
            raise ValueError("Initial marking must be entered as a Python dictionary, e.g., {'P1': 3, 'P2': 0, 'P3': 0}.")

        transitions = eval(transitions_entry.get())  # Ensure it's a dictionary
        if not isinstance(transitions, dict):
            raise ValueError("Transitions must be entered as a Python dictionary.")

        # Validation
        if not all(place in places for place in initial_marking.keys()):
            raise ValueError("All places in the initial marking must match the defined places.")

        # Function to explore markings
        def explore_marking(current_marking):
            new_markings = []
            for t, rule in transitions.items():
                if all(current_marking.get(place, 0) >= rule["input"].get(place, 0) for place in rule["input"]):
                    new_marking = current_marking.copy()
                    for place, value in rule["input"].items():
                        new_marking[place] -= value
                    for place, value in rule["output"].items():
                        new_marking[place] = new_marking.get(place, 0) + value
                    new_markings.append(new_marking)
            return new_markings

        # Build the marking graph
        graph = nx.DiGraph()  # Directed graph for the marking graph
        markings_to_explore = [initial_marking]
        explored_markings = set()

        while markings_to_explore:
            marking = markings_to_explore.pop()
            marking_tuple = tuple(sorted(marking.items()))
            if marking_tuple in explored_markings:
                continue

            explored_markings.add(marking_tuple)
            graph.add_node(str(marking))
            new_markings = explore_marking(marking)
            for new_marking in new_markings:
                graph.add_edge(str(marking), str(new_marking))
                markings_to_explore.append(new_marking)

        # Display the marking graph
        plt.figure(figsize=(10, 7))
        pos = nx.spring_layout(graph)
        nx.draw(graph, pos, with_labels=True, node_color='lightblue', node_size=3000, font_size=10, font_weight='bold')
        plt.title("Marking Graph", fontsize=16)
        plt.show()

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")


# Function to draw the Petri Net (RDP)
def draw_petri_net():
    try:
        # Retrieve user input
        places = eval(places_entry.get())  # Ensure it's a list
        if not isinstance(places, list):
            raise ValueError("Places must be entered as a Python list, e.g., ['P1', 'P2', 'P3'].")

        transitions = eval(transitions_entry.get())  # Ensure it's a dictionary
        if not isinstance(transitions, dict):
            raise ValueError("Transitions must be entered as a Python dictionary.")

        # Build the Petri Net graph
        petri_net = nx.DiGraph()  # Directed graph for the Petri Net (RDP)

        # Add places and transitions as nodes
        for place in places:
            petri_net.add_node(place, shape='circle', color='lightblue')
        for transition in transitions:
            petri_net.add_node(transition, shape='rect', color='black')  # Rectangular (black) transitions

        # Add edges based on transitions (directed)
        for transition, rule in transitions.items():
            # Input arcs (places -> transition) are directed
            for place, value in rule.get("input", {}).items():
                petri_net.add_edge(place, transition, weight=value)
            
            # Output arcs (transition -> places) are directed
            for place, value in rule.get("output", {}).items():
                petri_net.add_edge(transition, place, weight=value)

        # Draw the Petri Net
        plt.figure(figsize=(10, 7))
        pos = nx.spring_layout(petri_net)

        # Draw places (circle nodes)
        nx.draw_networkx_nodes(petri_net, pos, nodelist=[n for n in petri_net if petri_net.nodes[n]['shape'] == 'circle'],
                               node_color='lightblue', node_size=3000, label="Places")
        
        # Draw transitions (rectangular nodes with specific width: 0.3 * height)
        for transition in [n for n in petri_net if petri_net.nodes[n]['shape'] == 'rect']:
            x, y = pos[transition]
            height = 0.2  # Adjust the height as desired
            width = 0.3 * height  # Set the width to 0.3 of the height
            rectangle = mpatches.Rectangle((x - width / 2, y - height / 2), width=width, height=height, color='black', lw=1)  # Add custom rectangle shape
            plt.gca().add_patch(rectangle)

        # Draw edges (arcs) with arrows
        nx.draw_networkx_edges(petri_net, pos, connectionstyle="arc3,rad=0.2", width=2, arrowsize=20)
        
        # Draw labels for places and transitions
        nx.draw_networkx_labels(petri_net, pos, font_size=10, font_weight="bold")
        
        # Title and legend
        plt.title("Petri Net (RDP)", fontsize=16)
        plt.legend(loc="best")
        
        # Display the plot
        plt.show()

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")


# Create the GUI
root = tk.Tk()
root.title("Petri Net and Marking Graph Constructor")

# Places input
tk.Label(root, text="Places (Python list):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
places_entry = tk.Entry(root, width=50)
places_entry.grid(row=0, column=1, padx=5, pady=5)

# Transitions input
tk.Label(root, text="Transitions (Python dict):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
transitions_entry = tk.Entry(root, width=50)
transitions_entry.grid(row=1, column=1, padx=5, pady=5)

# Initial marking input
tk.Label(root, text="Initial Marking (Python dict):").grid(row=2, column=0, sticky="w", padx=5, pady=5)
initial_marking_entry = tk.Entry(root, width=50)
initial_marking_entry.grid(row=2, column=1, padx=5, pady=5)

# Buttons to create the graphs
marking_button = ttk.Button(root, text="Generate Marking Graph", command=create_marking_graph)
marking_button.grid(row=3, column=0, pady=10)

petri_net_button = ttk.Button(root, text="Generate Petri Net (RDP)", command=draw_petri_net)
petri_net_button.grid(row=3, column=1, pady=10)

# Run the GUI
root.mainloop()
