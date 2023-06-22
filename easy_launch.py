import subprocess
import sys

import get_ip


def launch_terminal(command):
    if sys.platform.startswith('win'):
        subprocess.Popen(['start', 'cmd', '/k', command], shell=True)
    elif sys.platform.startswith('darwin'):
        subprocess.Popen(['open', '-a', 'Terminal', command])
    elif sys.platform.startswith('linux'):
        subprocess.Popen(['x-terminal-emulator', '-e', 'bash', '-c', command])
    else:
        print("Non supportato: impossibile aprire un nuovo terminale.")


ip = get_ip.get_my_ip()


def main():
    command = f'python peer.py matgar00 8000 8001'
    launch_terminal(command)

    command = f'python peer.py frapin98 8010 8011 -f {ip} 8000'
    launch_terminal(command)

    command = f'python peer.py gabgio00 8020 8021 -f {ip} 8010'
    launch_terminal(command)

    command = f'python peer.py mitmxx99 8030 8031 -f {ip} 8000'
    launch_terminal(command)


if __name__ == '__main__':
    main()
