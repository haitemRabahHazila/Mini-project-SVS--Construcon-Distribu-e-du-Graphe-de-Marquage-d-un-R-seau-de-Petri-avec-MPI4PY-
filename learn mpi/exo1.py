from mpi4py import MPI
import numpy as np

# Initialisation de MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# Taille du tableau
n = 10

# Communication en anneau
if rank == 0:
    # Le processus 0 initialise le tableau
    tab = np.zeros(n, dtype=int)
    # Le processus 0 commence en envoyant le tableau à son voisin (rang 1)
    comm.send(tab, dest=1)
    print(f"Processus {rank} a envoyé {tab} au processus 1")

    # Le processus 0 attend de recevoir le tableau final du dernier processus (rang 9)
    tab = comm.recv(source=size - 1)
    print(f"Processus {rank} a reçu {tab} du processus {size - 1}")
    print("this is the last one")
else:
    # Les autres processus préparent un tableau vide pour recevoir les données
    tab = np.empty(n, dtype=int)
    # Les autres processus reçoivent le tableau, le modifient et l'envoient au suivant
    tab = comm.recv(source=(rank - 1) % size)
    print(f"Processus {rank} a reçu {tab} du processus {(rank - 1) % size}")

    # Mise à jour de la case correspondant au rang
    tab[rank] = rank

    # Envoi du tableau au processus suivant dans l'anneau
    comm.send(tab, dest=(rank + 1) % size)
    print(f"Processus {rank} a envoyé {tab} au processus {(rank + 1) % size}")