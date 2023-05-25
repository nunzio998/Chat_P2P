from random import *
import socket
from threading import Thread
import time

# Procedura di registrazione al coordinatore

coordinator1_port = 8000

# creo porta di registrazione casuale che sarà anche quella di ricezione:
port = randint(1, 60000)

# Crea un socket per la registrazione/disconnessione al nodo coordinatore e per ricevere messaggi da nodi o coordinatore
socket_register = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socket_register.bind(('localhost', port))

# Invia una richiesta di registrazione al nodo coordinatore
socket_register.sendto("REGISTER".encode(), ('localhost', coordinator1_port))

# Crea un socket per la ricezione dei messaggi
# socket_receive = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Utilizza una porta casuale per la ricezione
# socket_receive.bind(('localhost', 0))
# Ricevi la porta assegnata dal sistema per la ricezione dei messaggi
# port = socket_receive.getsockname()[1]

# Invia la porta al nodo coordinatore per la comunicazione
socket_register.sendto(str(port).encode(), ('localhost', coordinator1_port))

# Ricevi la lista dei nodi connessi dal coordinatore
data, _ = socket_register.recvfrom(1024)
node_list = data.decode().split("\n")
print(node_list)
# Rimuovi la propria porta dalla lista dei nodi connessi
node_list.remove(str(port))

time.sleep(5)

socket_register.sendto("DISCONNECT".encode(), ('localhost', coordinator1_port))

# Chiudi il socket di registrazione
socket_register.close()


def receive_from_server():
    pass


def send():
    pass


def receive():
    pass


"""
try:
    th1 = Thread(target=receive_from_server, args=())
    th1.start()
except:
    pass
try:
    th2 = Thread(target=send, args=())
    th2.start()
except:
    pass

try:
    th3 = Thread(target=receive, args=())
    th3.start()
except:
    pass
"""
# Effettua la comunicazione diretta con gli altri nodi
for node_port in node_list:
    node_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    node_socket.bind(('localhost', 7878))
    node_socket.sendto("Ciao, sono un nodo!".encode(), ('localhost', int(node_port)))
    node_socket.close()

# Chiudi il socket di ricezione
# socket_receive.close()
