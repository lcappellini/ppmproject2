# MyWeather API

MyWeather API è un'API RESTful basata su Flask che fornisce previsioni meteo. Include autenticazione degli utenti e gestione delle chiavi API.

## Struttura del Progetto

Il progetto include i seguenti file e cartelle:

- `main.py`: file principale che contiene la logica dell'applicazione Flask.
- `db_utils.py`: contiene una funzione per fare un reset del database e popolarlo con qualche riga di esempio.
- `templates/`: Cartella che contiene i template HTML.
- `static/`: Contiene il file CSS con lo stile per le pagine.
- `insance`: Contiene i file dell'istanza, in particolare il database (su Vercel invece è nella cartella '/tmp' di Vercel, non accessibile direttamente)
- `sample_requests.py`: esempio di codice che permette di effettuare richieste all'api


## Dipendenze

Le dipendenze del progetto sono elencate nel file `requirements.txt`:


# Documentazione API


### /api/forecast

Gestisce i dati delle previsioni meteo per luoghi specifici.

#### GET

Recupera le previsioni meteo in base ai parametri specificati.

**Parametri:**
- `key`: API key per l'autenticazione.
- `placename` o `placeid`: Specifica il nome del luogo o l'ID del luogo.
- `date` (opzionale): Data per la quale è richiesta la previsione (formato: `yyyy-mm-dd` o `yyyymmdd`).
- `details` (opzionale): True o False per includere informazioni dettagliate sulla previsione.

**Risposte:**
- 200 OK: Restituisce i dati delle previsioni meteo.
- 400 Bad Request: Parametri mancanti o non validi.
- 401 Unauthorized: API key non valida.
- 404 Not Found: Nessun dato trovato con i parametri specificati.

#### PUT

Aggiorna i dati delle previsioni meteo.

**Parametri:**
- `key`: API key per l'autenticazione.
- `placeid`: ID del luogo.
- `date`: Data della previsione (formato: `yyyy-mm-dd` o `yyyymmdd`).
- Parametri meteo (opzionali): `condition`, `temperature`, `rain`, `humidity`, `wind`, `wind_direction`.

**Risposte:**
- 200 OK: Previsioni aggiornate con successo.
- 400 Bad Request: Parametri mancanti o non validi.
- 401 Unauthorized: API key non valida.

#### DELETE

Cancella i dati delle previsioni meteo.

**Parametri:**
- `key`: API key per l'autenticazione.
- `forecastid`: ID della previsione da cancellare.

**Risposte:**
- 200 OK: Previsione cancellata con successo.
- 400 Bad Request: Parametri mancanti o non validi.
- 401 Unauthorized: API key non valida.

### /api/places

Gestisce le informazioni sui luoghi specifici.

#### GET

Recupera le informazioni su un luogo specifico.

**Parametri:**
- `key`: API key per l'autenticazione.
- `placename` o `placeid`: Specifica il nome del luogo o l'ID del luogo.

**Risposte:**
- 200 OK: Restituisce le informazioni del luogo.
- 400 Bad Request: Parametri mancanti o non validi.
- 401 Unauthorized: API key non valida.
- 404 Not Found: Nessun luogo trovato con i parametri specificati.

#### PUT

Aggiorna le informazioni su un luogo specifico.

**Parametri:**
- `key`: API key per l'autenticazione.
- `placeid`: ID del luogo da aggiornare.
- `placename`: Nome del luogo.
- `coords` (opzionale): Coordinate del luogo (formato: `latitudine,longitudine`).
- `lat` e `lon` (opzionali): Coordinate del luogo.

**Risposte:**
- 200 OK: Luogo aggiornato con successo.
- 400 Bad Request: Parametri mancanti o non validi.
- 401 Unauthorized: API key non valida.

#### DELETE

Cancella le informazioni su un luogo specifico.

**Parametri:**
- `key`: API key per l'autenticazione.
- `placeid` o `placename`: ID o nome del luogo da cancellare.

**Risposte:**
- 200 OK: Luogo cancellato con successo.
- 400 Bad Request: Parametri mancanti o non validi.
- 401 Unauthorized: API key non valida.


### /api/conditions

Gestisce le informazioni sulle condizioni meteo.

#### GET

Recupera le informazioni su una condizione meteo (la sua descrizione).

**Parametri:**
- `key`: API key per l'autenticazione.
- `id`: Specifica l'ID della condizione meteo.

**Risposte:**
- 200 OK: Restituisce le informazioni della condizione meteo.
- 400 Bad Request: Parametri mancanti o non validi.
- 401 Unauthorized: API key non valida.
- 404 Not Found: Nessuna condizione meteo trovata con i parametri specificati.
