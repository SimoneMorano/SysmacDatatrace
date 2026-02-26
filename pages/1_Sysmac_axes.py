import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import plotly.graph_objects as go

st.set_page_config(
    page_title="Sysmac Axes",
    page_icon="👋",
    layout="wide"
)

uploaded_files = st.file_uploader("Choose a CSV file")

print(uploaded_files)

if uploaded_files:
    data_trace = pd.read_csv(uploaded_files, sep=',', header=19)
    data_trace_1 = data_trace.drop(['Index', 'Date', 'ClockTime', 'RawTime', 'TraceSampID'], axis = 'columns')

    for index in range(len(data_trace_1.columns)):
        data_trace_1[data_trace_1.columns[index]] = data_trace_1[data_trace_1.columns[index]].replace(',','.',regex=True)
        data_trace_1[data_trace_1.columns[index]] = pd.to_numeric(data_trace_1[data_trace_1.columns[index]], downcast="float") 

    values = st.slider("Select a range of values", 0.0, float(len(data_trace_1)), (0.0, float(len(data_trace_1))))
    options = st.multiselect("Seleziona la variabile del Grafico", data_trace_1.columns)
    options_check = st.selectbox("Variabile Scala Y", options)
    minmax = st.checkbox("minmax")
    data_trace_2 = data_trace_1.loc[values[0]:values[1]]

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

    # --- Grafico 3D ---
    st.subheader("Grafico 3D")
    if "n_3d_series" not in st.session_state:
        st.session_state.n_3d_series = 1

    cols_btn = st.columns([1, 1, 4])
    with cols_btn[0]:
        if st.button("➕ Aggiungi altra serie 3D"):
            st.session_state.n_3d_series += 1
            st.rerun()
    with cols_btn[1]:
        if st.session_state.n_3d_series > 1 and st.button("➖ Rimuovi ultima serie"):
            st.session_state.n_3d_series -= 1
            st.rerun()

    colors_3d = ["steelblue", "coral", "seagreen", "mediumpurple", "darkorange"]
    traces_3d = []
    axis_x_first = axis_y_first = axis_z_first = None

    for i in range(st.session_state.n_3d_series):
        st.markdown(f"**Serie {i + 1}**")
        col_x, col_y, col_z = st.columns(3)
        with col_x:
            axis_x = st.selectbox("Asse X", data_trace_1.columns, key=f"3d_x_{i}")
        with col_y:
            axis_y = st.selectbox("Asse Y", data_trace_1.columns, key=f"3d_y_{i}")
        with col_z:
            axis_z = st.selectbox("Asse Z", data_trace_1.columns, key=f"3d_z_{i}")

        if axis_x and axis_y and axis_z:
            if axis_x_first is None:
                axis_x_first, axis_y_first, axis_z_first = axis_x, axis_y, axis_z
            color = colors_3d[i % len(colors_3d)]
            row_index = data_trace_2.index.values
            traces_3d.append(
                go.Scatter3d(
                    x=data_trace_2[axis_x].values,
                    y=data_trace_2[axis_y].values,
                    z=data_trace_2[axis_z].values,
                    customdata=row_index,
                    mode="lines",
                    line=dict(color=color, width=2),
                    name=f"Serie {i + 1}",
                    hovertemplate=(
                        "<b>Riga (indice)</b>: %{customdata}<br>"
                        f"<b>{axis_x}</b>: %{{x:.4g}}<br>"
                        f"<b>{axis_y}</b>: %{{y:.4g}}<br>"
                        f"<b>{axis_z}</b>: %{{z:.4g}}<extra></extra>"
                    ),
                )
            )

    if traces_3d:
        fig2 = go.Figure(
            data=traces_3d,
            layout=go.Layout(
                title=dict(text="Grafico 3D – più serie"),
                scene=dict(
                    xaxis_title=axis_x_first or "X",
                    yaxis_title=axis_y_first or "Y",
                    zaxis_title=axis_z_first or "Z",
                ),
                margin=dict(l=0, r=0, b=0, t=40),
                height=600,
                showlegend=True,
            ),
        )
        st.plotly_chart(fig2, use_container_width=True)
    plt.close(fig1)
