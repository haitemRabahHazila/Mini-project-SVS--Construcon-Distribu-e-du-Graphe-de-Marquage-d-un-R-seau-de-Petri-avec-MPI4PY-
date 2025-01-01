from time import sleep
from threading import Thread

def task():
    sleep(1)
    print("Execution d'un thread")

# Création du thread
thread = Thread(target=task)

# Lancer le thread
thread.start()

# Attendre la fin du thread
print("Attendre le thread...")
thread.join()
print('fin',thread.name)