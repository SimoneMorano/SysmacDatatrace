import pandas as pd
import streamlit as st 
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Sysmac servo Nodes",
    page_icon="👋",
    layout="wide"
)

uploaded_files = st.file_uploader("Choose a CSV file")

if uploaded_files:
    # Cerca la riga che contiene le intestazioni "Index" e "Offset" (possono essere su righe diverse a seconda dei parametri)
    first_lines = []
    for _ in range(25):
        line = uploaded_files.readline()
        if not line:
            break
        if isinstance(line, bytes):
            line = line.decode("utf-8", errors="replace")
        first_lines.append(line)

    header_row = None
    for i, line in enumerate(first_lines):
        # Rimuovi virgolette dalle celle (es. "Index" -> Index) per riconoscere l'header
        cells = [c.strip().strip('"') for c in line.split(",")]
        if "Index" in cells and "Offset" in cells:
            header_row = i
            break

    if header_row is None:
        st.error("Intestazioni 'Index' e 'Offset' non trovate nel file.")
    else:
        skip_rows = header_row

        uploaded_files.seek(0)
        try:
            data_trace_motors = pd.read_csv(
                uploaded_files, sep=',', skiprows=skip_rows, on_bad_lines='skip'
            )
        except TypeError:
            uploaded_files.seek(0)
            data_trace_motors = pd.read_csv(
                uploaded_files, sep=',', skiprows=skip_rows, error_bad_lines=False
            )

        cols_to_drop = [c for c in ['Index', 'Offset'] if c in data_trace_motors.columns]
        data_trace_motors_1 = data_trace_motors.drop(columns=cols_to_drop)
        data_trace_motors_1 = data_trace_motors_1.loc[0:1023]

        for index in range(len(data_trace_motors_1.columns)):
            data_trace_motors_1[data_trace_motors_1.columns[index]] = pd.to_numeric(data_trace_motors_1[data_trace_motors_1.columns[index]], downcast="float")

        values = st.slider("Select a range of values", 0.0, float(len(data_trace_motors_1)), (0.0, float(len(data_trace_motors_1))))
        options = st.multiselect("Seleziona la variabile del Grafico", data_trace_motors_1.columns)
        options_check = st.selectbox("Variabile Scala Y", options)
        minmax = st.checkbox("minmax")
        data_trace_2 = data_trace_motors_1.loc[values[0]:values[1]]

        fig1, ax1 = plt.subplots(figsize=(20,8))
        ax1.set_xlabel('X')
        ax1.set_ylabel('Y')
        ax1.set_title('Grafico')

        if minmax:
            for option in options:
                max1 = data_trace_2[options_check].max()
                min1 = data_trace_2[options_check].min()
                max = data_trace_2[option].max()
                min = data_trace_2[option].min()
                data_trace_2[option] = data_trace_2[option].apply(lambda x : ((x - min) / (max - min)) * (max1 - min1) + min1)
                ax1.plot(data_trace_2[option], label = option)
        else:
            for option in options:
                ax1.plot(data_trace_2[option], label = option)

        ax1.legend()
        st.pyplot(fig1)
