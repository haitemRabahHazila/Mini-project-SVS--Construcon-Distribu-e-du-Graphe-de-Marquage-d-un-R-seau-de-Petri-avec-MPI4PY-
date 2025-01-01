from mpi4py import MPI
import numpy
comm = MPI.COMM_WORLD
rank= comm.Get_rank()
if rank == 0:
  tab = numpy.arange(1, 10, 3)
  comm.Send(tab , dest = 1)
  print(str(rank),"envoie", tab,"vers", "1")
if rank == 1:
  tok = numpy.empty(3, dtype= int)
  comm.Recv(tok, source= 0)
  print(str(rank), "recoit", tok,"de", "0")