from time import sleep
from threading import Thread

def task():
    """Simulate a task by sleeping for 1 second and printing a message."""
    sleep(1)  # Simulate work by sleeping for 1 second
    print("Execution d'un thread")


  """Main function to create, start, and wait for a thread."""
  # Création du thread
  thread = Thread(target=task)

  # Lancer le thread
  thread.start()
  print("Attendre le thread...")

  # Attendre la fin du thread
  thread.join()
  print("Le thread a terminé son exécution.")

if __name__ == "__main__":
    main()