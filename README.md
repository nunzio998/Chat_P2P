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
| ACK                    | Messaggio di conferma di ricezione. Viene inviato automaticamente come risposta a un messaggio ricevuto correttamente. |
| CONNECTION_ACCEPTED    | Messaggio inviato per accettare una richiesta di JOIN e fornire le informazioni di connessione.                        |
| CONNECTION_REFUSED     | Messaggio inviato per rifiutare una richiesta di JOIN a causa di un nickname non disponibile.                          |
| CHANGE_PREC            | Messaggio inviato per comunicare al nodo successivo di impostare un nuovo nodo come predecessore.                      |
| QUIT                   | Messaggio inviato da un nodo per indicare la sua volontà di uscire dal network.                                        |
### Parsing

### Procedura di JOIN

### Procedura di Discovery

### Procedura di Acknowledge

### Procedura di Disconnessione


## Running Info
Per eseguire il programma bisognerà portarsi nella directory del progetto per poi eseguire il seguente comando nel caso si voglia creare una nuova rete:
```
python peer.py .................
```
Altrimenti il seguente comando nel caso ci si voglia unire ad una rete già esistente:
```
python peer.py .................
```
Una volta eseguito, all'utente verrà chiesto di specificare i seguenti input:
  * 
  * 


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
