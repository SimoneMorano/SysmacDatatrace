import pandas as pd
import streamlit as st 
import matplotlib.pyplot as plt
import plotly as ply

st.set_page_config(
    page_title="Sysmac servo Nodes",
    page_icon="👋",
)

uploaded_files = st.file_uploader("Choose a CSV file")

if uploaded_files:
    data_trace_motors = pd.read_csv(uploaded_files, sep=',', header=8)

    data_trace_motors_1 = data_trace_motors.drop(['Index', 'Offset'], axis = 'columns')
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