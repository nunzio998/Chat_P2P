import socket


def get_my_ip() -> str:
    socket_temp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    socket_temp.settimeout(0)
    try:
        # doesn't even have to be reachable
        socket_temp.connect(('8.8.8.8', 1))
        my_host_IP = socket_temp.getsockname()[0]
    except Exception:
        my_host_IP = '127.0.0.1'
    socket_temp.close()
    return my_host_IP
