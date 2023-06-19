import socket
class Nodo:

    def __init__(self, nick, IP_next, PORT_next, IP_prec, PORT_prec, socket_send: socket, socket_recv: socket):
        self.nickname = nick
        self.IP_next = IP_next
        self.PORT_next = PORT_next
        self.IP_prec = IP_prec
        self.PORT_prec = PORT_prec
        self.socket_send = socket_send
        self.socket_recv = socket_recv

    # Getter per il nickname
    def get_nickname(self):
        return self.nickname

    # Getter per IP_next
    def get_IP_next(self):
        return self.IP_next

    def get_socket_send(self):
        return self.socket_send

    def get_socket_recv(self):
        return self.socket_recv

    # Setter per IP_next
    def set_IP_next(self, new_IP_next):
        self.IP_next = new_IP_next

    # Getter per PORT_next
    def get_PORT_next(self):
        return self.PORT_next

    # Setter per PORT_next
    def set_PORT_next(self, new_PORT_next):
        self.PORT_next = new_PORT_next

    # Getter per IP_prec
    def get_IP_prec(self):
        return self.IP_prec

    # Setter per IP_prec
    def set_IP_prec(self, new_IP_prec):
        self.IP_prec = new_IP_prec

    # Getter per PORT_prec
    def get_PORT_prec(self):
        return self.PORT_prec

    # Setter per PORT_prec
    def set_PORT_prec(self, new_PORT_prec):
        self.PORT_prec = new_PORT_prec
