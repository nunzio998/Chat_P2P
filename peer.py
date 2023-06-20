import socket
import threading
import argparse
from naming import *
from message_handler_utils import *
from Nodo import Nodo
import psutil
from format import Formatting as fmt


# Funzione per inviare un messaggio al nodo successivo nel ring
def send_message():
    """
    La funziona ha lo scopo d'inviare messaggi standard dei nodi lungo la rete ad anello.
    Accetta messaggi in ingresso dall'utente con i quali compone il messaggio da inviare che avrà
    il seguente formato: 'TIPO_MESSAGGIO§ID_MITTENTE§ID_DESTINATARIO§MESSAGGIO'
    :return:
    """
    while True:
        destinatario = input("A chi vuoi mandare un messaggio?\n")

        if destinatario == "":
            print("\n")
        elif destinatario.upper() == "QUIT":
            # disconnessione volontaria
            message_back = fmt.packing("QUIT", peer.get_nickname(), "", peer.get_IP_next(), peer.get_PORT_next())
            socket_send.sendto(message_back.encode(), (peer.get_IP_prec(), peer.get_PORT_prec()))
            message_forward = fmt.packing("QUIT", peer.get_nickname(), "", peer.get_IP_prec(), peer.get_PORT_prec())
            socket_send.sendto(message_forward.encode(), (peer.get_IP_next(), peer.get_PORT_next()))
        elif check_name(destinatario):
            message = fmt.packing("STANDARD", peer.get_nickname(), destinatario.upper(), input("Messaggio:\n"))
            socket_send.sendto(message.encode(), (peer.get_IP_next(), peer.get_PORT_next()))
        else:
            print("Il nickname indicato non è valido.")


def send_join_message(ip_pre, port_pre, joiner_nickname, socket_receive):
    message_join = fmt.packing("JOIN", joiner_nickname, "", socket_receive.getsockname()[0],
                               socket_receive.getsockname()[1])
    socket_send.sendto(message_join.encode(), (ip_pre, port_pre))


# Funzione per la gestione dei messaggi ricevuti
def message_handler():
    joiner_address = None
    while True:
        data, address = socket_receive.recvfrom(1024)
        message = data.decode()
        msg_type, id_mittente, id_destinatario, msg = fmt.unpacking(message).values()

        # handling del messaggio in base al tipo
        if msg_type == "JOIN":
            # Gestione del messaggio di join da un nuovo nodo
            # Invia i tuoi ip_next e port_next al nuovo nodo
            # Avvia la procedura di discovery per trovare un nickname disponibile
            # Assegna il nickname se disponibile al nuovo nodo
            joiner_address = msg
            if id_mittente == peer.get_nickname():
                # Il nodo sta cercando di unirsi alla chat con il mio stesso nickname
                send_connection_refused_message(peer, joiner_address)
            else:
                send_discovery_query(peer, id_mittente)

        elif msg_type == "DISCOVERY_QUERY":
            msg = msg[0]
            discovery_query_handler(peer, id_mittente, id_destinatario, msg, joiner_address)

        elif msg_type == "DISCOVERY_ANSWER":
            msg = msg[0]
            discovery_answer_handler(peer, id_mittente, id_destinatario, msg, joiner_address)

        elif msg_type == "STANDARD":
            # messaggio di tipo standard
            msg = msg[0]
            standard_message_handler(peer, id_mittente, id_destinatario, msg)

        elif msg_type == "ACK":
            # messaggio di tipo ack
            msg = msg[0]
            ack_message_handler(peer, id_mittente, id_destinatario, msg)

        elif msg_type == "QUIT":
            print(f"l'utente {id_mittente} si è disconnesso..")
            peer.set_IP_next(msg[0])
            peer.set_PORT_next(msg[1])
        elif msg_type == "CHANGE_PREC":
            peer.set_IP_prec(msg[0])
            peer.set_PORT_prec(msg[1])
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

# Se specifico ip e porta del nodo a cui voglio connettermi allora mi sto connettendo ad un anello già
# esistente. Altrimenti sono il primo di un nuovo anello, per cui la procedura di join non deve essere
# avviata.
my_node_id, ip_next, port_next = (None, None, None)
if args.f:
    received_message = False  # Variabile che userò per verificare la ricezione di una risposta al messaggio di join
    # Variabili per l'indirizzo del nodo che conosco nel ring, a cui dovrò inviare il messaggio di JOIN
    ip_prec, port_prec = args.f
    port_prec = int(port_prec)

    # La procedura di JOIN parte da qui:
    # Mando messaggio di join
    send_join_message(ip_prec, port_prec, args.nickname, socket_receive)
    # Aspetto un messaggio DISCOVERY QUERY O ANSWER
    while not received_message:
        data, address = socket_receive.recvfrom(1024)
        message = data.decode()
        msg_type, id_mittente, id_destinatario, msg = fmt.unpacking(message).values()
        if msg_type == "CONNECTION_REFUSED":
            received_message = True
            raise ValueError('Il nickname inserito è già in uso. Riprovare con un nickname diverso.')
        elif msg_type == "CONNECTION_ACCEPTED":
            # se la procedura va a buon fine assegno il nickname scelto. Altrimenti termino il processo.
            # bisognerà inoltre impostare i valori di ip e porta del nodo successivo
            my_node_id = format_name(args.nickname)
            ip_next, port_next = msg
            received_message = True
else:  # Se sono il primo di un nuovo ring
    my_node_id = format_name(args.nickname)
    ip_prec = args.IP_socket_rec
    port_prec = args.PORT_socket_rec
    ip_next = args.IP_socket_rec
    port_next = args.PORT_socket_rec

peer = Nodo(my_node_id, ip_next, port_next, ip_prec, port_prec, socket_send, socket_receive)

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
