# Chat P2P
Con lo sviluppo di questo progetto vogliamo realizzare un' applicazione di chat peer-to-peer (P2P) che consenta a un gruppo di utenti di comunicare tra loro direttamente, senza al necessità di un server centrale. In questa architettura decentralizzata, ogni partecipante svolge il ruolo sia di client che di server, consentendo la condivisione delle risorse e la comunicazione diretta tra i nodi della rete al fine di creare un ambiente sicuro, affidabile e robusto.

## Implementazione

### Definizione struttura del Peer
Ogni peer della rete è rappresentato dalle seguenti caratteristiche:
- **Nickname**: Composto da ...
- **Socket di invio messaggi**: ... IP: ... PORTA: ...
- **Socket di ricezione messaggi**: ... IP: ... PORTA: ...
- **...**: ...
### Tipologie di messaggi
Per la corretta gestione della chat sono stati implementate diverse tipologie di messaggio al fine di gestire varie funzionalità

| TIPOLOGIA DI MESSAGGIO | DESCRIZIONE                                                                                                            |
|------------------------|------------------------------------------------------------------------------------------------------------------------|
| STANDARD               | Messaggio inviato tra i nodi del network per la normale comunicazione.                                                 |
| JOIN                   | Messaggio inviato da un nuovo nodo per richiedere di unirsi al network.                                                |
| DISCOVERY_QUERY        | Messaggio inviato per verificare la disponibilità di un nickname durante la procedura di JOIN.                         |
| DISCOVERY_ANSWER       | Messaggio inviato se il nickname del nodo che vuole collegarsi sia già occupato dal un altro nodo.                     |
| TERMINATE              | Messaggio inviato (quando digito quit) dal thread di invio a quello di gestione messaggi per farlo terminare.          |
| ACK                    | Messaggio di conferma di ricezione. Viene inviato automaticamente come risposta a un messaggio ricevuto correttamente. |
| CONNECTION_ACCEPTED    | Messaggio inviato per accettare una richiesta di JOIN e fornire le informazioni di connessione.                        |
| CHANGE_PREC            | Messaggio inviato per comunicare al nodo successivo di impostare un nuovo nodo come predecessore.                      |
| CHANGE_NEXT            |                                                                                                                        |
| CONNECTION_REFUSED     | Messaggio inviato per rifiutare una richiesta di JOIN a causa di un nickname non disponibile.                          |
| QUIT                   | Messaggio inviato da un nodo per indicare la sua volontà di uscire dal network.                                        |
### Parsing
Il parsing coinvolge diversi parametri:
- nickname: identifica il nickname che l'host vuole e che sarà verificato con la procedura di JOIN. Nel caso in cui l'host sia il primo di un nuovo ring invece viene assegnato e basta.
- IP_socket_rec: ip della socket di ricezione messaggi.
- PORT_socket_rec: porta della socket di ricezione messaggi.
- IP_socket_send: ip della socket di invio messaggi.
- PORT_socket_send: porta della socket di invio messaggi.
- -f IP_prec PORT_prec: flag e parametri che se specificati indicano che il nodo si aggiungerà ad un ring già esistente. In particolare invierà un messaggio di JOIN all'indirizzo (IP_prec, PORT_prec) col quale partirà la procedura.

Il commando da digitare su CLI per creare un host quindi è il seguente:
```
python peer.py nickname IP_socket_rec PORT_socket_rec IP_socket_send PORT_socket_send -f IP_prec PORT_prec  
```

### Procedura di JOIN
La procedura di JOIN serve a permettere ad un nodo di unirsi ad un ring e a verificare che il nickname che ha scelto per unirsi sia effettivamente disponibile e non già usato da un altro nodo nel ring.
Quando un host X vuole unirsi ad una rete (flag e parametri specificati) per prima cosa avvia la procedura inviando un messaggio di JOIN con mittente uguale al nickname che ha scelto al nodo Y che si trova 
all'indirizzo (IP_prec, PORT_prec) (che deve conoscere a priori per potersi connettere).
Una volta ricevuto il messaggio di JOIN Y fa partire la procedura di DISCOVERY con la quale si verifica se il nickname scelto da X è disponibile o meno. In base dunque al successo di questa procedura X riceverà 
un messaggio di risposta da Y di due possibili tipologie:
- CONNECTION_REFUSED: Il nickname non è disponibile. Il processo viene interrotto e si dovrà riprovare lanciando nuovamente lo script con un altro nickname.
- CONNECTION_ACCEPTED: La procedura di DISCOVERY è andata a buon fine. Ora, sia Z il nodo successivo ad Y, Y manderà a X un CONNECTION_ACCEPTED con l'ip e la porta di Z da impostare come suoi successivi (in precedenza X aveva già impostato Y come suo predecessore). 
Dopodiché Y invierà un messaggio a Z con ip e porta di X dicendogli di impostarlo come suo precedente. Infine Y imposterà X come suo successivo. L'inserimento del nodo è completo.

N.B: L’inserimento del nuovo host avviene sempre tra il nodo che riceve il join e il successivo. 


### Procedura di Discovery
La procedura di DISCOVERY viene avviata da un nodo Y che ha appena ricevuto un messaggio di JOIN da un nodo X che vuole aggiungersi al suo ring con un dato nickname. X quindi fa partire un messaggio di tipo DISCOVERY_QUERY con destinatario proprio
il nickname scelto da X. Se, facendo il giro del ring, il messaggio incontra un nodo T che ha quel nickname, quest'ultimo cambia la tipologia del messaggio in DISCOVERY_ANSWER ad indicare che quel nickname non è disponibile e lo invia ad Y. 
Dunque una volta che X invia nel ring il DISCOVERY_QUERY possono accadere sostanzialmente due cose:
1) Il messaggio torna invariato ad Y dopo aver fatto tutto il giro del ring, questo significa che il nickname scelto da X è libero. La procedura va a buon fine.
2) X riceve un DISCOVERY_ANSWER, il che significa che il nickname è già in uso. La procedura da esito negativo.
### Procedura di Acknowledge

### Procedura di Disconnessione


## Running Info
Per eseguire il programma bisognerà portarsi nella directory del progetto per poi eseguire il seguente comando nel caso si voglia creare una nuova rete:
```
python peer.py numero01 8000 8001
```
Altrimenti il seguente comando nel caso ci si voglia unire ad una rete già esistente:
```
 python peer.py numero02 8010 8011 -f localhost 8000
```
Una volta eseguito, all'utente verrà chiesto di specificare i seguenti input:
  * A chi si vuole inviare un messaggio, specificando il nickname.
  * Il messaggio da inviare.


## Vulnerabilità

- MITM
- Disconnessione imprevista
- Scalabilità
- Tolleranza ai guasti
- Privacy e sicurezza


## Sviluppi Futuri
- Architettura a anello con ridondanza:
  - Ogni nodo è collegato al suo vicino immediato e al vicino del vicino per garantire un percorso alternativo in caso di guasto o disconnessione imprevista di un peer della rete.

- Comunicazione bidirezionale per l'aumento dell'efficienza:
  - I nodi possono inviare e ricevere dati simultaneamente, migliorando l'efficienza complessiva della rete.

- Ping continui per il monitoraggio dell'attività dei nodi:
  - I nodi inviano ping continui agli altri nodi per verificare se sono attivi o caduti, consentendo una gestione reattiva dei guasti.

- Crittografia e hashing per la sicurezza dei dati:
  - Il mittente utilizza la chiave pubblica del destinatario per crittografare i dati.
  - Ogni hop nel percorso può provare a decriptare i dati utilizzando la propria chiave privata per verificare se sono il destinatario legittimo.
  - L'utilizzo di algoritmi di hashing per garantire l'integrità dei dati durante la trasmissione.
