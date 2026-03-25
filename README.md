# SysmacDatatrace

Visualizzazione di grafici a partire da file CSV **Data Trace** di Sysmac Studio.

---

## App Streamlit

L'app Streamlit permette di caricare CSV Data Trace e analizzarli con grafici 2D e 3D interattivi.

### Avvio

```bash
pip install -r requirements.txt
streamlit run DatatraceStreamlit.py
```

L'app si apre nel browser (di solito `http://localhost:8501`).

### Pagine

- **Home** – Pagina iniziale dell'app.
- **Sysmac Axes** – Per CSV Data Trace degli assi (header alla riga 20):
  - Caricamento CSV e scelta dell'intervallo di righe con uno slider.
  - **Grafico 2D**: più variabili, scala Y configurabile, opzione min/max per normalizzare.
  - **Grafico 3D** (Plotly): scelta di X, Y, Z tra le variabili del CSV; possibilità di aggiungere più serie (Serie 1, Serie 2, …) nello stesso grafico. In tooltip: indice di riga e valori degli assi.
- **Sysmac Nodes** – Per CSV Data Trace dei nodi servo:
  - L'intestazione (riga con "Index" e "Offset") viene cercata automaticamente nelle prime righe, anche con parametri aggiuntivi o virgolette. Grafici 2D con più variabili e opzione min/max.
- **General Plotly 2D** – Per CSV generici separati da `;` (file anche molto grandi):
  - **Grafico 2D Plotly** con linee.
  - **Asse X** = numero di riga globale (da 0 all’ultima riga del file).
  - Selezione dell’intervallo righe e **downsample** per mantenere il grafico reattivo su file molto grandi.
  - Per file >200MB usare **Local CSV path** (lettura diretta da disco, senza upload).

### Come usare l'applicazione

1. **Avvia l'app** (vedi [Avvio](#avvio)) e dalla barra laterale sinistra scegli la pagina:
   - **Sysmac Axes** per tracce degli assi
   - **Sysmac Nodes** per tracce dei nodi servo

2. **Carica il CSV**: clicca su *Choose a CSV file* e seleziona il file Data Trace esportato da Sysmac Studio. L'app caricherà i dati e mostrerà i controlli e i grafici.

3. **Sysmac Axes – Grafico 2D**
   - **Select a range of values**: trascina lo slider per limitare l'intervallo di righe da visualizzare.
   - **Seleziona la variabile del Grafico**: scegli una o più variabili da plottare.
   - **Variabile Scala Y**: scegli quale variabile usare come riferimento per la scala dell'asse Y (utile con *minmax*).
   - **minmax**: se attivo, normalizza tutte le curve nel range min–max della variabile scelta come scala Y, per confrontare forme con ordini di grandezza diversi.
   - Il grafico 2D si aggiorna in base a queste scelte.

4. **Sysmac Axes – Grafico 3D**
   - Per ogni **Serie** scegli **Asse X**, **Asse Y** e **Asse Z** tra le variabili del CSV (stesso intervallo di righe del grafico 2D).
   - **➕ Aggiungi altra serie 3D**: aggiunge una seconda (o terza, …) curva nello stesso grafico 3D, con un altro insieme di variabili X/Y/Z.
   - **➖ Rimuovi ultima serie**: toglie l'ultima serie aggiunta.
   - Sul grafico 3D puoi ruotare la vista, zoomare e fare pan. Passando il mouse sui punti vedi **Riga (indice)** (stesso indice dell'asse X del grafico 2D) e i valori delle tre variabili.

5. **Sysmac Nodes**
   - Stessi passi del grafico 2D di Sysmac Axes: carica il CSV, imposta l'intervallo con lo slider, scegli le variabili, eventualmente **Variabile Scala Y** e **minmax**. L'header (Index, Offset) viene rilevato automaticamente.

6. **General Plotly 2D**
   - Inserisci il percorso in **Local CSV path** se il file è grande (lo `streamlit file_uploader` ha limite 200MB).
   - Seleziona le colonne da plottare in **Y columns** (di default sono tutte disabilitate).
   - Imposta intervallo righe e downsample se necessario.

### Dipendenze

- `pandas` – lettura e elaborazione CSV  
- `streamlit` – interfaccia web  
- `matplotlib` – grafici 2D  
- `plotly` – grafici 3D interattivi (solo Sysmac Axes)
