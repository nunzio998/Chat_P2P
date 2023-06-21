from Nodo import Nodo
from format import Formatting as fmt


def standard_message_handler(peer: Nodo, id_mittente, id_destinatario, message):
    """
    Funzione che ha il compito gestire i messaggi di tipo STANDARD.
    :param peer:
    :param id_mittente:
    :param id_destinatario:
    :param message:
    :return:
    """

    if id_mittente == peer.get_nickname() and id_destinatario != peer.get_nickname():
        # il mittente sono io, ma non sono il destinatario
        # questo vuol dire che ho inviato un messaggio a un destinatario che non esiste
        print("Non esiste un nodo con nickname {}\n".format(id_destinatario))

    elif id_destinatario == peer.get_nickname():
        # Il messaggio è indirizzato a me, quindi lo gestisco
        print(f"Messaggio ricevuto da {id_mittente}: {message}\n")

        # invio un messaggio di ack al mittente
        ack_msg = fmt.packing("ACK", peer.get_nickname(), id_mittente, f"{id_destinatario} ha ricevuto correttamente "
                                                                       f"il messaggio")
        peer.get_socket_send().sendto(ack_msg.encode(), (peer.get_IP_next(), peer.get_PORT_next()))

    else:
        # il messaggio non è stato mandato da me e non è diretto a me
        # allora lo inoltro al prossimo nodo, continua il giro.
        std_message = fmt.packing("STANDARD", id_mittente, id_destinatario, message)
        peer.get_socket_send().sendto(std_message.encode(), (peer.get_IP_next(), peer.get_PORT_next()))


def ack_message_handler(peer: Nodo, id_mittente, id_destinatario, message):
    """
    Funzione che ha il compito gestire i messaggi di tipo ACK.
    :param id_mittente:
    :param peer:
    :param id_destinatario:
    :param message:
    :return:
    """

    if id_destinatario == peer.get_nickname():
        # Il messaggio è indirizzato a me, stampo il messaggio di ack
        print(message + "\n")
    else:
        # il messaggio non è diretto a me allora lo inoltro
        # al prossimo nodo, continua il giro.
        ack_msg = fmt.packing("ACK", id_mittente, id_destinatario, message)
        peer.get_socket_send().sendto(ack_msg.encode(), (peer.get_IP_next(), peer.get_PORT_next()))


def discovery_query_handler(peer, id_mittente, id_destinatario, msg, joiner_address):
    """
    Funzione che ha il compito gestire i messaggi di tipo DISCOVERY_QUERY.
    :param peer:
    :param id_mittente:
    :param id_destinatario:
    :param msg:
    :param joiner_address:
    :return:
    """
    if id_mittente == peer.get_nickname():  # il mittente sono io, ma non sono il destinatario
        # il nickname propost dal joiner è disponibile

        # Mando un connection accepted al joiner con le info sui miei ip_next e port_next
        send_connection_accepted_message(peer, joiner_address)
        # mando un messaggio al mio attuale successivo per dirgli di impostare il joiner come suo precedente
        send_change_prec_message(peer, joiner_address)
        # e imposto il joiner come mio successivo.
        peer.set_IP_next(joiner_address[0])
        peer.set_PORT_next(joiner_address[1])

    elif id_destinatario == peer.get_nickname():
        # Il messaggio è indirizzato a me, quindi il nickname è occupato
        packet = fmt.packing("DISCOVERY_ANSWER", peer.get_nickname(), id_mittente,
                             f"{peer.get_nickname()} è già in uso")
        peer.sendto_next(packet)

    else:
        # il messaggio non è stato mandato da me e non è diretto a me,
        # allora lo inoltro al prossimo nodo, continua il giro.
        packet = fmt.packing("DISCOVERY_QUERY", id_mittente, id_destinatario, msg)
        peer.sendto_next(packet)


def discovery_answer_handler(peer, id_mittente, id_destinatario, msg, joiner_address):
    """
    Funzione che ha il compito gestire i messaggi di tipo DISCOVERY_ANSWER.
    :param peer:
    :param id_mittente:
    :param id_destinatario:
    :param msg:
    :param joiner_address:
    :return:
    """
    if id_destinatario == peer.get_nickname():
        # Il destinatario sono io; il nickname proposto dal joiner non è disponibile
        # Mando al joiner un messaggio di CONNECTION_REFUSED
        send_connection_refused_message(peer, joiner_address)

    else:
        # il messaggio non è stato mandato da me e non è diretto a me, allora lo inoltro al prossimo nodo
        packet = fmt.packing("DISCOVERY_ANSWER", id_mittente, id_destinatario, msg)
        peer.sendto_next(packet)


def send_discovery_query(peer: Nodo, id_mittente):
    """
    Funzione che ha il compito d'inviare un messaggio di tipo DISCOVERY_QUERY
    :param peer:
    :param id_mittente:
    :return:
    """
    packet = fmt.packing("DISCOVERY_QUERY", peer.get_nickname(), id_mittente,
                         f"{id_mittente} vorrebbe unirsi alla chat")
    peer.get_socket_send().sendto(packet.encode(), (peer.get_IP_next(), peer.get_PORT_next()))


def send_connection_accepted_message(peer: Nodo, joiner: tuple):
    packet = fmt.packing("CONNECTION_ACCEPTED", peer.get_nickname(), "", peer.get_IP_next(),
                         peer.get_PORT_next())
    peer.get_socket_send().sendto(packet.encode(), joiner)


def send_connection_refused_message(peer: Nodo, joiner: tuple):
    packet = fmt.packing("CONNECTION_REFUSED", peer.get_nickname(), "", "")
    peer.get_socket_send().sendto(packet.encode(), joiner)


def send_change_prec_message(peer: Nodo, address):
    """

    :param peer:
    :param address: l'indirizzo con cui cambiare il prec del destinatario del messaggio
    :return:
    """
    packet = fmt.packing("CHANGE_PREC", peer.get_nickname(), "", address[0], address[1])
    peer.sendto_next(packet)
