import pandas as pd
import streamlit as st
import plotly.graph_objects as go

st.set_page_config(
    page_title="Sysmac servo Nodes",
    page_icon="👋",
    layout="wide",
)

uploaded_files = st.file_uploader("Choose a CSV file")

if uploaded_files:
    data_trace_motors = pd.read_csv(uploaded_files, sep=',', header=8)

    data_trace_motors_1 = data_trace_motors.drop(['Index', 'Offset'], axis='columns')
    data_trace_motors_1 = data_trace_motors_1.loc[0:1023]

    for index in range(len(data_trace_motors_1.columns)):
        data_trace_motors_1[data_trace_motors_1.columns[index]] = pd.to_numeric(data_trace_motors_1[data_trace_motors_1.columns[index]], downcast="float")

    values = st.slider("Select a range of values", 0.0, float(len(data_trace_motors_1)), (0.0, float(len(data_trace_motors_1))))
    options = st.multiselect("Seleziona la variabile del Grafico", data_trace_motors_1.columns)
    options_check = st.selectbox("Variabile Scala Y", options) if options else None

    minmax = st.checkbox("minmax")
    data_trace_2 = data_trace_motors_1.loc[values[0]:values[1]]

    if minmax and options and options_check:
        for option in options:
            max1 = data_trace_2[options_check].max()
            min1 = data_trace_2[options_check].min()
            max_val = data_trace_2[option].max()
            min_val = data_trace_2[option].min()
            data_trace_2[option] = data_trace_2[option].apply(lambda x: ((x - min_val) / (max_val - min_val)) * (max1 - min1) + min1)

    traces_2d = []
    x_index = data_trace_2.index.values
    for option in options:
        traces_2d.append(
            go.Scatter(
                x=x_index,
                y=data_trace_2[option].values,
                mode="lines",
                name=option,
            )
        )

    fig1 = go.Figure(
        data=traces_2d,
        layout=go.Layout(
            title=dict(text="Grafico"),
            xaxis_title="X",
            yaxis_title="Y",
            height=500,
            showlegend=True,
            margin=dict(l=60, r=20, b=50, t=50),
        ),
    )
    st.plotly_chart(fig1, width="stretch")
