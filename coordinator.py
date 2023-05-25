import socket
import ssl
import threading
import time

# Dizionario per memorizzare le porte dei nodi registrati
node_ports = {}

listen_port = 8000
send_port = 6000


# Funzione per la gestione delle richieste di registrazione dei nodi
def handle_registration():
    while True:
        data, address = socket_receive.recvfrom(1024)
        if data.decode() == "REGISTER":
            # Aggiungi la porta del nodo registrato al dizionario
            node_ports[address[1]] = True
            # Invia la lista aggiornata dei nodi connessi a tutti i nodi registrati
            node_list = "\n".join([str(port) for port in node_ports.keys() if node_ports[port] == True])
            print(node_list)
            for port in node_ports.keys():
                socket_send.sendto(node_list.encode(), ('localhost', port))
            print(node_ports)


def handle_disconnection():
    while True:
        data, address = socket_receive.recvfrom(1024)
        if data.decode() == "DISCONNECT":
            # Rimuovi la porta del nodo registrato al dizionario
            node_ports[address[1]] = False
            # Invia la lista aggiornata dei nodi connessi a tutti i nodi registrati
            node_list = "\n".join([str(port) for port in node_ports.keys() if node_ports[port] == True])
            for port in node_ports.keys():
                socket_send.sendto(node_list.encode(), ('localhost', port))
            print(node_ports)


# Crea un socket per la ricezione dei messaggi
socket_receive = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socket_receive.bind(('localhost', listen_port))

# Crea un socket per l'invio dei messaggi
socket_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socket_send.bind(('localhost', send_port))

# Avvia il thread per la gestione delle richieste di registrazione
registration_thread = threading.Thread(target=handle_registration)
registration_thread.start()

# Avvia il thread per la gestione delle richieste di disconnessione
disconnection_thread = threading.Thread(target=handle_disconnection)
disconnection_thread.start()
print("Coordinatore in ascolto all'indirizzo {} sulla porta {}".format('127.0.0.1', listen_port))
# Attendi la terminazione dei thread
registration_thread.join()
disconnection_thread.join()

# Chiudi i socket
socket_receive.close()
socket_send.close()
