import socket
import threading
from sys import argv

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
    """
    Funzione che ha il solo scopo di stampare a schermo il messaggio e chi lo ha inviato.
    :param sender:
    :param message:
    :return:
    """
    print(f"Messaggio ricevuto da {sender}: {message}\n")


# Funzione per inviare un messaggio al nodo successivo nel ring
def send_message():
    """
    La funziona ha lo scopo d'inviare messaggi standard dei nodi lungo la rete ad anello.
    Accetta messaggi in ingresso dall'utente con i quali compone il messaggio da inviare che avrà
    il seguente formato: 'TIPO_MESSAGGIO#ID_MITTENTE#ID_DESTINATARIO#MESSAGGIO'
    :return:
    """
    while True:
        destinatario = input("A chi vuoi mandare un messaggio?\n")
        message = "STANDARD" + "#" + my_node_id + "#" + destinatario + "#" + input("messaggio: ")
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
            if id_mittente == my_node_id and id_destinatario != my_node_id:
                # il mittente sono io, ma non sono il destinatario
                # questo vuol dire che ho inviato un messaggio ad un destinatario che non esiste
                print("Non esiste un nodo con nickname {}\n".format(id_destinatario))
            elif id_destinatario == my_node_id:
                # Il messaggio è indirizzato a me, quindi lo gestisco
                handle_message(id_mittente, msg)
            else:
                # il messaggio non è stato mandato da me e non è diretto a me
                # allora lo inoltro al prossimo nodo, continua il giro.
                socket_send.sendto(message.encode(), (ip_next, port_next))
        else:
            # messaggio non riconosciuto
            # handle_message(id_mittente, msg)
            print("il formato del messaggio {} non è riconosciuto\n".format(message))


# Crea un socket per la ricezione dei messaggi
socket_receive = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socket_receive.bind(('localhost', int(argv[1])))

# Crea un socket per l'invio dei messaggi
socket_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socket_send.bind(('localhost', int(argv[2])))

# La procedura di JOIN parte da qui:

# Variabili per l'indirizzo del nodo successivo nel ring
ip_next = 'localhost'
port_next = int(argv[3])

# Id del nodo:
my_node_id = argv[4]

# Creo e avvio il thread per la gestione dei messaggi ricevuti
message_handler_thread = threading.Thread(target=message_handler, args=())
message_handler_thread.start()

# Creo e avvio il thread per la gestione dell'invio dei messaggi
send_message_thread = threading.Thread(target=send_message, args=())
send_message_thread.start()

# Attendi la terminazione dei thread
message_handler_thread.join()
send_message_thread.join()

# Chiudi i socket
socket_receive.close()
socket_send.close()
