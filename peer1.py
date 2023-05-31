import socket
import threading

"""
i nodi vengono riconosciuti nel ring tramite un identificativo numerico o alfanumerico in formato di
stringa. 
Il formato dei messaggi è attualmente il seguente: 'tipo_messaggio#mittente#destinatario#messaggio'
il tipo di messaggio può essere molteplice:
- messaggio normale 
- messaggio di discovery
- messaggio di join
l'utente della chat p2p ha facoltà di mandare solo messaggi standard. Messaggi di discovery/join vengono
inviati solo all'inizio dello script, quando il nodo viene creato e ha bisogno di agganciarsi al ring
con un nuovo identificativo.
"""


# Funzione per la gestione dei messaggi ricevuti
def handle_message(sender, message):
    print(f"Messaggio ricevuto da {sender}: {message}\n")


# Funzione per inviare un messaggio al nodo successivo nel ring
def send_message():
    while True:
        destinatario = input("A chi vuoi mandare un messaggio?\n")
        message = "STANDARD" + "#" + my_node_id + "#" + destinatario + "#" + input("messaggio: ")
        print(message + "\n")
        socket_send.sendto(message.encode(), (ip_next, port_next))


# Funzione per la gestione dei messaggi ricevuti
def message_handler():
    while True:
        data, address = socket_receive.recvfrom(1024)
        message = data.decode()
        msg_type, id_mittente, id_destinatario, msg = message.split("#")

        if msg_type == "JOIN":
            # Gestione del messaggio di join da un nuovo nodo
            # Invia i tuoi ip_next e port_next al nuovo nodo
            # Avvia la procedura di discovery per trovare un nickname disponibile
            # Assegna il nickname disponibile al nuovo nodo
            pass
        elif msg_type == "DISCOVERY":
            # procedura di discovery da sviluppare
            pass
        elif msg_type == "STANDARD":
            if id_mittente == my_node_id:  # il mittente sono io, quel nickname non esiste
                print("Non esiste un nodo con nickname {}\n".format(id_destinatario))
            elif id_destinatario == my_node_id:
                handle_message(id_mittente, msg)
            else:
                # il messaggio non è stato mandato da me e non è diretto a me
                # allora lo inoltro al prossimo nodo, continua il giro
                socket_send.sendto(message.encode(), (ip_next, port_next))
        else:
            # messaggio non riconosciuto
            # handle_message(id_mittente, msg)
            print("il formato del messaggio {} non è riconosciuto\n".format(message))


# Crea un socket per la ricezione dei messaggi
socket_receive = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socket_receive.bind(('localhost', 8000))

# Crea un socket per l'invio dei messaggi
socket_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socket_send.bind(('localhost', 8001))

# Variabili per l'indirizzo del nodo successivo nel ring
ip_next = 'localhost'
port_next = 8002

# Id del nodo:
my_node_id = "1"

# Creo e avvio il thread per la gestione dei messaggi ricevuti
receive_message_thread = threading.Thread(target=message_handler, args=())
receive_message_thread.start()

# Creo e avvio il thread per la gestione dell'invio dei messaggi
send_message_thread = threading.Thread(target=send_message, args=())
send_message_thread.start()

# Attendi la terminazione dei thread
receive_message_thread.join()
send_message_thread.join()

# Chiudi i socket
socket_receive.close()
socket_send.close()
