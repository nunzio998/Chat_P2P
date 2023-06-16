import socket
import threading
import argparse
from naming import *

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
        elif msg_type == "QUIT":
            ip_next, port_next = msg.split("-")
        else:
            # messaggio non riconosciuto
            # handle_message(id_mittente, msg)
            print("il formato del messaggio {} non è riconosciuto\n".format(message))


# Faccio il parsing degli argomenti passati in input dall'utente:
parser = argparse.ArgumentParser(description="Parametri descrittivi del peer")
parser.add_argument("nickname", type=str, help="nickname identificativo con cui l'host vuole aggiungersi")
parser.add_argument("-IP_sock_rec", type=str, default="localhost", help="IP della porta di ricezione dei messaggi")
parser.add_argument("PORT_sock_rec", type=int, help="Porta di ricezione dei messaggi")
parser.add_argument("-IP_socket_send", type=str, default="localhost", help="IP della porta di invio dei messaggi")
parser.add_argument("PORT_socket_send", type=int, help="Porta di invio dei messaggi")
parser.add_argument('-f', nargs=2, metavar=('IP', 'PORT'), help='Specificare l\'indirizzo IP e la porta del nodo a '
                                                                'cui voglio collegarmi')
# Parsa gli argomenti dalla riga di comando
args = parser.parse_args()

# Controllo che il nickname scelto sia nel formato corretto (stabilito dalla regex r'^[A-Z]{6}\d{2}$'). Se
# non lo è termino il processo.
if not check_name(args.nickname):
    raise ValueError('Il nickname inserito non rispetta i parametri. Riprovare con un nickname valido.')


# Crea un socket per la ricezione dei messaggi
socket_receive = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socket_receive.bind((args.IP_sock_rec, args.PORT_sock_rec))

# Crea un socket per l'invio dei messaggi
socket_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socket_send.bind((args.IP_socket_send, args.PORT_socket_send))

# Se specifico ip e porta del nodo a cui voglio connettermi allora mi sto connettendo ad un anello già
# esistente. Altrimenti sono il primo di un nuovo anello, per cui la procedura di join non deve essere
# avviata.
if args.f:
    # Variabili per l'indirizzo del nodo che conosco nel ring, a cui dovrò inviare il messaggio di JOIN
    ip_prec, port_prec = args.f

    # La procedura di JOIN parte da qui:

    # se la procedura va a buon fine assegno il nickname scelto. Altrimenti termino il processo.
    # bisognerà inoltre impostare i valori di ip e porta del nodo successivo
    my_node_id = format_name(args.nickname)
    ip_next = "ip del nodo successivo"
    port_next = "porta del nodo successivo"
else:  # Se sono il primo di un nuovo ring
    my_node_id = format_name(args.nickname)
    ip_prec = None
    port_prec = None
    ip_next = None
    port_next = None

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
