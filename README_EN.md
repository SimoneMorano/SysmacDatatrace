# SysmacDatatrace

Visualize charts from **Data Trace** CSV files exported from Sysmac Studio.

---

## Streamlit App

The Streamlit app lets you upload Data Trace CSV files and analyze them with interactive 2D and 3D charts.

### Getting started

```bash
pip install -r requirements.txt
streamlit run DatatraceStreamlit.py
```

The app opens in your browser (usually `http://localhost:8501`).

### Pages

- **Home** – App landing page.
- **Sysmac Axes** – For axis Data Trace CSV files (header at row 20):
  - Upload CSV and choose the row range with a slider.
  - **2D chart**: multiple variables, configurable Y scale, min/max option to normalize curves.
  - **3D chart** (Plotly): choose X, Y, and Z from the CSV variables; option to add more series (Series 1, Series 2, …) in the same plot. Tooltip shows row index and axis values.
- **Sysmac Nodes** – For servo node Data Trace CSV files:
  - The header row (containing "Index" and "Offset") is detected automatically in the first lines, even with extra parameter rows or quoted fields. 2D charts with multiple variables and min/max option.

### How to use the app

1. **Start the app** (see [Getting started](#getting-started)) and select a page from the left sidebar:
   - **Sysmac Axes** for axis traces
   - **Sysmac Nodes** for servo node traces

2. **Upload the CSV**: click *Choose a CSV file* and select the Data Trace file exported from Sysmac Studio. The app will load the data and show the controls and charts.

3. **Sysmac Axes – 2D chart**
   - **Select a range of values**: use the slider to limit the row range to display.
   - **Seleziona la variabile del Grafico**: choose one or more variables to plot.
   - **Variabile Scala Y**: choose which variable to use as the Y-axis scale reference (useful with *minmax*).
   - **minmax**: when enabled, normalizes all curves to the min–max range of the variable chosen as Y scale, to compare shapes with different magnitudes.
   - The 2D chart updates according to these choices.

4. **Sysmac Axes – 3D chart**
   - For each **Series**, choose **Asse X**, **Asse Y**, and **Asse Z** from the CSV variables (same row range as the 2D chart).
   - **➕ Aggiungi altra serie 3D**: adds a second (or third, …) curve in the same 3D chart with another set of X/Y/Z variables.
   - **➖ Rimuovi ultima serie**: removes the last added series.
   - On the 3D chart you can rotate the view, zoom, and pan. Hovering over points shows **Row (index)** (same as the 2D chart X-axis index) and the three variable values.

5. **Sysmac Nodes**
   - Same steps as the Sysmac Axes 2D chart: upload CSV, set the range with the slider, choose variables, and optionally **Variabile Scala Y** and **minmax**. The header (Index, Offset) is detected automatically.

### Dependencies

- `pandas` – CSV reading and processing  
- `streamlit` – web UI  
- `matplotlib` – 2D charts  
- `plotly` – interactive 3D charts (Sysmac Axes only)
