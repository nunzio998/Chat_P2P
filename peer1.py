from random import *
import socket
from threading import Thread
import time
import threading

# Procedura di registrazione al coordinatore

coordinator1_port = 8000

# creo porta di registrazione casuale che sarà anche quella di ricezione:
port = randint(1, 60000)

#Creo una lista di nodi peer inizialmente vuota

lista_nodi = []



def receive_from_server():
    pass


def send():
    while True:
        try:
            # text = input("Type value in peer2: ")
            text = input()
            print(text)
            if text == "disconnection":
                disconnect()
                exit(0)
        except:
            pass
    pass


def receive():
    pass


def register():
    # Invia una richiesta di registrazione al nodo coordinatore
    socket_register.sendto("REGISTER".encode(), ('localhost', coordinator1_port))

    # Invia la porta al nodo coordinatore per la comunicazione
    socket_register.sendto(str(port).encode(), ('localhost', coordinator1_port))

    # Ricevi la lista dei nodi connessi dal coordinatore
    data, _ = socket_register.recvfrom(1024)
    node_list = data.decode().split("\n")
    print(node_list)
    # Rimuovi la propria porta dalla lista dei nodi connessi
    node_list.remove(str(port))


def disconnect():
    socket_register.sendto("DISCONNECT".encode(), ('localhost', coordinator1_port))

    # Chiudi il socket di registrazione
    socket_register.close()


# Creo le socket di cui ho bisogno
socket_register = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socket_register.bind(('localhost', port))

# Creo i threads che mi servono
try:
    register_thread = threading.Thread(target=register, args=())
    send_thread = threading.Thread(target=send, args=())

    # Faccio partire i thread
    register_thread.start()
    send_thread.start()

    # Attendo la terminazione dei thread
    register_thread.join()
    send_thread.join()
except:
    pass
