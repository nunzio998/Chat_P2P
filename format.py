class Formatting:
    sep_packet = "§"
    sep_payload = "£"

    @staticmethod
    def packing(tipo, id_mittente, id_destinatario, *payload) -> str:
        """

        :param tipo:
        :param id_mittente:
        :param id_destinatario:
        :param payload:
        :return:
        """
        msg = "".join(str(el) + Formatting.sep_payload for el in payload)[0:-1]
        return str(tipo) + Formatting.sep_packet + str(id_mittente) + Formatting.sep_packet + str(id_destinatario) + \
            Formatting.sep_packet + msg

    @staticmethod
    def unpacking(messaggio: str) -> dict:
        """

        :param messaggio:
        :return:
        """
        if type(messaggio) is not str:
            raise TypeError("Il pacchetto deve essere di tipo stringa")
        campi = messaggio.split(Formatting.sep_packet)
        msg = tuple(campi[-1].split(Formatting.sep_payload))
        if len(msg) == 1: msg = msg[0]
        return {"Tipo": campi[0], "id_mittente": campi[1], "id_destinatario": campi[2], "payload": msg}
