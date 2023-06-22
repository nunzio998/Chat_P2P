import socket
import threading
import argparse
import time

from naming import *
from message_handler_utils import *
from Nodo import Nodo
import psutil
from format import Formatting as fmt
import get_ip


# Funzione per inviare un messaggio al nodo successivo nel ring
def send_message():
    """
    La funziona ha lo scopo d'inviare messaggi standard dei nodi lungo la rete ad anello.
    Accetta messaggi in ingresso dall'utente con i quali compone il messaggio da inviare che avrà
    il seguente formato: 'TIPO_MESSAGGIO§ID_MITTENTE§ID_DESTINATARIO§MESSAGGIO'
    :return:
    """

    termination_flag = False
    while not termination_flag:
        print("--------------------------------")
        destinatario = input("A chi vuoi mandare un messaggio?\n")

        if destinatario.upper() == "QUIT":
            # disconnessione volontaria
            message_back = fmt.packing("CHANGE_NEXT", peer.get_nickname(), "", peer.get_IP_next(), peer.get_PORT_next())
            peer.sendto_prec(message_back)
            message_forward = fmt.packing("CHANGE_PREC", peer.get_nickname(), "", peer.get_IP_prec(),
                                          peer.get_PORT_prec())
            peer.sendto_next(message_forward)
            # Invio il messaggio alla socket che riceve i messaggi per terminare anche quel thread
            # Termino il thread di invio messaggi
            message_close = fmt.packing("TERMINATE", peer.get_nickname(), "", "", "")
            socket_send.sendto(message_close.encode(), peer.get_socket_recv().getsockname())
            print("Disconnessione..")
            termination_flag = True
        elif check_name(destinatario):
            message = fmt.packing("STANDARD", peer.get_nickname(), destinatario.upper(), input("\nMessaggio:\n"))
            peer.sendto_next(message)
        else:
            print("Il nickname indicato non è valido.")
        time.sleep(2)


def send_join_message(nodo: Nodo):
    try:
        message_join = fmt.packing("JOIN", nodo.get_nickname(), "", nodo.socket_recv.getsockname()[0],
                                   nodo.socket_recv.getsockname()[1])
        nodo.sendto_prec(message_join)
        nodo.socket_send.settimeout(2)
        data, address = nodo.socket_send.recvfrom(1024)
        print(data.decode())
    except Exception:
        # Nessuna risposta ricevuta, l'indirizzo IP o la porta potrebbero non essere disponibili
        raise ValueError(f"L'indirizzo IP {nodo.get_IP_prec()} e/o la porta {nodo.get_PORT_prec()} potrebbero non "
                         f"essere disponibili.")


# Funzione per la gestione dei messaggi ricevuti
def message_handler():
    termination_flag = False

    joiner_address = None
    while not termination_flag:
        data, address = peer.receive()
        packet = data.decode()
        # print(packet, address)
        msg_type, id_mittente, id_destinatario, msg = fmt.unpacking(packet).values()

        if not msg_type == "NOTICE":
            packet = fmt.packing("NOTICE", "", "", "")
            peer.sendto_prec(packet)

        if msg_type == "JOIN":
            # Assegna il nickname se disponibile al nuovo nodo
            peer.socket_send.sendto("In connessione..".encode(), address)
            joiner_address = msg
            if id_mittente == peer.get_nickname():  # Il joiner ha proposto il mio stesso nickname
                # mando un CONNECTION_REFUSED
                send_connection_refused_message(peer, joiner_address)
            else:
                # avvio la procedura di discovery per vedere se il nickname è disponibile
                send_discovery_query(peer, id_mittente)

        elif msg_type == "DISCOVERY_QUERY":
            discovery_query_handler(peer, id_mittente, id_destinatario, msg[0], joiner_address)

        elif msg_type == "DISCOVERY_ANSWER":
            discovery_answer_handler(peer, id_mittente, id_destinatario, msg[0], joiner_address)

        elif msg_type == "STANDARD":
            standard_message_handler(peer, id_mittente, id_destinatario, msg[0])

        elif msg_type == "ACK":
            ack_message_handler(peer, id_mittente, id_destinatario, msg[0])

        elif msg_type == "CHANGE_NEXT":
            peer.set_IP_next(msg[0])
            peer.set_PORT_next(msg[1])

        elif msg_type == "CHANGE_PREC":
            peer.set_IP_prec(msg[0])
            peer.set_PORT_prec(msg[1])
            send_change_nextnext_message(peer, (peer.get_IP_next(), peer.get_PORT_next()))

        elif msg_type == "CHANGE_NEXTNEXT":
            peer.set_IP_nextnext(msg[0])
            peer.set_PORT_nextnext(msg[1])

        elif msg_type == "TERMINATE" and id_mittente == peer.get_nickname():
            # è arrivato da me stesso un messaggio di tipo terminate
            termination_flag = True

        elif msg_type == "NOTICE":
            peer.set_availability_next()

        else:  # messaggio non riconosciuto
            print("il formato del messaggio {} non è riconosciuto\n".format(packet))


my_host_ip = get_ip.get_my_ip()

# Faccio il parsing degli argomenti passati in input dall'utente:
parser = argparse.ArgumentParser(description="Parametri descrittivi del peer")
parser.add_argument("nickname", type=str, help="nickname identificativo con cui l'host vuole aggiungersi")
parser.add_argument("-IP_socket_rec", type=str, default=my_host_ip, help="IP della porta di ricezione dei messaggi")
parser.add_argument("PORT_socket_rec", type=int, help="Porta di ricezione dei messaggi")
parser.add_argument("-IP_socket_send", type=str, default=my_host_ip, help="IP della porta di invio dei messaggi")
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
peer = Nodo(format_name(args.nickname), None, None, None, None, None, None, socket_send, socket_receive)
my_node_id, ip_next, port_next = (None, None, None)
if args.f:  # se mi collego ad un ring esistente
    received_message = False  # Variabile che userò per verificare la ricezione di una risposta al messaggio di join
    # Setto l'indirizzo del nodo che conosco nel ring, a cui dovrò inviare il messaggio di JOIN
    peer.set_IP_prec(args.f[0])
    peer.set_PORT_prec(int(args.f[1]))

    # Procedura di JOIN:
    # Mando messaggio di join
    send_join_message(peer)
    # Aspetto un messaggio CONNECTION_REFUSED O CONNECTION_ACCEPTED
    data, address = peer.receive()
    packet = data.decode()
    msg_type, id_mittente, id_destinatario, msg = fmt.unpacking(packet).values()
    if msg_type == "CONNECTION_REFUSED":
        raise ValueError('Il nickname inserito è già in uso. Riprovare con un nickname diverso.')
    elif msg_type == "CONNECTION_ACCEPTED":
        # imposto i valori di ip e porta del nodo successivo
        peer.set_IP_next(msg[0])
        peer.set_PORT_next(msg[1])
        data, address = peer.receive()
        msg_type, id_mittente, id_destinatario, msg = fmt.unpacking(data.decode()).values()
        if msg_type == "CHANGE_NEXTNEXT":
            # imposto i valori di ip e porta del nodo nextnext
            peer.set_IP_nextnext(msg[0])
            peer.set_PORT_nextnext(msg[1])
        else:
            raise Exception("C'è stato un errore durante la connessione. Riprovare.")
    else:
        raise Exception("C'è stato un errore durante la connessione. Riprovare.")
else:  # Se sono il primo di un nuovo ring
    peer.set_IP_prec(args.IP_socket_rec)
    peer.set_PORT_prec(args.PORT_socket_rec)
    peer.set_IP_next(args.IP_socket_rec)
    peer.set_PORT_next(args.PORT_socket_rec)
    peer.set_IP_nextnext(args.IP_socket_rec)
    peer.set_PORT_nextnext(args.PORT_socket_rec)

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
