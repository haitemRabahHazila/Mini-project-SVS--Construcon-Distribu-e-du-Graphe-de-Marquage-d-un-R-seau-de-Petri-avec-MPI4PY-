from mpi4py import MPI
import numpy as np

# Initialisation de MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()  # Corrected method to get the rank

# Initialisation du tableau
data = np.zeros(3, dtype=int)

if rank == 0:
    # Le processus 0 initialise le tableau
    data = np.arange(1, 10, 3)
    print("Avant envoi, le contenu de data est", data)

# Diffusion du tableau à tous les processus
data = comm.bcast(data, root=0)

# Affichage du tableau reçu par chaque processus
print(f"Processus {rank}: {data}")