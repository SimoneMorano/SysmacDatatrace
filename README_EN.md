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
  - Upload **one or more CSVs** and choose the row range with a slider.
  - **2D chart**: multiple variables, configurable Y scale, min/max option to normalize curves. Variable selection uses `file | column` to distinguish files.
  - **3D chart** (Plotly): for each series you choose the **file** plus X/Y/Z; option to add more series (Series 1, Series 2, …) in the same plot. Tooltip shows file, row index and axis values.
- **Sysmac Nodes** – For servo node Data Trace CSV files:
  - The header row (containing "Index" and "Offset") is detected automatically in the first lines, even with extra parameter rows or quoted fields. 2D charts with multiple variables and min/max option.
- **General Plotly 2D** – For generic `;`-separated CSV files (including very large files):
  - **Plotly 2D line chart**.
  - **Multi-file**: load multiple CSVs and plot columns from different files on the same chart (legend format `file | column`).
  - **X axis**:
    - if **timestamp** mode is off: time is computed from **cycle time** (cycle time can be different per file) and you can apply an **X shift per file** (in rows) to align/overlap signals.
    - if **timestamp** mode is on: uses the **first column** of each file as timestamp, with a selectable **epoch unit** for numeric timestamps: `s`, `ms`, `us`, `ns`.
  - **Reference**: the file with the most rows defines the max range; shorter files stop when they end.
  - Samples outside the reference X range are not shown (left/right clipping).
  - Row range selection and **downsampling** to keep plots responsive on big datasets.
  - Robust handling of “messy” CSV rows (e.g. trailing `;;;;`): rows are normalized to prevent **legend ↔ data** misalignment.
  - For files >200MB, use **Local CSV paths** (one per line) (reads directly from disk, no upload).

### How to use the app

1. **Start the app** (see [Getting started](#getting-started)) and select a page from the left sidebar:
   - **Sysmac Axes** for axis traces
   - **Sysmac Nodes** for servo node traces

2. **Upload the CSV**: click *Choose a CSV file* and select the Data Trace file exported from Sysmac Studio. The app will load the data and show the controls and charts.

3. **Sysmac Axes – 2D chart**
   - **Select a range of values**: use the slider to limit the row range to display.
   - **Seleziona la variabile del Grafico**: choose one or more variables to plot (`file | column` when multiple CSVs are loaded).
   - **Variabile Scala Y**: choose which variable to use as the Y-axis scale reference (useful with *minmax*).
   - **minmax**: when enabled, normalizes all curves to the min–max range of the variable chosen as Y scale, to compare shapes with different magnitudes.
   - The 2D chart updates according to these choices.

4. **Sysmac Axes – 3D chart**
   - For each **Series**, choose **File**, **Asse X**, **Asse Y**, and **Asse Z** from the CSV variables (same row range as the 2D chart).
   - **➕ Aggiungi altra serie 3D**: adds a second (or third, …) curve in the same 3D chart with another set of X/Y/Z variables.
   - **➖ Rimuovi ultima serie**: removes the last added series.
   - On the 3D chart you can rotate the view, zoom, and pan. Hovering over points shows **Row (index)** (same as the 2D chart X-axis index) and the three variable values.

5. **Sysmac Nodes**
   - Same steps as the Sysmac Axes 2D chart: upload CSV, set the range with the slider, choose variables, and optionally **Variabile Scala Y** and **minmax**. The header (Index, Offset) is detected automatically.

6. **General Plotly 2D**
   - Upload multiple CSVs (max 200MB each) or paste multiple paths into **Local CSV paths** (one per line).
   - Select one or more columns in **Y columns (multi-file)** (by default all columns are disabled).
   - To use timestamps, enable **Use each file first column as timestamp (X axis)**.
   - If the timestamp is numeric (epoch), set **Timestamp unit (epoch)** (`s`, `ms`, `us`, `ns`) to interpret the X axis correctly.
   - If timestamp mode is off, set **cycle time per file** and optionally **X shift per file** to align/overlap signals.
   - Adjust row range and downsampling if needed.

### Dependencies

- `pandas` – CSV reading and processing  
- `streamlit` – web UI  
- `matplotlib` – 2D charts  
- `plotly` – interactive 3D charts (Sysmac Axes only)
