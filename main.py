from mpi4py import MPI

# Initialisation MPI(Message Passing Interface)
#تفترض MPI أن الاتصال يتم ضمن مجموعة من العمليات التي يجب أن تعرف بعضها البعض
#Tout processus est identifie `a l’aide d’un nom unique.
# elmorssil y3ayat l send() et lmosta9bil y3ayat l recv()



comm = MPI.COMM_WORLD # communicateur
rank = comm.Get_rank() #grade
size = comm.Get_size() # nbr of processus 

# Définition du réseau de Petri
initial_marking = {'p1': 1, 'p2': 0}  # Exemple de marquage initial
transitions = {
    't1': {'input': {'p1': 1}, 'output': {'p2': 1}},
    't2': {'input': {'p2': 1}, 'output': {'p1': 1}}
}

# Fonction de hachage pour déterminer le site responsable d'un marquage
def hash_marking(marking):
    return hash(frozenset(marking.items())) % size

# Fonction pour explorer un marquage
def explore_marking(marking, transitions):
    explored = set()
    to_explore = [marking]

    while to_explore:
        current_marking = to_explore.pop()
        current_marking_frozen = frozenset(current_marking.items())  # Convertir en frozenset
        if current_marking_frozen in explored:
            continue
        explored.add(current_marking_frozen)

        for transition, effect in transitions.items():
            if all(current_marking.get(p, 0) >= v for p, v in effect['input'].items()):
                new_marking = current_marking.copy()
                for p, v in effect['input'].items():
                    new_marking[p] -= v
                for p, v in effect['output'].items():
                    new_marking[p] += v

                target_rank = hash_marking(new_marking)
                if target_rank != rank:  # Envoyer uniquement si le marquage est destiné à un autre site
                    comm.send(new_marking, dest=target_rank)
                    print(f"Site {rank}: Envoi du marquage {new_marking} au site {target_rank}")
                else:
                    to_explore.append(new_marking)  # Explorer localement si le marquage est pour ce site

    return explored

# Site 0 (maître)
if rank == 0:
    print(f"Site {rank}: Démarrage du processus de calcul du graphe de marquage")
    # Étape 1 : Hachage du marquage initial
    target_rank = hash_marking(initial_marking)
    print(f"Site {rank}: Le marquage initial {initial_marking} est attribué au site {target_rank}")
    
    # Étape 2 : Envoi de la demande d'exploration au site responsable
    comm.send(initial_marking, dest=target_rank, tag=0)
    print(f"Site {rank}: Demande d'exploration envoyée au site {target_rank}")

    # Synchronisation : Attendre que tous les processus atteignent cette barrière
    comm.Barrier()

    # Étape 6 : Réception des résultats des autres sites
    global_markings = set()
    for i in range(1, size):
        received_markings = comm.recv(source=i, tag=1)
        global_markings.update(received_markings)
        print(f"Site {rank}: Résultats reçus du site {i}")

    # Étape 7 : Fusion des résultats et construction du graphe de marquage
    print(f"Site {rank}: Fusion des résultats et construction du graphe de marquage")
    graph = {}
    for marking in global_markings:
        marking_dict = dict(marking)  # Convertir frozenset en dictionnaire
        graph[marking_dict] = []
        for transition, effect in transitions.items():
            if all(marking_dict.get(p, 0) >= v for p, v in effect['input'].items()):
                new_marking = marking_dict.copy()
                for p, v in effect['input'].items():
                    new_marking[p] -= v
                for p, v in effect['output'].items():
                    new_marking[p] += v
                graph[marking_dict].append((transition, new_marking))

    print("Graphe de marquage global:", graph)

# Autres sites (travailleurs)
else:
    # Synchronisation : Attendre que le Site 0 ait terminé son initialisation
    comm.Barrier()

    # Étape 3 : Réception de la demande d'exploration
    marking = comm.recv(source=0, tag=0)
    print(f"Site {rank}: Demande d'exploration reçue pour le marquage {marking}")

    # Étape 4 : Exploration du marquage
    explored = explore_marking(marking, transitions)

    # Étape 5 : Envoi des résultats au site 0
    comm.send(explored, dest=0, tag=1)
    print(f"Site {rank}: Résultats de l'exploration envoyés au site 0")