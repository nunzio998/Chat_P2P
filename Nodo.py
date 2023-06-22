import socket
import time
import message_handler_utils as mhu


class Nodo:

    def __init__(self, nick, IP_next, PORT_next, IP_prec, PORT_prec, IP_nn, PORT_nn, socket_send: socket,
                 socket_recv: socket):
        self.nickname = nick
        self.IP_next = IP_next
        self.PORT_next = PORT_next
        self.IP_prec = IP_prec
        self.PORT_prec = PORT_prec
        self.IP_nextnext = IP_nn
        self.PORT_nextnext = PORT_nn
        self.socket_send = socket_send
        self.socket_recv = socket_recv
        # attributi per gestione disconnessione involontaria
        self.next_available = True
        self.__timer__ = 2

    # Getter per il nickname
    def get_nickname(self):
        return self.nickname

    def get_socket_send(self):
        return self.socket_send

    def get_socket_recv(self):
        return self.socket_recv

    # Getter per IP_next
    def get_IP_next(self):
        return self.IP_next

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

    def get_IP_nextnext(self):
        return self.IP_nextnext

    # Setter per IP_next
    def set_IP_nextnext(self, new_IP_nn):
        self.IP_nextnext = new_IP_nn

    # Getter per PORT_next
    def get_PORT_nextnext(self):
        return self.PORT_nextnext

    # Setter per PORT_next
    def set_PORT_nextnext(self, new_PORT_nn):
        self.PORT_nextnext = new_PORT_nn

    def sendto_next(self, message: str):
        if self.IP_next == self.IP_nextnext and self.PORT_next == self.PORT_nextnext:
            self.socket_send.sendto(message.encode(), (self.get_IP_next(), self.get_PORT_next()))
            return
        if not self.next_available:
            print("aspetto il timer")
            time.sleep(self.__timer__)
        if self.next_available:
            self.socket_send.sendto(message.encode(), (self.get_IP_next(), self.get_PORT_next()))
            self.next_available = False
        else:
            self.riconnection_procedure()

    def sendto_prec(self, message: str):
        self.socket_send.sendto(message.encode(), (self.get_IP_prec(), self.get_PORT_prec()))

    def receive(self) -> tuple:
        print("receive")
        #time.sleep(2)
        return self.socket_recv.recvfrom(1024)

    def set_availability_next(self):
        print("set ava next")
        self.next_available = True

    def riconnection_procedure(self):
        print("non dovrei entrare mai qui")
        self.IP_next = self.IP_nextnext
        self.PORT_next = self.PORT_nextnext
        mhu.send_change_prec_message(self, (self.get_socket_recv().getsockname()[0], self.get_socket_recv().getsockname()[1]))
        mhu.send_change_nextnext_message(self, (self.IP_next, self.PORT_next))
        self.next_available = True
