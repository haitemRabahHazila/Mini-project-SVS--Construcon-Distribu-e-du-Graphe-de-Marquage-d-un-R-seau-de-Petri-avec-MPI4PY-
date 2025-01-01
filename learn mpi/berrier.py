from mpi4py import MPI

# Initialisation de MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()  # Corrected method to get the rank

if rank == 0:
    print("Processus", rank, "commence son execution")  # Removed unnecessary spaces

# Synchronisation avec une barrière
comm.Barrier()
print("Processus", rank, "a atteint la barriere")  # Removed unnecessary spaces