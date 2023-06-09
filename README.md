# Chat P2P
Con lo sviluppo di questo progetto vogliamo realizzare un' applicazione di chat peer-to-peer (P2P) che consenta a un gruppo di utenti di comunicare tra loro direttamente, senza al necessità di un server centrale. In questa architettura decentralizzata, ogni partecipante svolge il ruolo sia di client che di server, consentendo la condivisione delle risorse e la comunicazione diretta tra i nodi della rete al fine di creare un ambiente sicuro, affidabile e robusto.

## Implementazione

### Definizione struttura del Peer
Ogni peer della rete è rappresentato dalle seguenti caratteristiche:
- **Nickname**: Il nickname è una stringa alfanumerica che identifica ogni host nel ring ed è dunque univoco. il nickname deve essere composto da sei lettere iniziali e due numeri finali.
- **Socket di invio messaggi**: Composta dall'ip e la porta che vengono specificati all'avvio dello script con i parametri -IP_socket_send e PORT_socket_send.
- **Socket di ricezione messaggi**: Composta dall'ip e la porta che vengono specificati all'avvio dello script con i parametri -IP_socket_rec e PORT_socket_rec.
- **Indirizzo del peer precedente**: Viene impostato all'inizio. Se specifico -f IP_prec PORT_prec sarà (IP_prec, PORT_prec) altrimenti trattandosi del primo nodo di un nuovo ring sarà identificato dalla socket di ricezione del nodo stesso (IP_socket_rec, PORT_socket_rec)
- **Indirizzo del peer successivo**: Viene impostato alla fine della procedura di JOIN se il nodo a cui ho mandato il messaggio di JOIN mi invia un CONNECTION_ACCEPTED con l'indirizzo del nodo da impostare come successivo. 
Quindi se non specifico -f IP_prec PORT_prec non partirà la procedura di JOIN, per cui sarà identificato dalla socket di ricezione del nodo stesso (IP_socket_rec, PORT_socket_rec)

### Tipologie di messaggi
Per la corretta gestione della chat sono stati implementate diverse tipologie di messaggio al fine di gestire varie funzionalità

| TIPOLOGIA DI MESSAGGIO | DESCRIZIONE                                                                                                                                                              | CAMPI DEL MESSAGGIO<br/>(per chiarezza, il payload viene qui rappresentato in formato fstring)                                                                                                                |
|------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| STANDARD               | Messaggio inviato tra i nodi del network per la normale comunicazione.                                                                                                   | ID_MIT=nodo che manda il messaggio<br/>ID_DEST=nodo destinatario del messaggio<br/>PAYLOAD=f"{messaggio}"                                                                                                     |
| JOIN                   | Messaggio inviato da un nuovo nodo per richiedere di unirsi al network.                                                                                                  | ID_MIT=id proposto dal joiner all'assistant<br/>ID_DEST=""<br/>PAYLOAD=f"{ip}£{port}" della socket di ricezione                                                                                               |
| DISCOVERY_QUERY        | Messaggio inviato per verificare la disponibilità di un nickname durante la procedura di JOIN.                                                                           | ID_MIT=nodo assistant, che manda la query<br/>ID_DEST=id del joiner proposto alla rete<br/>PAYLOAD=f"{id_joiner} vorrebbe unirsi alla chat"                                                                   |
| DISCOVERY_ANSWER       | Messaggio inviato se il nickname del nodo che vuole collegarsi sia già occupato dal un altro nodo.                                                                       | ID_MIT=id del joiner nella query, nonchè id del nodo che ha riscontrato la corrispondenza con il proprio nick<br/>ID_DEST=id dell'assistant, da cui proviene la query<br/>PAYLOAD=f"{id_joiner} è già in uso" |
| ACK                    | Messaggio di conferma di ricezione. Viene inviato automaticamente come risposta a un messaggio ricevuto correttamente.                                                   | ID_MIT=nodo che ha ricevuto il messaggio standard<br/>ID_DEST=nodo mittente del messaggio stadard<br/>PAYLOAD=f"{id_ricevitore} ha ricevuto correttamente il messaggio"                                       |
| CONNECTION_ACCEPTED    | Messaggio inviato per accettare una richiesta di JOIN e fornire le informazioni di connessione.                                                                          | ID_MIT=nodo assistant, che ha mandato la query<br/>ID_DEST=""<br/>PAYLOAD=f"{ip}£{port} del nodo successivo all'assistant, a cui il joiner si deve collegare                                                  |
| CONNECTION_REFUSED     | Messaggio inviato per rifiutare una richiesta di JOIN a causa di un nickname non disponibile.                                                                            | ID_MIT=nodo assitant, che ha mandato la query<br/>ID_DEST=""<br/>PAYLOAD=""                                                                                                                                   |
| CHANGE_PREC            | Messaggio inviato per comunicare al nodo successivo di impostare un nuovo nodo come predecessore.                                                                        | ID_MIT=nodo quitter<br/>ID_DEST=""<br/>PAYLOAD=f"{ip}£{port} del nodo precedente al quitter                                                                                                                   |
| CHANGE_NEXT            | Messaggio inviato per comunicare al nodo precedente di impostare un nuovo nodo come successivo.                                                                          | ID_MIT=nodo quitter<br/>ID_DEST=""<br/>PAYLOAD=f"{ip}£{port} del nodo successivo al quitter                                                                                                                   |
| TERMINATE              | Messaggio inviato (quando digito quit) dal thread di invio a quello di gestione messaggi per farlo terminare.                                                            | ID_MIT=nodo quitter<br/>ID_DEST=""<br/>PAYLOAD=""                                                                                                                                                             |
| NOTICE                 | Messaggio inviato in risposta ad un qualsiasi messaggio proveniente dal nodo prec. Serve a comunicare la propria attività e a innescare la procedura di gestione guasti. | ID_MIT=""<br/>ID_DEST=""<br/>PAYLOAD=""                                                                                                                                                                       |

### Struttura del messaggio
Ogni messaggio scambiato all'interno della rete è composto da quattro campi:
- **TIPOLOGIA**: identifica la tipologia di messaggio.
- **ID_MIT**: identifica il nodo che manda il messaggio.
- **ID_DEST**: identifica il nodo destinatario del messaggio.
- **PAYLOAD**: contiene il corpo del messaggio con le informazioni utili sulla base della tipologia.

### Parsing
Il parsing coinvolge diversi parametri:
- nickname: identifica il nickname che l'host vuole e che sarà verificato con la procedura di JOIN. Nel caso in cui l'host sia il primo di un nuovo ring invece viene assegnato e basta.
- -IP_socket_rec: ip della socket di ricezione messaggi, è opzionale e se non lo inserisco viene preso di default l'ip della macchina che lancia lo script.
- PORT_socket_rec: porta della socket di ricezione messaggi.
- -IP_socket_send: ip della socket di invio messaggi. Opzionale, se non lo inserisco viene preso di default l'ip della macchina che lancia lo script.
- PORT_socket_send: porta della socket di invio messaggi.
- -f IP_prec PORT_prec: flag e parametri che se specificati indicano che il nodo si aggiungerà ad un ring già esistente. In particolare invierà un messaggio di JOIN all'indirizzo (IP_prec, PORT_prec) col quale partirà la procedura.

Il commando da digitare su CLI per creare un host quindi è il seguente:
```
python peer.py nickname -IP_socket_rec <ip di ricezione> PORT_socket_rec -IP_socket_send <ip di invio> PORT_socket_send -f IP_prec PORT_prec  
```

### Procedura di JOIN
La procedura di JOIN serve a permettere ad un nodo di unirsi ad un ring e a verificare che il nickname che ha scelto per unirsi sia effettivamente disponibile e non già usato da un altro nodo nel ring.
Quando un host X (joiner) vuole unirsi ad una rete (parsing con flag e parametri specificati) per prima cosa avvia la procedura inviando un messaggio di JOIN con mittente uguale al nickname che ha scelto al nodo Y (assistant) che si trova 
all'indirizzo (IP_prec, PORT_prec) (che deve conoscere a priori per potersi connettere).
Una volta ricevuto il messaggio di JOIN, Y fa partire la procedura di DISCOVERY con la quale si verifica se il nickname scelto da X è disponibile o meno. La procedura di discovery è descritta in seguito.

In base al successo o insuccesso della procedura di DISCOVERY si differenziano due scenari:
- **Insuccesso**: il nickname non è disponibile; l'host assistant manda al joiner un messaggio di tipo CONNECTION_REFUSED; il processo joiner viene interrotto e si dovrà riprovare lanciando nuovamente lo script con un altro nickname;
- **Successo**: il nickname è disponibile; l'host assistant manda al joiner un messaggio di tipo CONNECTION_ACCEPTED contenente ip e porta del proprio nodo successivo. Il joiner imposta i riferimenti dell'host precedente a quelli dell'assistent, e i riferimenti dell'host successivo a quelli ricevuti nel CONNECTION_ACCEPTED. 
Successivamente l'assistant manda un messaggio al suo next di tipo CHANGE_PREC, contenente ip e porta del joiner, così che il suo next possa impostare il joiner come proprio prec. Infine, il joiner imposta come next il joiner, e la procedura termina. 

N.B: L’inserimento del nuovo host avviene sempre tra il nodo che riceve il join e il successivo. 


### Procedura di Discovery
La procedura di DISCOVERY viene avviata da un nodo Y appena riceve un messaggio di JOIN da un nodo X che vuole aggiungersi al suo ring con un dato nickname. 
Nel caso X non abbia scelto un nickname uguale all' ID di Y, Y  fa partire un messaggio di tipo DISCOVERY_QUERY con destinatario proprio
il nickname scelto da X. Se, facendo il giro del ring, il messaggio incontra un nodo T che ha quel nickname, quest'ultimo cambia la tipologia del messaggio in DISCOVERY_ANSWER ad indicare che quel nickname non è disponibile e lo invia ad Y. 
Dunque una volta che Y invia nel ring il DISCOVERY_QUERY possono accadere sostanzialmente due cose:
1) Il messaggio torna invariato ad Y dopo aver fatto tutto il giro del ring, questo significa che il nickname scelto da X è libero. La procedura va a buon fine.
2) Y riceve un DISCOVERY_ANSWER, il che significa che il nickname è già in uso. La procedura da esito negativo.

### Procedura di Acknowledge
La procedura di Acknowledge è un meccanismo implementato per confermare la corretta ricezione di un messaggio da parte di un nodo destinatario. 
Quando un nodo riceve un messaggio di tipo STANDARD, invia automaticamente un messaggio di conferma, noto come messaggio di tipo ACK, al mittente originale del messaggio. 
L'ACK serve a garantire che il messaggio sia stato recapitato con successo e che il mittente sia a conoscenza di ciò.
Il mittente tiene traccia degli ACK ricevuti e può adottare azioni appropriate in base a tali conferme. 
Se non riceve l'ACK entro un determinato periodo di tempo, il mittente può assumere che il messaggio non sia stato recapitato correttamente e può decidere in totale autonomia di inviarlo nuovamente.
La procedura di Acknowledge contribuisce a migliorare l'affidabilità della comunicazione all'interno della rete. 
In questo modo si riduce la possibilità di perdita di dati e si stabilisce una maggiore sicurezza nella trasmissione delle informazioni tra i nodi del network.

### Procedura di Disconnessione
La procedura di disconnessione è la sequenza di operazioni realizzate nella rete al momento in cui un nodo lascia la rete. Distinguiamo due possibili situazioni di disconnessione: disconnessione volontaria e disconnessione involontaria.

#### Disconnessione volontaria
La disconnessione volontaria avviene quando un nodo (il quitter) vuole intenzionalmente uscire dalla rete, e lo comunica preventivamente agli altri nodi, così da permettere la riorganizzazione della rete. Questa tipologia di disconnessione è gestita dal sistema nel seguente modo:
1. L'utente intenzionato ad uscire dalla rete digiterà la parola `quit` in corrispondenza della richiesta "A chi vuoi mandare un messaggio?";
2. L'host quitter costruirà un messaggio di tipo CHANGE_PREC contenente nel payload ip e porta del proprio nodo precedente, poi manderà questo messaggio al proprio nodo successivo;
3. L'host quitter costruirà un messaggio di tipo CHANGE_NEXT contenente nel payload ip e porta del proprio nodo successivo, poi manderà questo messaggio al proprio nodo precedente;
4. Il next del quitter riceverà il CHANGE_PREC e cambierà il proprio prec con i riferimenti nel payload del messaggio;
5. Il prec del quitter riceverà il CHANGE_NEXT e cambierà il proprio next con i riferimenti nel payload del messaggio;
6. L'host quitter potrà a questo punto terminare.
Così facendo si realizzerà un collegamento (bidirezionale) tra prec e next del nodo quitter, che garantiranno la comunicazione a seguito dell'uscita del quitter.

Questo tipo di strategia locale di gestione della disconnessione permette due importanti vantaggi:
- la rete non viene affollata di messaggi di quit
- è possibile la disconnessione multipla contemporanea in diversi punti della rete

#### Disconnessione involontaria - guasto improvviso di un host
La disconnessione involontaria si realizza nel momento in cui il processo di un nodo termina senza preavviso, quindi senza che quest'ultimo possa comunicare preventivamente l'uscita al resto della rete.
Il sistema attualmente è in grado di gestire la disconnessione volontaria (tolleranza ai guasti) ma solo di un nodo alla volta nella stessa porzione di rete.

La gestione dei guasti è basata sull'utilizzo di:
- messaggi di NOTICE, inviati automaticamente da ogni nodo al peer precedente in risposta ad ogni messaggio proveniente da esso per comunicare la propria attività in rete
- collegamento di ogni nodo al successivo del successivo.

la procedura si articola come segue:
1. un nodo (reorganiser) si accorge del guasto del successivo per via della mancata ricezione di un NOTICE;
2. lo stesso nodo imposta come proprio next il nodo attualmente nextnext
3. lo stesso manda un CHANGE_PREC al next contenente il riferimento di sé stesso*
4. lo stesso manda un CHANGE_NEXTNEXT al prec con il riferimento dell'attuale next
5. il nodo next invia al reorganizer un CHANGE_NEXTNEXT con il riferimento del proprio next.

`*` poichè il nodo aspetta una ricezione di un NOTICE anche in risposta al CHANGE_PREC, sarebbe possibile implementare la gestione della disconnessione involotnaria di più nodi consecutivi contemporaneamente, con l'accortezza di utilizzare link di ridondanza più lunghi (link ad next del next del next).

## Running Info
Per eseguire il programma bisognerà portarsi nella directory del progetto per poi eseguire il seguente comando nel caso si voglia creare una nuova rete:
```
python peer.py numero01 8000 8001
```
Altrimenti il seguente comando nel caso ci si voglia unire ad una rete già esistente:
```
python peer.py numero02 8010 8011 -f <specificare il proprio ip> 8000
```
Inoltre è possibile specificare ip diversi per le socket di ricezioni e invio dei messaggi:
```
python peer.py numero02 -IP_socket_rec <ip socket ricezione> 8010 -IP_socket_send <ip socket invio> 8011 -f <specificare il proprio ip> 8000
```
Una volta eseguito, all'utente verrà chiesto di specificare i seguenti input:
  * A chi si vuole inviare un messaggio, specificando il nickname.
  * Il messaggio da inviare.


## Vulnerabilità

- MITM: durante la procedura di inserimento di un nodo X, che manda il JOIN a Y, una terza parte Z potrebbe intercettare fin da subito il messaggio e mandare un falso JOIN a Y e un falso CONNECTION_ACCEPTED a X mettendosi in mezzo alla comunicazione nel ring e intercettando potenzialmente tutti i messaggi.
- Disconnessione imprevista: attualmente il guasto imprevisto di un nodo non viene gestito, e causa una segmentazione dell'anello in cui la comunicazione è fortemente limitata.
- Tolleranza ai guasti di collegamento: il guasto improvviso di un link tra nodi risulta fatale per la comunicazione lungo la rete.
- Privacy e sicurezza: La comunicazione lungo il ring (invio e inoltro di tutti i messaggi) avviene in chiaro, questo implica che chiunque si trovi nello stesso ring può, potenzialmente, leggere i messaggi che viaggiano sullo stesso. Inoltre, come già detto, questa architettura è allo stato attuale molto vulnerabile ai MITM attack.
- Se un nodo riesce a prendere controllo della formattazione dei messaggi (possibile?) può causare danni a tutti gli altri della rete.
- Se un messaggio supera la lunghezza del MTU previsto dall'UDP il thread di message_handler va in errore.
- Se due utenti, adiacenti, effettuano il quit nello stesso momento la topologia di rete non viene riorganizzata correttamente e il ring si spezza.
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
- Bisogna far gestire al peer prima di inviare il messaggio la segmentazione dello stesso in modo tale da non superare l'MTU massimo consentito.
- Gestione disconnessione volontaria e non da parte di due o più utenti adiacenti.