import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from pathlib import Path


st.set_page_config(
    page_title="Generic Plotly 2D",
    page_icon="📈",
    layout="wide",
)

st.title("Generic CSV – Plotly 2D")

uploaded_file = st.file_uploader("Choose a CSV file (max 200MB)", type=["csv"])
st.markdown("**Large file?** Use the local path option below (no upload).")
file_path = st.text_input(
    "Local CSV path (optional)",
    value="",
    placeholder=r"C:\path\to\complete_oscmac_operfseal_reduced_control_period.csv",
)

@st.cache_data(show_spinner=False)
def _count_data_rows_for_path(path_str: str) -> int:
    # Count data rows excluding header row (row 0)
    with open(path_str, "rb") as f:
        # Fast-ish newline count
        total_lines = 0
        while True:
            chunk = f.read(1024 * 1024)
            if not chunk:
                break
            total_lines += chunk.count(b"\n")
    # If file doesn't end with newline, count() misses last line; that's fine for UI bounds.
    return max(0, total_lines - 1)


@st.cache_data(show_spinner=False)
def _count_data_rows_for_upload(file_bytes: bytes) -> int:
    total_lines = file_bytes.count(b"\n")
    return max(0, total_lines - 1)


def _seek0_if_possible(source) -> None:
    if hasattr(source, "seek"):
        source.seek(0)


def _read_header_cols(source) -> list[str]:
    _seek0_if_possible(source)
    df0 = pd.read_csv(source, sep=";", nrows=0)
    return list(df0.columns)


def _read_slice(source, start_row: int, end_row: int, usecols: list[str]) -> pd.DataFrame:
    """
    Read only [start_row, end_row] rows (0-based, excluding header row).
    Header is always row 0 in the file.
    """
    if end_row < start_row:
        start_row, end_row = end_row, start_row

    nrows = (end_row - start_row) + 1

    # Skip data rows before start_row but keep the header row (row 0)
    _seek0_if_possible(source)
    return pd.read_csv(
        source,
        sep=";",
        usecols=usecols,
        skiprows=range(1, start_row + 1),
        nrows=nrows,
        on_bad_lines="skip",
        low_memory=False,
    )


source = None
if file_path.strip():
    p = Path(file_path.strip().strip('"'))
    if not p.exists():
        st.error(f"File not found: {p}")
    else:
        source = str(p)
elif uploaded_file is not None:
    source = uploaded_file


if source is not None:
    cols = _read_header_cols(source)

    left, right = st.columns([1, 2])
    with left:
        # For now: no X selection. X axis is the row index.
        y_cols = st.multiselect("Y columns", cols, default=[])
        y_scale_col = st.selectbox("Y scale reference (for minmax)", y_cols, disabled=len(y_cols) == 0)
        minmax = st.checkbox("minmax (normalize Y to reference min/max)", value=False, disabled=len(y_cols) == 0)

    with right:
        st.markdown("**Row range (0-based, data rows)**")

        if isinstance(source, str):
            total_rows = _count_data_rows_for_path(source)
        else:
            # Uploaded file: count from bytes once (still respects 200MB limit)
            _seek0_if_possible(source)
            file_bytes = source.getvalue()
            total_rows = _count_data_rows_for_upload(file_bytes)

        # Default: full range
        if "osc_start_row" not in st.session_state:
            st.session_state.osc_start_row = 0
        if "osc_end_row" not in st.session_state:
            st.session_state.osc_end_row = total_rows

        start_row = st.number_input("Start row", min_value=0, max_value=total_rows, value=int(st.session_state.osc_start_row), step=1000)
        end_row = st.number_input("End row", min_value=0, max_value=total_rows, value=int(st.session_state.osc_end_row), step=1000)
        st.session_state.osc_start_row = int(start_row)
        st.session_state.osc_end_row = int(end_row)

        # Default downsample so that initial plot is responsive but still covers full file
        suggested = max(1, int((max(1, abs(int(end_row) - int(start_row)) + 1)) / 50000))
        downsample_step = st.number_input(
            "Downsample (keep 1 every N rows)",
            min_value=1,
            value=suggested,
            step=1,
            help="Use 1 for no downsampling (may be slow on very large ranges).",
        )

    if len(y_cols) == 0:
        st.info("Select one or more columns in **Y columns** to plot.")
    else:
        usecols = list(y_cols)
        df = _read_slice(source, int(start_row), int(end_row), usecols=usecols)

        # Convert numeric columns where possible
        for c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

        # X axis: global row number in the file (0..N)
        x_vals = pd.Series(range(int(start_row), int(start_row) + len(df)), name="row")

        if downsample_step > 1:
            step = int(downsample_step)
            df = df.iloc[::step]
            x_vals = x_vals.iloc[::step]

        if df.empty:
            st.warning("No data read for the selected range.")
        else:
            fig = go.Figure()

            # Optional minmax normalization per series to match the reference Y range
            if minmax and y_scale_col in df.columns and df[y_scale_col].notna().any():
                ref_min = df[y_scale_col].min()
                ref_max = df[y_scale_col].max()
            else:
                ref_min = ref_max = None

            for y in y_cols:
                if y not in df.columns:
                    continue

                series = df[y]
                if minmax and ref_min is not None and ref_max is not None:
                    s_min = series.min()
                    s_max = series.max()
                    if pd.notna(s_min) and pd.notna(s_max) and s_max != s_min:
                        series = (series - s_min) / (s_max - s_min)
                        series = series * (ref_max - ref_min) + ref_min

                fig.add_trace(
                    go.Scatter(
                        x=x_vals,
                        y=series,
                        mode="lines",
                        name=y,
                        hovertemplate=(
                            "<b>row</b>: %{x}<br>"
                            f"<b>{y}</b>: %{{y:.6g}}<extra></extra>"
                        ),
                    )
                )

            fig.update_layout(
                height=650,
                margin=dict(l=10, r=10, t=40, b=10),
                hovermode="x unified",
                legend=dict(orientation="h"),
                xaxis_title="row",
                yaxis_title="Value",
            )

            st.plotly_chart(fig, use_container_width=True)
