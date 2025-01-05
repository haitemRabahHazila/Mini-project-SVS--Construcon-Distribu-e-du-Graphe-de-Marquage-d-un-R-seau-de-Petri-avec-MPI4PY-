#  this is the correct code 

from mpi4py import MPI
# initialisee MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size() # nbr of sites

# Example de marquage initial et les transitions
marquage_initial = {
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
        'input': {'p2': 1},
        'output': {'p4': 1}
    }
}

# marquage_initial = {
#     'p1': 1,
#     'p2': 0,
#     'p3': 0,
#     'p4': 0,
#     'p5': 0,
#     'p6': 0
# }
# transitions = {
#     't1': {
#         'input': {'p1': 1},
#         'output': {'p2': 1}
#     },
#     't2': {
#         'input': {'p2': 1},
#         'output': {'p3': 1}
#     },
#     't3': {
#         'input': {'p2': 1},
#         'output': {'p4': 1}
#     },
#     't4': {
#         'input': {'p3': 1},
#         'output': {'p5': 1}
#     },
#     't5': {
#         'input': {'p3': 1},
#         'output': {'p6': 1}
#     }
# }

# Fonction de hachage
def hachage(marking): 
    # convert to list of tuples[('p1', 1), ('p2', 0), ('p3', 0), ('p4', 0)]==> it is an object
    obj = str(sorted(marking.items())) 
    #Objects hashed: it is a number
    value = hash(obj)
    site = value % size  
    return site

# Function to check if a transition is enabled
def si_activable(transition, marking):  
    for place, tokens in transition['input'].items():
        # print('place: ', place)
        # print('tokens: ', tokens)
        # print('else: ', marking.get(place, 0))
        if marking.get(place, 0) < tokens: # si jetons nécessaires ne sont pas présents dans les places d'entrée de la transition==>False
            return False 
    return True

# Function pour appliquer la transition
def appliquer_transition(transition, marking): 
    nouveau_marquage = marking.copy()
    for place, tokens in transition['input'].items():
        nouveau_marquage[place] -= tokens # Retrait des Jetons des Places d'Entrée
    for place, tokens in transition['output'].items():
        nouveau_marquage[place] = nouveau_marquage.get(place, 0) + tokens #Ajout des Jetons aux Places de Sortie
    return nouveau_marquage

# Function to explore le marquage(activant les transitions possibles et pour chaque transition activable génère un nouveau marquage)
def explorer_marquage(marking):   
    nouveaux_marquages = [] # pour stocker les nouveaux marquages générés
    for transition_name, transition in transitions.items(): 
        if si_activable(transition, marking):
            nouveau_marquage = appliquer_transition(transition, marking)
            nouveaux_marquages.append((nouveau_marquage, transition_name))
    return nouveaux_marquages

# Main logic
if rank == 0: 
    # S0 initialise le processus
    target_site = hachage(marquage_initial)
    if target_site == 0:
        # the list of markings
        markings_to_explore = [marquage_initial]
    else:
        #Distribution du marquage initial(send to the target site)
        comm.send(marquage_initial, dest=target_site)
        markings_to_explore = [] # S0 initrialise markings_to_explore et qttente de la fin de l'exploration
else:
    #Les autres sites attendent des demandes d'exploration
    markings_to_explore = [] #Chaque site initialise une liste vide pour stocke les marquages explorer

    marking = comm.recv(source=MPI.ANY_SOURCE) #attente jusqu'à ce qu'il reçoit un message(Le site responsable continue et les autres non)
    if marking is not None:  # if it is None that means the exploration in done
        markings_to_explore.append(marking) # ajouter le marquage a sa liste pour explorer

# pour stocker les marquages qui ont déjà été explorés par le site courant(Cette liste n'est pas ordonnée et ne contient aucune répétition(set()))
explored_markings = set()
graph_edges = []  # Pour stocker les transitions entre les marquages

# Limiter la Profondeur d'Exploration(pour eviter les boucles infinies)
max_depth = 10000
current_depth = 0

# Explore markings
while markings_to_explore and current_depth < max_depth:
    current_marking = markings_to_explore.pop() # récupérer le marquage courant
    current_depth += 1
    marking_key = tuple(sorted(current_marking.items())) # convert marquage to key,exp:(('p1', 1), ('p2', 0), ('p3', 0), ('p4', 0))
    if marking_key not in explored_markings:#{(('p1', 0), ('p2', 1), ('p3', 0), ('p4', 0)), (('p1', 1), ('p2', 0), ('p3', 0), ('p4', 0))}
        explored_markings.add(marking_key)
        nouveaux_marquages = explorer_marquage(current_marking) #Explorer le marquage courant
        for nouveau_marquage, transition_name in nouveaux_marquages:
            target_site = hachage(nouveau_marquage)
            if target_site == rank:
                markings_to_explore.append(nouveau_marquage)
            else:
                comm.send(nouveau_marquage, dest=target_site)
            # Enregistrer la transition
            graph_edges.append((marking_key, tuple(sorted(nouveau_marquage.items())), transition_name)) # source,target,la transition activée.

# Envoi du Signal de Terminaison
if rank == 0:
    for i in range(1, size):
        comm.send(None, dest=i)

# Collecte des Résultats
all_markings = comm.gather(explored_markings, root=0)
all_edges = comm.gather(graph_edges, root=0)

# Fusion des Résultats
if rank == 0:
    # Fusionner tous les marquages ​​pour construire le graphique marketing global
    global_markings = set()
    for markings in all_markings:
        global_markings.update(markings)

    # Fusionner toutes les arêtes pour construire les arêtes du graphe global
    global_edges = []
    for edges in all_edges:
        global_edges.extend(edges)

    # Assurez-vous que tous les marquages ​​sur les edges sont inclus dans les marquages ​​globaux
    for edge in global_edges:
        source, target, _ = edge
        global_markings.add(source)
        global_markings.add(target)

    # Trier les marquages ​​et inverser l'ordre
    sorted_markings = sorted(global_markings, reverse=True)  # Inverser l'ordre ici

    # Attribuer des ID aux marquages ​​dans l'ordre inverse
    marking_to_id = {marking: f"M{i}" for i, marking in enumerate(sorted_markings)}

    # Imprimer le graphique marketing global
    print("Global Marking Graph:")
    for edge in global_edges:
        source, target, transition = edge
        print(f"{marking_to_id[source]} --({transition})--> {marking_to_id[target]}")

    # Print the values of each node
    print("\nValues of each node:")
    for marking, marking_id in marking_to_id.items():
        print(f"{marking_id}: {dict(marking)}")