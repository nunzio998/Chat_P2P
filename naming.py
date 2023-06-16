import re


def check_name(name: str) -> bool:
    """
    Funzione che controlla che la stringa in ingresso rispetti il formato XXXXXXdd, in cui X è qualsiasi carattere,
    maiuscolo o minuscolo, dell'alfabeto inglese da A a Z, e d rappresenta una qualsiasi cifra da 0 a 9.

    :param name:
    :return: restituisce true se la stringa rappresenta un nome valido
    """
    if re.match(r'^[A-Za-z]{6}\d{2}$', name):
        return True
    return False


def format_name(name: str) -> str:
    """
    Formatta la stringa in ingresso in XXXXXXdd con X carattere maiuscolo

    :param name:
    :return:
    """
    return name.upper()
