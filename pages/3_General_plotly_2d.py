import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from pathlib import Path
import numpy as np
import io


st.set_page_config(
    page_title="Generic Plotly 2D",
    page_icon="📈",
    layout="wide",
)

st.title("Generic CSV – Plotly 2D")

uploaded_files = st.file_uploader(
    "Choose one or more CSV files (max 200MB each)",
    type=["csv"],
    accept_multiple_files=True,
)
st.markdown("**Large file?** Use local paths below (one path per line, no upload).")
file_paths_text = st.text_area(
    "Local CSV paths (optional)",
    value="",
    placeholder=(
        r"C:\path\to\file_1.csv" "\n"
        r"C:\path\to\file_2.csv"
    ),
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

    def _open_text_stream(src):
        if isinstance(src, str):
            return open(src, "r", encoding="utf-8", errors="replace", newline="")
        _seek0_if_possible(src)
        # UploadedFile behaves like a binary stream; wrap into text.
        return io.TextIOWrapper(src, encoding="utf-8", errors="replace", newline="")

    # Detect malformed rows (extra ';' fields) and fall back to a robust reader that
    # truncates each data row to the header field count.
    with _open_text_stream(source) as f:
        header_line = f.readline()
        if not header_line:
            return pd.DataFrame()
        header_fields = header_line.rstrip("\r\n").split(";")
        expected_n_fields = len(header_fields)

        sample_line = f.readline()
        sample_n_fields = len(sample_line.rstrip("\r\n").split(";")) if sample_line else expected_n_fields

    malformed = sample_n_fields != expected_n_fields

    if not malformed:
        # Fast path: let pandas slice directly
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

    # Robust path: rebuild a mini-CSV in-memory with truncated rows
    out = io.StringIO()
    out.write(header_line)

    with _open_text_stream(source) as f:
        _ = f.readline()  # consume header
        # Skip rows before start_row
        for _i in range(start_row):
            if not f.readline():
                break

        for _i in range(nrows):
            line = f.readline()
            if not line:
                break
            parts = line.rstrip("\r\n").split(";")
            if len(parts) >= expected_n_fields:
                parts = parts[:expected_n_fields]
            else:
                parts = parts + [""] * (expected_n_fields - len(parts))
            out.write(";".join(parts) + "\n")

    out.seek(0)
    return pd.read_csv(
        out,
        sep=";",
        usecols=usecols,
        on_bad_lines="skip",
        low_memory=False,
    )


source_entries = []

# Local paths (one per line)
raw_paths = [x.strip().strip('"') for x in file_paths_text.splitlines() if x.strip()]
for idx, path_str in enumerate(raw_paths):
    p = Path(path_str)
    if not p.exists():
        st.error(f"File not found: {p}")
        continue
    source_entries.append(
        {
            "id": f"path_{idx}",
            "label": p.name,
            "source": str(p),
            "kind": "path",
        }
    )

# Uploaded files
for idx, uf in enumerate(uploaded_files or []):
    source_entries.append(
        {
            "id": f"upload_{idx}",
            "label": uf.name,
            "source": uf,
            "kind": "upload",
        }
    )

if len(source_entries) == 0:
    st.info("Upload one or more CSV files, or provide local CSV paths.")
else:
    # Read metadata (columns and available rows) for each source
    valid_entries = []
    for entry in source_entries:
        try:
            cols = _read_header_cols(entry["source"])
            first_col = cols[0] if len(cols) > 0 else None
            if entry["kind"] == "path":
                total_rows = _count_data_rows_for_path(entry["source"])
            else:
                _seek0_if_possible(entry["source"])
                total_rows = _count_data_rows_for_upload(entry["source"].getvalue())
        except Exception as exc:
            st.error(f"Cannot read file '{entry['label']}': {exc}")
            continue

        valid_entries.append(
            {
                **entry,
                "cols": cols,
                "first_col": first_col,
                "total_rows": total_rows,
            }
        )

    if len(valid_entries) == 0:
        st.stop()

    max_total_rows = max(e["total_rows"] for e in valid_entries)
    reference_entry = max(valid_entries, key=lambda x: x["total_rows"])
    reference_label = reference_entry["label"]

    left, right = st.columns([1, 2])
    with left:
        has_any_first_col = any(e["first_col"] is not None for e in valid_entries)
        use_first_col_as_timestamp = st.checkbox(
            "Use each file first column as timestamp (X axis)",
            value=False,
            disabled=not has_any_first_col,
        )
        timestamp_unit = None
        if use_first_col_as_timestamp:
            # For numeric timestamps (epoch), unit is required to interpret correctly.
            # For string timestamps, unit is ignored.
            timestamp_unit = st.selectbox(
                "Timestamp unit (epoch)",
                options=["auto", "s", "ms", "us", "ns"],
                index=1,  # ms as a sensible default for PLC logs
                help="Used only if the timestamp column is numeric (epoch). For ISO/date strings keep 'auto'.",
            )

        trace_options = []
        for e in valid_entries:
            for c in e["cols"]:
                if use_first_col_as_timestamp and e["first_col"] is not None and c == e["first_col"]:
                    continue
                trace_options.append(f"{e['label']} | {c}")

        selected_traces = st.multiselect("Y columns (multi-file)", trace_options, default=[])
        y_scale_ref = st.selectbox(
            "Y scale reference (for minmax)",
            selected_traces,
            disabled=len(selected_traces) == 0,
        )
        minmax = st.checkbox(
            "minmax (normalize Y to reference min/max)",
            value=False,
            disabled=len(selected_traces) == 0,
        )
        cycle_time_by_file = {}
        shift_rows_by_file = {}
        if use_first_col_as_timestamp:
            st.caption("Cycle time per file is disabled because timestamp mode is active.")
        else:
            st.markdown("**Cycle time per file [s]**")
            for e in valid_entries:
                cycle_time_by_file[e["label"]] = st.number_input(
                    f"{e['label']}",
                    min_value=0.000001,
                    value=0.01,
                    step=0.001,
                    format="%.6f",
                    key=f"cycle_time_{e['id']}",
                )
            st.markdown(f"**X shift per file [rows]** (reference: `{reference_label}`)")
            for e in valid_entries:
                shift_rows_by_file[e["label"]] = st.number_input(
                    f"Shift {e['label']}",
                    min_value=-max_total_rows,
                    max_value=max_total_rows,
                    value=0,
                    step=1,
                    key=f"x_shift_rows_{e['id']}",
                    disabled=(e["label"] == reference_label),
                )

    with right:
        st.markdown("**Row range (0-based, data rows)**")
        st.caption(f"Max available rows across selected files: 0 .. {max_total_rows}")

        if "osc_start_row" not in st.session_state:
            st.session_state.osc_start_row = 0
        if "osc_end_row" not in st.session_state:
            st.session_state.osc_end_row = max_total_rows

        # Keep range inside max bounds
        st.session_state.osc_start_row = max(0, min(int(st.session_state.osc_start_row), max_total_rows))
        st.session_state.osc_end_row = max(0, min(int(st.session_state.osc_end_row), max_total_rows))

        row_range = st.slider(
            "Row range",
            min_value=0,
            max_value=max_total_rows,
            value=(int(st.session_state.osc_start_row), int(st.session_state.osc_end_row)),
            step=1,
        )
        start_row, end_row = int(row_range[0]), int(row_range[1])
        st.session_state.osc_start_row = start_row
        st.session_state.osc_end_row = end_row

        suggested = max(1, int((max(1, abs(end_row - start_row) + 1)) / 50000))
        downsample_step = st.number_input(
            "Downsample (keep 1 every N rows)",
            min_value=1,
            value=suggested,
            step=1,
            help="Use 1 for no downsampling (may be slow on very large ranges).",
        )

    if len(selected_traces) == 0:
        st.info("Select one or more columns in **Y columns (multi-file)** to plot.")
    else:
        # Parse selected traces "file | column"
        # Keep a stable order (Streamlit selection order) and avoid set() to prevent
        # any accidental re-ordering / ambiguity when building usecols.
        selected_by_file: dict[str, list[str]] = {}
        for token in selected_traces:
            file_label, col_name = token.split(" | ", 1)
            selected_by_file.setdefault(file_label, [])
            if col_name not in selected_by_file[file_label]:
                selected_by_file[file_label].append(col_name)

        fig = go.Figure()
        series_map = {}
        x_title = "time [s]" if not use_first_col_as_timestamp else "timestamp"
        if not use_first_col_as_timestamp:
            ref_cycle_time_s = float(cycle_time_by_file.get(reference_label, 0.01))
            ref_x_min = float(start_row) * ref_cycle_time_s
            ref_x_max = float(end_row) * ref_cycle_time_s

        for e in valid_entries:
            if e["label"] not in selected_by_file:
                continue
            if start_row > e["total_rows"]:
                # This file has already ended in the selected range
                continue

            local_end_row = min(end_row, e["total_rows"])

            cols_for_this_file = list(selected_by_file[e["label"]])
            usecols = list(cols_for_this_file)
            if use_first_col_as_timestamp and e["first_col"] is not None and e["first_col"] not in usecols:
                usecols = [e["first_col"]] + usecols

            try:
                df = _read_slice(e["source"], start_row, local_end_row, usecols=usecols)
            except Exception as exc:
                st.warning(f"Skip '{e['label']}' due to read error: {exc}")
                continue

            if use_first_col_as_timestamp and e["first_col"] is not None and e["first_col"] in df.columns:
                x_raw = df[e["first_col"]]
                # If it's numeric, interpret as epoch with the selected unit.
                x_numeric = pd.to_numeric(x_raw, errors="coerce")
                if x_numeric.notna().any():
                    unit = None if (timestamp_unit in (None, "auto")) else str(timestamp_unit)
                    x_vals = pd.to_datetime(x_numeric, errors="coerce", unit=unit)
                else:
                    x_vals = pd.to_datetime(x_raw, errors="coerce")
                x_title = e["first_col"]
            else:
                cycle_time_s = float(cycle_time_by_file.get(e["label"], 0.01))
                start_time_s = float(start_row) * cycle_time_s
                x_vals = pd.Series(
                    [start_time_s + i * cycle_time_s for i in range(len(df))],
                    name="time_s",
                )
                shift_rows = int(shift_rows_by_file.get(e["label"], 0))
                x_vals = x_vals + (shift_rows * cycle_time_s)

            for c in cols_for_this_file:
                if c in df.columns:
                    df[c] = pd.to_numeric(df[c], errors="coerce")

            if downsample_step > 1:
                step = int(downsample_step)
                df = df.iloc[::step]
                x_vals = x_vals.iloc[::step]

            for c in cols_for_this_file:
                if c not in df.columns:
                    continue

                trace_name = f"{e['label']} | {c}"
                # Align by position to avoid pandas index mismatches after slicing/downsampling
                x_series = pd.Series(x_vals).reset_index(drop=True)
                series = df[c].reset_index(drop=True)
                if not use_first_col_as_timestamp:
                    # Hide samples outside reference X range
                    mask = ((x_series >= ref_x_min) & (x_series <= ref_x_max)).to_numpy()
                    x_plot = x_series.to_numpy()[mask]
                    y_plot = series.to_numpy()[mask]
                else:
                    x_plot = x_series.to_numpy()
                    y_plot = series.to_numpy()
                series_map[trace_name] = (x_plot, y_plot)

        if len(series_map) == 0:
            st.warning("No valid data to plot in selected range.")
        else:
            ref_min = ref_max = None
            if minmax and y_scale_ref in series_map:
                ref_series = series_map[y_scale_ref][1]
                ref_arr = np.asarray(ref_series, dtype=float)
                finite = np.isfinite(ref_arr)
                if finite.any():
                    ref_min = float(np.nanmin(ref_arr[finite]))
                    ref_max = float(np.nanmax(ref_arr[finite]))

            for trace_name in selected_traces:
                if trace_name not in series_map:
                    continue
                x_vals, series = series_map[trace_name]

                if minmax and ref_min is not None and ref_max is not None:
                    arr = np.asarray(series, dtype=float)
                    finite = np.isfinite(arr)
                    if finite.any():
                        s_min = float(np.nanmin(arr[finite]))
                        s_max = float(np.nanmax(arr[finite]))
                    else:
                        s_min = s_max = np.nan

                    # Avoid minmax-scaling discrete/status signals (0/1/32, etc.):
                    # scaling them to the reference range creates tall "bars" that ruin readability.
                    col_name = trace_name.split(" | ", 1)[1] if " | " in trace_name else trace_name
                    col_l = col_name.lower()
                    is_likely_discrete = ("status" in col_l) or ("command" in col_l)
                    if finite.any():
                        finite_vals = arr[finite]
                        # Fast heuristic: few unique values and small span -> discrete.
                        uniq = np.unique(finite_vals[:200000])  # cap to keep it fast on huge arrays
                        if uniq.size <= 10 and np.isfinite(s_min) and np.isfinite(s_max) and (s_max - s_min) <= 50:
                            is_likely_discrete = True

                    if (not is_likely_discrete) and np.isfinite(s_min) and np.isfinite(s_max) and s_max != s_min:
                        series = (arr - s_min) / (s_max - s_min)
                        series = series * (ref_max - ref_min) + ref_min

                fig.add_trace(
                    go.Scatter(
                        x=x_vals,
                        y=series,
                        mode="lines",
                        name=trace_name,
                        hovertemplate=(
                            f"<b>{x_title}</b>: %{{x}}<br>"
                            f"<b>{trace_name}</b>: %{{y:.6g}}<extra></extra>"
                        ),
                    )
                )

            fig.update_layout(
                height=650,
                margin=dict(l=10, r=10, t=40, b=10),
                hovermode="x unified",
                legend=dict(orientation="h"),
                xaxis_title=x_title,
                yaxis_title="Value",
            )
            st.plotly_chart(fig, width="stretch")
