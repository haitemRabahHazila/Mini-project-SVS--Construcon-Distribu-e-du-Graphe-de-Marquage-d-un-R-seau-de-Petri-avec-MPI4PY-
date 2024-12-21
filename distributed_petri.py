import tkinter as tk
from tkinter import ttk, messagebox
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

class PetriNetGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Petri Net Marking Graph Generator")

        self.places = []  # List to store dynamic places
        self.transitions = {}  # Dictionary to store dynamic transitions
        self.initial_marking = {}  # Dictionary to store initial marking

        # Create input fields
        self.create_input_widgets()

    def create_input_widgets(self):
        # Places input
        tk.Label(self.root, text="Places (comma-separated):").pack(pady=5)
        self.places_entry = tk.Entry(self.root, width=50)
        self.places_entry.pack(pady=5)
        self.places_entry.insert(0, "P1,P2,P3")  # Default values

        # Initial marking input
        tk.Label(self.root, text="Initial Marking (format: P1:2,P2:0,P3:0):").pack(pady=5)
        self.marking_entry = tk.Entry(self.root, width=50)
        self.marking_entry.pack(pady=5)
        self.marking_entry.insert(0, "P1:2,P2:0,P3:0")  # Default values

        # Button to add transitions dynamically
        ttk.Button(self.root, text="Add Transition", command=self.add_transition_widgets).pack(pady=10)

        # Button to generate the marking graph and Petri Net
        ttk.Button(self.root, text="Generate Marking Graph", command=self.create_marking_graph).pack(pady=10)
        ttk.Button(self.root, text="Show Petri Net", command=self.draw_petri_net).pack(pady=10)

    def add_transition_widgets(self):
        """Dynamically add transition input fields."""
        transition_frame = ttk.LabelFrame(self.root, text=f"Transition T{len(self.transitions) + 1}")
        transition_frame.pack(pady=10, padx=10, fill="x")

        # Input and output for the new transition
        t_input_label = tk.Label(transition_frame, text=f"T{len(self.transitions) + 1} Input (format: P1:1):")
        t_input_label.pack()
        t_input_entry = tk.Entry(transition_frame, width=50)
        t_input_entry.pack()
        t_input_entry.insert(0, f"P1:1")  # Default value for input

        t_output_label = tk.Label(transition_frame, text=f"T{len(self.transitions) + 1} Output (format: P2:1):")
        t_output_label.pack()
        t_output_entry = tk.Entry(transition_frame, width=50)
        t_output_entry.pack()
        t_output_entry.insert(0, f"P2:1")  # Default value for output

        # Add transition data to the transitions dictionary
        self.transitions[f"T{len(self.transitions) + 1}"] = {
            "input": t_input_entry,
            "output": t_output_entry
        }

    def parse_marking(self, marking_str):
        marking = {}
        for item in marking_str.split(','):
            if ':' in item:
                place, tokens = item.split(':')
                marking[place.strip()] = int(tokens)
        return marking

    def get_petri_net_data(self):
        try:
            # Parse places
            self.places = [p.strip() for p in self.places_entry.get().split(',')]
            
            # Parse initial marking
            self.initial_marking = self.parse_marking(self.marking_entry.get())
            
            # Parse transitions dynamically
            self.transitions_data = {}
            for t_name, entry_widgets in self.transitions.items():
                self.transitions_data[t_name] = {
                    'input': self.parse_marking(entry_widgets['input'].get()),
                    'output': self.parse_marking(entry_widgets['output'].get())
                }
            
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Invalid input format: {str(e)}")
            return False

    def marking_to_str(self, marking):
        """Convert marking dictionary to a consistent string representation"""
        return str(dict(sorted(marking.items())))

    def create_marking_graph(self):
        if not self.get_petri_net_data():
            return

        def is_enabled(marking, transition_rule):
            """Check if a transition is enabled in the current marking"""
            return all(marking.get(place, 0) >= tokens 
                      for place, tokens in transition_rule["input"].items())

        def fire_transition(marking, transition_rule):
            """Fire a transition and return the new marking"""
            new_marking = marking.copy()
            # Remove input tokens
            for place, tokens in transition_rule["input"].items():
                new_marking[place] -= tokens
            # Add output tokens
            for place, tokens in transition_rule["output"].items():
                new_marking[place] = new_marking.get(place, 0) + tokens
            return new_marking

        # Initialize the graph and tracking structures
        graph = nx.DiGraph()
        to_explore = [self.initial_marking]
        explored = set()

        while to_explore:
            current_marking = to_explore.pop(0)
            current_str = self.marking_to_str(current_marking)
            
            if current_str in explored:
                continue
                
            explored.add(current_str)
            graph.add_node(current_str)
            
            # Try all possible transitions
            for t_name, t_rule in self.transitions_data.items():
                if is_enabled(current_marking, t_rule):
                    new_marking = fire_transition(current_marking, t_rule)
                    new_str = self.marking_to_str(new_marking)
                    
                    # Add new marking to exploration queue if not seen
                    if new_str not in explored:
                        to_explore.append(new_marking)
                    
                    # Add edge to graph
                    graph.add_edge(current_str, new_str, transition=t_name)

        # Visualization
        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(graph, k=1, iterations=50)
        
        # Draw nodes
        nx.draw_networkx_nodes(graph, pos, node_color='lightblue', node_size=3000)
        
        # Draw edges
        nx.draw_networkx_edges(graph, pos, arrows=True, arrowsize=20)
        
        # Draw labels
        nx.draw_networkx_labels(graph, pos, font_size=8)
        
        # Draw edge labels (transitions)
        edge_labels = nx.get_edge_attributes(graph, 'transition')
        nx.draw_networkx_edge_labels(graph, pos, edge_labels, font_size=8)
        
        plt.title("Marking Graph")
        plt.axis('off')
        plt.show()

    def draw_petri_net(self):
        if not self.get_petri_net_data():
            return

        # Create Petri net graph
        petri_net = nx.DiGraph()

        # Add places and transitions
        for place in self.places:
            petri_net.add_node(place, node_type='place')
        for transition in self.transitions_data:
            petri_net.add_node(transition, node_type='transition')

        # Add edges with weights
        for t_name, t_rule in self.transitions_data.items():
            for place, weight in t_rule['input'].items():
                petri_net.add_edge(place, t_name, weight=weight)
            for place, weight in t_rule['output'].items():
                petri_net.add_edge(t_name, place, weight=weight)

        # Draw the Petri net
        plt.figure(figsize=(10, 8))
        pos = nx.spring_layout(petri_net, k=1, iterations=50)

        # Draw places (circles)
        place_nodes = [n for n, attr in petri_net.nodes(data=True) 
                      if attr.get('node_type') == 'place']
        nx.draw_networkx_nodes(petri_net, pos, nodelist=place_nodes,
                             node_color='lightblue', node_shape='o', 
                             node_size=2000)

        # Draw transitions (rectangles)
        trans_nodes = [n for n, attr in petri_net.nodes(data=True) 
                      if attr.get('node_type') == 'transition']
        for t in trans_nodes:
            x, y = pos[t]
            rect = plt.Rectangle((x-0.05, y-0.05), 0.1, 0.1, 
                               color='black')
            plt.gca().add_patch(rect)

        # Draw edges with weights
        edges = petri_net.edges()
        weights = nx.get_edge_attributes(petri_net, 'weight')
        nx.draw_networkx_edges(petri_net, pos, edgelist=edges, width=2)
        nx.draw_networkx_edge_labels(petri_net, pos, edge_labels=weights)

        # Draw node labels
        nx.draw_networkx_labels(petri_net, pos, font_size=12, font_color='black')

        plt.title("Petri Net")
        plt.axis('off')
        plt.show()

# Create the main application window
root = tk.Tk()
app = PetriNetGUI(root)
root.mainloop()
