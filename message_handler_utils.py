from Nodo import Nodo
from format import Formatting as fmt


def ack_message_handler(peer: Nodo, id_destinatario, message):
    """
    Funzione che ha il compito gestire i messaggi di tipo ACK.
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
        peer.get_socket_send.sendto(message.encode(), (peer.get_IP_next(), peer.get_PORT_next()))


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
        peer.get_socket_send.sendto(ack_msg.encode(), peer.get_IP_next(), peer.get_PORT_next())

    else:
        # il messaggio non è stato mandato da me e non è diretto a me
        # allora lo inoltro al prossimo nodo, continua il giro.
        peer.get_socket_send.sendto(message.encode(), (peer.get_IP_next(), peer.get_PORT_next()))


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
    if id_mittente == peer.get_nickname():
        # il mittente sono io, ma non sono il destinatario
        # questo vuol dire che il nickname che ha scelto è disponibile

        # Mando un connection accepted al joiner con le info sui miei ip_next e port_next
        send_connection_accepted_message(peer, joiner_address, id_destinatario)
        # mando un messaggio al mio attuale successivo per dirgli di impostare il joiner come suo precedente
        send_change_prec_message(peer, joiner_address)
        # e imposto il joiner come mio successivo.
        peer.set_IP_next(joiner_address[0])
        peer.set_PORT_next(joiner_address[1])

    elif id_destinatario == peer.get_nickname():
        # Il messaggio è indirizzato a me, quindi il nickname è occupato
        discovery_answer_msg = fmt.packing("DISCOVERY_ANSWER", peer.get_nickname(), id_mittente,
                                           f"{id_destinatario} è già in uso")
        peer.get_socket_send.sendto(discovery_answer_msg.encode(), peer.get_IP_next(), peer.get_PORT_next())

    else:
        # il messaggio non è stato mandato da me e non è diretto a me
        # allora lo inoltro al prossimo nodo, continua il giro.
        peer.get_socket_send.sendto(msg.encode(), (peer.get_IP_next(), peer.get_PORT_next()))


def discovery_answer_handler(peer, id_destinatario, msg, joiner_address):
    """
    Funzione che ha il compito gestire i messaggi di tipo DISCOVERY_ANSWER.
    :param joiner_address:
    :param peer:
    :param id_destinatario:
    :param msg:
    :return:
    """
    if id_destinatario == peer.get_nickname():
        # Il destinatario sono io. Questo vuol dire che devo comunicare al nodo
        # che mi ha chiesto di unirsi un messaggio di CONNECTION_REFUSED poiché
        # il nickname che ha scelto non è disponibile

        # L'id destinatario non è disponibile. Devo mandare un messaggio connection refused.
        send_connection_refused_message(peer, joiner_address)

    else:
        # il messaggio non è stato mandato da me e non è diretto a me
        # allora lo inoltro al prossimo nodo, continua il giro fino al
        # nodo che ha fatto partire la procedura di JOIN.
        peer.get_socket_send.sendto(msg.encode(), (peer.get_IP_next(), peer.get_PORT_next()))


def send_discovery_query(peer: Nodo, id_mittente, joiner_address):
    """
    Funzione che ha il compito d'inviare un messaggio di tipo DISCOVERY_QUERY
    :param joiner_address:
    :param peer:
    :param id_mittente:
    :return:
    """
    if id_mittente == peer.get_nickname():
        # Il nodo sta cercando di unirsi alla chat con il mio stesso nickname
        send_connection_refused_message(peer, joiner_address)

    else:
        discovery_query_msg = fmt.packing("DISCOVERY_QUERY", peer.get_nickname(), id_mittente,
                                          f"{id_mittente} vorrebbe unisrsi alla chat")
        peer.get_socket_send.sendto(discovery_query_msg.encode(), (peer.get_IP_next(), peer.get_PORT_next()))


def send_connection_accepted_message(peer: Nodo, join_node_address, joiner_nickname):
    message_accepted = fmt.packing("CONNECTION_ACCEPTED", peer.get_nickname(), joiner_nickname, peer.get_IP_next(),
                                   peer.get_PORT_next())
    peer.get_socket_send.sendto(message_accepted.encode(), join_node_address)


def send_connection_refused_message(peer: Nodo, address):
    message_refused = fmt.packing("CONNECTION_REFUSED", peer.get_nickname(), "", "")
    peer.get_socket_send.sendto(message_refused.encode(), address)


def send_change_prec_message(peer: Nodo, addr_joiner):
    message_change_prec = fmt.packing("CHANGE_PREC", peer.get_nickname(), "", addr_joiner[0], addr_joiner[1])
    peer.get_socket_send.sendto(message_change_prec.encode(), (peer.get_IP_next(), peer.get_PORT_next()))
