import pandas as pd
import streamlit as st 
import matplotlib.pyplot as plt
import plotly as ply

st.set_page_config(
    page_title="Sysmac servo Nodes",
    page_icon="👋",
)

data_trace_motors = pd.read_csv('csv_example\M31.csv', sep=',', header=8)

data_trace_motors_1 = data_trace_motors.drop(['Index', 'Offset'], axis = 'columns')
data_trace_motors_1 = data_trace_motors_1.loc[0:1023]

for index in range(len(data_trace_motors_1.columns)):
    data_trace_motors_1[data_trace_motors_1.columns[index]] = pd.to_numeric(data_trace_motors_1[data_trace_motors_1.columns[index]], downcast="float") 



option = st.multiselect("Seleziona la variabile", data_trace_motors_1.columns)