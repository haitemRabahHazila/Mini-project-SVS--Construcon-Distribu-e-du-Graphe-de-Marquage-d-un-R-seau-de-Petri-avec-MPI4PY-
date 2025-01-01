from mpi4py import MPI
import numpy as np

# Initialisation de MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# Nombre total de nombres aléatoires à générer
total_numbers = 20

# Génération des nombres aléatoires sur le processus racine (rang 0)
if rank == 0:
    # Génère un tableau de nombres aléatoires
    data = np.random.randint(0, 100, total_numbers)
    print(f"Processus {rank} a généré les nombres : {data}")
else:
    data = None

# Dispersion des nombres à tous les processus
local_size = total_numbers // size  # Nombre de nombres par processus
local_data = np.empty(local_size, dtype=int)  # Tableau local pour chaque processus
comm.Scatter(data, local_data, root=0)

# Calcul de la moyenne locale
local_mean = np.mean(local_data)
print(f"Processus {rank} a reçu les nombres : {local_data}, moyenne locale : {local_mean}")

# Rassemblement des moyennes locales sur le processus racine
all_means = None
if rank == 0:
    all_means = np.empty(size, dtype=float)  # Tableau pour stocker toutes les moyennes
comm.Gather(local_mean, all_means, root=0)

# Calcul de la moyenne globale sur le processus racine
if rank == 0:
    global_mean = np.mean(all_means)
    print(f"Moyennes locales reçues par le processus 0 : {all_means}")
    print(f"Moyenne globale calculée : {global_mean}")