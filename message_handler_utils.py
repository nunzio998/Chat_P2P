from Nodo import Nodo


def ack_message_handler(peer: Nodo, id_destinatario, message, socket_send):
    """
    Funzione che ha il compito gestire i messaggi di tipo ACK.
    :param peer:
    :param id_mittente:
    :param id_destinatario:
    :param message:
    :param socket_send:
    :return:
    """

    if id_destinatario == peer.get_nickname():
        # Il messaggio è indirizzato a me, stampo il messaggio di ack
        print(message + "\n")
    else:
        # il messaggio non è diretto a me allora lo inoltro
        # al prossimo nodo, continua il giro.
        socket_send.sendto(message.encode(), (peer.get_IP_next(), peer.get_PORT_next()))


def standard_message_handler(peer: Nodo, id_mittente, id_destinatario, message, socket_send):
    """
    Funzione che ha il compito gestire i messaggi di tipo STANDARD.
    :param peer:
    :param id_mittente:
    :param id_destinatario:
    :param message:
    :param socket_send:
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
        ack_msg = "ACK" + "#" + peer.get_nickname() + "#" + id_destinatario + "#" + f"{id_destinatario} ha ricevuto correttamente il messaggio"
        socket_send.sendto(ack_msg.encode(), peer.get_IP_next(), peer.get_PORT_next())

    else:
        # il messaggio non è stato mandato da me e non è diretto a me
        # allora lo inoltro al prossimo nodo, continua il giro.
        socket_send.sendto(message.encode(), (peer.get_IP_next(), peer.get_PORT_next()))
