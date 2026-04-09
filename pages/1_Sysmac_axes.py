import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import numpy as np

st.set_page_config(
    page_title="Sysmac Axes",
    page_icon="👋",
    layout="wide"
)

uploaded_files = st.file_uploader("Choose one or more CSV files", type=["csv"], accept_multiple_files=True)


@st.cache_data(show_spinner=False)
def _load_axes_csv(file_bytes: bytes) -> pd.DataFrame:
    df = pd.read_csv(pd.io.common.BytesIO(file_bytes), sep=",", header=19)
    df = df.drop(["Index", "Date", "ClockTime", "RawTime", "TraceSampID"], axis="columns", errors="ignore")

    for c in df.columns:
        # Sysmac exports may use comma as decimal separator
        s = df[c]
        if s.dtype == object:
            s = s.replace(",", ".", regex=True)
        df[c] = pd.to_numeric(s, errors="coerce", downcast="float")
    return df


if uploaded_files:
    entries: list[dict] = []
    for uf in uploaded_files:
        try:
            df = _load_axes_csv(uf.getvalue())
        except Exception as exc:
            st.error(f"Cannot read '{uf.name}': {exc}")
            continue
        entries.append({"label": uf.name, "df": df})

    if not entries:
        st.stop()

    max_len = max(len(e["df"]) for e in entries)
    values = st.slider(
        "Select a range of values",
        0,
        max(0, int(max_len) - 1),
        (0, max(0, int(max_len) - 1)),
    )

    trace_options: list[str] = []
    for e in entries:
        for c in e["df"].columns:
            trace_options.append(f"{e['label']} | {c}")

    selected_traces = st.multiselect("Seleziona la variabile del Grafico", trace_options, default=[])
    y_scale_ref = st.selectbox("Variabile Scala Y", selected_traces, disabled=len(selected_traces) == 0)
    minmax = st.checkbox("minmax", value=False, disabled=len(selected_traces) == 0)

    # Build a map trace_name -> series
    series_map: dict[str, pd.Series] = {}
    for token in selected_traces:
        file_label, col = token.split(" | ", 1)
        e = next((x for x in entries if x["label"] == file_label), None)
        if e is None:
            continue
        df = e["df"]
        if col not in df.columns:
            continue
        start_i, end_i = int(values[0]), int(values[1])
        if start_i > len(df) - 1:
            continue
        end_i = min(end_i, len(df) - 1)
        series_map[token] = df[col].iloc[start_i : end_i + 1].reset_index(drop=True)

    fig1, ax1 = plt.subplots(figsize=(20, 8))
    ax1.set_xlabel("X")
    ax1.set_ylabel("Y")
    ax1.set_title("Grafico")

    if minmax and y_scale_ref in series_map:
        ref = series_map[y_scale_ref]
        ref_max = ref.max()
        ref_min = ref.min()
        for trace_name, s in series_map.items():
            s_max = s.max()
            s_min = s.min()
            if pd.notna(s_max) and pd.notna(s_min) and s_max != s_min:
                s = (s - s_min) / (s_max - s_min) * (ref_max - ref_min) + ref_min
            ax1.plot(s, label=trace_name)
    else:
        for trace_name, s in series_map.items():
            ax1.plot(s, label=trace_name)

    if series_map:
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

    line_thickness = st.radio(
        "Spessore linea (3D)",
        ["Fine", "Spessa"],
        index=0,
        horizontal=True,
    )
    line_width_3d = 2 if line_thickness == "Fine" else 6

    colors_3d = ["steelblue", "coral", "seagreen", "mediumpurple", "darkorange"]
    traces_3d = []
    axis_x_first = axis_y_first = axis_z_first = None

    for i in range(st.session_state.n_3d_series):
        st.markdown(f"**Serie {i + 1}**")
        row1_c1, row1_c2 = st.columns(2)
        with row1_c1:
            file_3d = st.selectbox(
                "File",
                [e["label"] for e in entries],
                key=f"3d_file_{i}",
            )
        df_3d = next((e["df"] for e in entries if e["label"] == file_3d), entries[0]["df"])
        cols_3d = list(df_3d.columns)
        with row1_c2:
            axis_x = st.selectbox("Asse X", cols_3d, key=f"3d_x_{i}")

        row2_c1, row2_c2 = st.columns(2)
        with row2_c1:
            axis_y = st.selectbox("Asse Y", cols_3d, key=f"3d_y_{i}")
        with row2_c2:
            axis_z = st.selectbox("Asse Z", cols_3d, key=f"3d_z_{i}")

        if axis_x and axis_y and axis_z:
            if axis_x_first is None:
                axis_x_first, axis_y_first, axis_z_first = axis_x, axis_y, axis_z
            color = colors_3d[i % len(colors_3d)]
            start_i, end_i = int(values[0]), int(values[1])
            if start_i <= len(df_3d) - 1:
                end_i = min(end_i, len(df_3d) - 1)
                df3 = df_3d.iloc[start_i : end_i + 1]
            else:
                df3 = df_3d.iloc[0:0]
            row_index = df3.index.values
            x_raw = df3[axis_x].values if axis_x in df3.columns else np.array([])
            y_raw = df3[axis_y].values if axis_y in df3.columns else np.array([])
            z_raw = df3[axis_z].values if axis_z in df3.columns else np.array([])
            x = np.asarray(x_raw, dtype="float64")
            y = np.asarray(y_raw, dtype="float64")
            z = np.asarray(z_raw, dtype="float64")
            finite_mask = np.isfinite(x) & np.isfinite(y) & np.isfinite(z)
            if finite_mask.size == 0 or finite_mask.sum() < 2:
                st.warning(
                    f"Serie {i + 1}: nessun punto valido (valori NaN/inf) per X/Y/Z nell'intervallo selezionato."
                )
                continue
            x = x[finite_mask]
            y = y[finite_mask]
            z = z[finite_mask]
            row_index = row_index[finite_mask]
            traces_3d.append(
                go.Scatter3d(
                    x=x,
                    y=y,
                    z=z,
                    customdata=row_index,
                    mode="lines",
                    line=dict(color=color, width=line_width_3d),
                    name=f"{file_3d} | Serie {i + 1}",
                    hovertemplate=(
                        "<b>Riga (indice)</b>: %{customdata}<br>"
                        f"<b>File</b>: {file_3d}<br>"
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
                template="plotly_white",
                scene=dict(
                    xaxis_title=axis_x_first or "X",
                    yaxis_title=axis_y_first or "Y",
                    zaxis_title=axis_z_first or "Z",
                    bgcolor="white",
                ),
                paper_bgcolor="white",
                margin=dict(l=0, r=0, b=0, t=40),
                height=600,
                showlegend=True,
            ),
        )
        st.plotly_chart(fig2, width="stretch", theme=None)
    plt.close(fig1)
