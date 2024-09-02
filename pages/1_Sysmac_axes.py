import pandas as pd
import streamlit as st 
import matplotlib.pyplot as plt
import plotly as ply

st.set_page_config(
    page_title="Sysmac Axes",
    page_icon="👋",
    layout="wide"
)

data_trace = pd.read_csv('csv_example\Delta_R1.csv', sep=',', header=19)
data_trace_1 = data_trace.drop(['Index', 'Date', 'ClockTime', 'RawTime', 'TraceSampID'], axis = 'columns')

for index in range(len(data_trace_1.columns)):
    data_trace_1[data_trace_1.columns[index]] = data_trace_1[data_trace_1.columns[index]].replace(',','.',regex=True)
    data_trace_1[data_trace_1.columns[index]] = pd.to_numeric(data_trace_1[data_trace_1.columns[index]], downcast="float") 



values = st.slider("Select a range of values", 0.0, float(len(data_trace_1)), (0.0, float(len(data_trace_1))))

options = st.multiselect("Seleziona la variabile", data_trace_1.columns)

data_trace_2 = data_trace_1.loc[values[0]:values[1]]

fig1, ax1 = plt.subplots(figsize=(20,6))
ax1.set_xlabel('X')
ax1.set_ylabel('Y')
ax1.set_title('Grafico')

for option in options:
    ax1.plot(data_trace_2[option], label = option)

ax1.legend()
st.pyplot(fig1)