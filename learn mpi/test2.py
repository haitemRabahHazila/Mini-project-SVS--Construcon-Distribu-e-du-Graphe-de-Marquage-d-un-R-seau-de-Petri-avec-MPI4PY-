from mpi4py import MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
TAG = 99
if rank == 0:
  message = "hello"
  comm.send(message , dest = 1, tag = TAG )
  print(str(rank),"envoie", message,"vers", "1")
if rank == 1:
  tok= comm.recv(source= MPI.ANY_SOURCE, tag = 99 )
  print(str(rank), "recoit", tok,"de", "0")