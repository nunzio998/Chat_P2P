import socket
import threading


# Funzione per la gestione dei messaggi ricevuti
def handle_message(sender, message):
    print(f"Messaggio ricevuto da {sender}: {message}")


# Funzione per inviare un messaggio al nodo successivo nel ring
def send_message():
    message = my_node_id + "#" + input()
    print(message)
    socket_send.sendto(message.encode(), (ip_next, port_next))


# Funzione per la gestione dei messaggi ricevuti
def message_handler():
    while True:
        data, address = socket_receive.recvfrom(1024)
        message = data.decode()
        id_, msg = message.split("#")

        if message == "JOIN":
            # Gestione del messaggio di join da un nuovo nodo
            # Invia i tuoi ip_next e port_next al nuovo nodo
            # Avvia la procedura di discovery per trovare un nickname disponibile
            # Assegna il nickname disponibile al nuovo nodo
            pass
        else:
            handle_message(id_, msg)


# Crea un socket per la ricezione dei messaggi
socket_receive = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socket_receive.bind(('localhost', 8000))

# Crea un socket per l'invio dei messaggi
socket_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socket_send.bind(('localhost', 8001))

# Variabili per l'indirizzo del nodo successivo nel ring
ip_next = 'localhost'
port_next = 8002
my_node_id = "2"

# Creo e avvio il thread per la gestione dei messaggi ricevuti
receive_message_thread = threading.Thread(target=message_handler, args=())
receive_message_thread.start()

# Creo e avvio il thread per la gestione dell'invio dei messaggi
send_message_thread = threading.Thread(target=send_message, args=())
send_message_thread.start()

# Invio del messaggio di join al nodo successivo nel ring
# send_message("JOIN")

# Invio di un messaggio al nodo successivo nel ring
# send_message("Ciao!")

# Attendi la terminazione dei thread
receive_message_thread.join()
send_message_thread.join()

# Chiudi i socket
socket_receive.close()
socket_send.close()
