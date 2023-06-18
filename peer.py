import socket
import threading
import argparse
from naming import *
from message_handler_utils import *
from Nodo import Nodo
import psutil

"""
i nodi vengono riconosciuti nel ring tramite un identificativo numerico o alfanumerico in formato di
stringa. 
Il formato dei messaggi è attualmente il seguente: 'tipo_messaggio§mittente§destinatario§messaggio'
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
def send_message(peer: Nodo):
    """
    La funziona ha lo scopo d'inviare messaggi standard dei nodi lungo la rete ad anello.
    Accetta messaggi in ingresso dall'utente con i quali compone il messaggio da inviare che avrà
    il seguente formato: 'TIPO_MESSAGGIO§ID_MITTENTE§ID_DESTINATARIO§MESSAGGIO'
    :return:
    """
    while True:
        destinatario = input("A chi vuoi mandare un messaggio?\n")
        message = "STANDARD" + "§" + peer.get_nickname() + "§" + destinatario + "§" + input("messaggio: ")
        socket_send.sendto(message.encode(), peer.get_IP_next(), peer.get_PORT_next())


def send_connection_refused_message(peer: Nodo, address):
    message_refused = "CONNECTION_REFUSED" + "§" + peer.get_nickname() + "§" + "" + "§" + ""
    socket_send.sendto(message_refused.encode(), address)


def send_discovery_query(peer: Nodo, nickname_to_check):
    message_discovery = "DISCOVERY_QUERY" + "§" + peer.get_nickname() + "§" + nickname_to_check + "§" + ""
    socket_send.sendto(message_discovery.encode(), (peer.get_IP_next(), peer.get_PORT_next()))


def send_join_message(ip_pre, port_pre, joiner_nickname):
    message_join = "JOIN" + "§" + joiner_nickname + "§" + "" + "§" + ""
    socket_send.sendto(message_join.encode(), (ip_pre, port_pre))


def send_connection_accepted_message(peer: Nodo, join_node_address, joiner_nickname):
    msg_accepted = peer.get_IP_next() + "£" + peer.get_PORT_next()
    message_accepted = "CONNECTION_ACCEPTED" + "§" + peer.get_nickname() + "§" + joiner_nickname + "§" + msg_accepted
    socket_send.sendto(message_accepted.encode(), join_node_address)


def send_change_prec_message(peer: Nodo, addr_joiner):
    msg_change_prec = addr_joiner[0] + "£" + addr_joiner[1]
    message_change_prec = "CHANGE_PREC" + "§" + peer.get_nickname() + "§" + "" + "§" + msg_change_prec
    socket_send.sendto(message_change_prec.encode(), (peer.get_IP_next(), peer.get_PORT_next()))


def send_discovery_answer(peer: Nodo, id_mittente_, id_destinatario_, msg_):
    message_discovery_answer = "DISCOVERY_ANSWER" + "§" + id_mittente_ + "§" + id_destinatario_ + "§" + msg_
    socket_send.sendto(message_discovery_answer.encode(), (peer.get_IP_next(), peer.get_PORT_next()))


# Funzione per la gestione dei messaggi ricevuti
def message_handler(peer: Nodo):
    joiner_address = None
    while True:
        data, address = socket_receive.recvfrom(1024)
        message = data.decode()
        msg_type, id_mittente, id_destinatario, msg = message.split("§")
        if msg_type == "JOIN":
            # Gestione del messaggio di join da un nuovo nodo
            # Invia i tuoi ip_next e port_next al nuovo nodo
            # Avvia la procedura di discovery per trovare un nickname disponibile
            # Assegna il nickname se disponibile al nuovo nodo
            joiner_address = address
            if id_mittente != peer.get_nickname():
                send_discovery_query(peer, id_mittente)
            else:
                send_connection_refused_message(peer, joiner_address)
        elif msg_type == "DISCOVERY_QUERY":
            # procedura di discovery da sviluppare

            if id_mittente == peer.get_nickname():
                # Mando un connection accepted al joiner con le info sui miei ip_next e port_next
                send_connection_accepted_message(peer, joiner_address, id_destinatario)
                # mando un messaggio al mio attuale successivo per dirgli di impostare il joiner come suo precedente
                send_change_prec_message(peer, joiner_address)
                # e imposto il joiner come mio successivo.
                peer.set_IP_next(joiner_address[0])
                peer.set_PORT_next(joiner_address[1])
            else:  # non sono il mittente del discovery query
                if id_destinatario == peer.get_nickname():
                    send_discovery_answer(peer, id_mittente, id_destinatario,
                                          msg)  # stesso messaggio ma cambio tipo in discovery answer e lo inoltro
                else:  # inoltro al nodo successivo
                    socket_send.sendto(message.encode(), (peer.get_IP_next(), peer.get_PORT_next()))

        elif msg_type == "DISCOVERY_ANSWER":
            # procedura di discovery da sviluppare se ricevo un messaggio di questo tipo (e il mittente sono io)
            # significa che il nickname non è disponibile. Quindi devo inviare un CONNECTION_REFUSED al mittente del
            # messaggio di JOIN
            if id_mittente == peer.get_nickname():
                # L'id destinatario non è disponibile. Devo mandare un messaggio connection refused.
                send_connection_refused_message(peer, joiner_address)
            else:  # Inoltra il DISCOVERY_QUERY al prossimo
                socket_send.sendto(message.encode(), (peer.get_IP_next(), peer.get_PORT_next()))

        elif msg_type == "STANDARD":
            # messaggio di tipo standard
            standard_message_handler(peer, id_mittente, id_destinatario, msg, socket_send)

        elif msg_type == "ACK":
            # messaggio di tipo ack
            ack_message_handler(peer, id_destinatario, msg, socket_send)

        elif msg_type == "QUIT":
            peer.set_IP_next(msg.split("ç")[0])
            peer.set_PORT_next(msg.split("ç")[1])
        elif msg_type == "CHANGE_PREC":
            new_prec_ip, new_prec_port = msg.split("£")
            peer.set_IP_prec(new_prec_ip)
            peer.set_PORT_prec(new_prec_port)
        else:
            # messaggio non riconosciuto
            # handle_message(id_mittente, msg)
            print("il formato del messaggio {} non è riconosciuto\n".format(message))


# Faccio il parsing degli argomenti passati in input dall'utente:
parser = argparse.ArgumentParser(description="Parametri descrittivi del peer")
parser.add_argument("nickname", type=str, help="nickname identificativo con cui l'host vuole aggiungersi")
parser.add_argument("-IP_socket_rec", type=str, default="localhost", help="IP della porta di ricezione dei messaggi")
parser.add_argument("PORT_socket_rec", type=int, help="Porta di ricezione dei messaggi")
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
try:
    socket_receive = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    socket_receive.bind((args.IP_socket_rec, args.PORT_socket_rec))
except OSError as error:
    print(f"Errore con la porta:{args.PORT_socket_rec}", error)
    if input(f"\nVuoi terminare il processo che impegna la porta {args.PORT_socket_rec}? [s/n]\n") != "s":
        raise ValueError('Non è possibile utilizzare le porte selezionate. '
                         'Riprovare con altri valori oppure terminare i processi che occupano le porte.')

    connection = psutil.net_connections()
    pid = None
    for conn in connection:
        if conn.laddr.port == args.PORT_socket_rec:
            pid = conn.pid
            break
    if pid:
        process = psutil.Process(pid)
        process.terminate()
        process.wait()
    socket_receive = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    socket_receive.bind((args.IP_socket_rec, args.PORT_socket_rec))

# Crea un socket per l'invio dei messaggi
try:
    socket_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    socket_send.bind((args.IP_socket_send, args.PORT_socket_send))
except OSError as error:
    print(f"Errore con la porta:{args.PORT_socket_send}", error)
    if input(f"\nVuoi terminare il processo che impegna la porta {args.PORT_socket_send}? [s/n]\n") != "s":
        raise ValueError('Non è possibile utilizzare le porte selezionate. '
                         'Riprovare con altri valori oppure terminare i processi che occupano le porte.')
    connection = psutil.net_connections()
    pid = None
    for conn in connection:
        if conn.laddr.port == args.PORT_socket_send:
            pid = conn.pid
            break
    if pid:
        process = psutil.Process(pid)
        process.terminate()
        process.wait()
    socket_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    socket_send.bind((args.IP_socket_send, args.PORT_socket_send))


def wait_for_join_response():
    pass


# Se specifico ip e porta del nodo a cui voglio connettermi allora mi sto connettendo ad un anello già
# esistente. Altrimenti sono il primo di un nuovo anello, per cui la procedura di join non deve essere
# avviata.
if args.f:
    received_message = False  # Variabile che userò per verificare la ricezione di una risposta al messaggio di join
    # Variabili per l'indirizzo del nodo che conosco nel ring, a cui dovrò inviare il messaggio di JOIN
    ip_prec, port_prec = args.f

    # La procedura di JOIN parte da qui:
    # Mando messaggio di join
    send_join_message(ip_prec, port_prec, args.nickname)
    # Aspetto un messaggio DISCOVERY QUERY O ANSWER
    while not received_message:
        data, address = socket_receive.recvfrom(1024)
        message = data.decode()
        msg_type, id_mittente, id_destinatario, msg = message.split("§")
        if msg_type == "CONNECTION_REFUSED":
            received_message = True
            raise ValueError('Il nickname inserito è già in uso. Riprovare con un nickname diverso.')
        elif msg_type == "CONNECTION_ACCEPTED":
            # se la procedura va a buon fine assegno il nickname scelto. Altrimenti termino il processo.
            # bisognerà inoltre impostare i valori di ip e porta del nodo successivo
            my_node_id = format_name(args.nickname)
            ip_next, port_next = msg.split("£")
            received_message = True
else:  # Se sono il primo di un nuovo ring
    my_node_id = format_name(args.nickname)
    ip_prec = None
    port_prec = None
    ip_next = None
    port_next = None

nodo = Nodo(my_node_id, ip_prec, port_prec, ip_next, port_next)

# Creo e avvio il thread per la gestione dei messaggi ricevuti
message_handler_thread = threading.Thread(target=message_handler, args=([nodo]))
message_handler_thread.start()

# Creo e avvio il thread per la gestione dell'invio dei messaggi
send_message_thread = threading.Thread(target=send_message, args=([nodo]))
send_message_thread.start()

# Attendi la terminazione dei thread
message_handler_thread.join()
send_message_thread.join()

# Chiudi i socket
socket_receive.close()
socket_send.close()
