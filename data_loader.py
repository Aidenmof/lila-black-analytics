"""
data_loader.py — LILA BLACK
Loads telemetry from local data/ folder if it exists,
otherwise shows a file uploader in the sidebar.
"""

import streamlit as st
import pandas as pd
import pyarrow.parquet as pq
import pathlib
import re
import io

DATA_FOLDER = "data"

DATE_FOLDERS = [
    "February_10", "February_11", "February_12",
    "February_13", "February_14",
]

COLUMN_RENAME = {
    "user_id": "player_id",
    "map_id":  "map_name",
    "ts":      "timestamp",
    "event":   "event_type",
}

UUID_PATTERN = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE,
)


def _is_bot(user_id: str) -> bool:
    return not bool(UUID_PATTERN.match(str(user_id)))


def _parse_date(folder_name: str) -> str:
    month_map = {
        "January": "01", "February": "02", "March": "03", "April": "04",
        "May": "05", "June": "06", "July": "07", "August": "08",
        "September": "09", "October": "10", "November": "11", "December": "12",
    }
    try:
        parts = folder_name.split("_")
        month = month_map.get(parts[0], "01")
        day = parts[1].zfill(2)
        return f"2026-{month}-{day}"
    except Exception:
        return "2026-01-01"


def _clean(df: pd.DataFrame, date_str: str) -> pd.DataFrame | None:
    if df is None or df.empty:
        return None
    if "event" in df.columns:
        df["event"] = df["event"].apply(
            lambda x: x.decode("utf-8") if isinstance(x, bytes) else str(x)
        )
    df["date"] = date_str
    if "user_id" in df.columns:
        df["is_bot"] = df["user_id"].apply(_is_bot)
    df = df.rename(columns=COLUMN_RENAME)
    return df


def _load_file_bytes(file_bytes: bytes, date_str: str) -> pd.DataFrame | None:
    try:
        df = pq.read_table(io.BytesIO(file_bytes)).to_pandas()
        return _clean(df, date_str)
    except Exception:
        return None


def _load_local_file(path: pathlib.Path, date_str: str) -> pd.DataFrame | None:
    try:
        df = pq.read_table(str(path)).to_pandas()
        return _clean(df, date_str)
    except Exception:
        return None


def _finalise(frames: list) -> pd.DataFrame:
    combined = pd.concat(frames, ignore_index=True)
    combined["timestamp"] = pd.to_numeric(combined["timestamp"], errors="coerce")
    combined["date"] = pd.to_datetime(combined["date"]).dt.date
    combined = combined.dropna(subset=["x", "z", "timestamp"])
    return combined


@st.cache_data(show_spinner="Loading telemetry data…")
def _load_local(data_folder: str) -> pd.DataFrame:
    base = pathlib.Path(data_folder)
    frames = []
    progress = st.progress(0, text="Reading files…")
    for i, folder_name in enumerate(DATE_FOLDERS):
        folder_path = base / folder_name
        if not folder_path.exists():
            continue
        for f in folder_path.iterdir():
            if f.is_file():
                df = _load_local_file(f, _parse_date(folder_name))
                if df is not None:
                    frames.append(df)
        progress.progress((i + 1) / len(DATE_FOLDERS), text=f"Loaded {folder_name}…")
    progress.empty()
    return _finalise(frames)


def load_all_data() -> pd.DataFrame:
    """
    Load data from local folder if available, otherwise show file uploader.
    """
    base = pathlib.Path(DATA_FOLDER)
    has_local_data = base.exists() and any(
        (base / f).exists() for f in DATE_FOLDERS
    )

    if has_local_data:
        return _load_local(DATA_FOLDER)

    # ── No local data: show uploader ─────────────────────────────────────────
    st.sidebar.markdown("### 📂 Upload data files")
    st.sidebar.caption(
        "Upload your `.nakama-0` telemetry files here. "
        "You can select multiple files at once (Ctrl+A in the folder)."
    )

    uploaded = st.sidebar.file_uploader(
        "Select telemetry files",
        accept_multiple_files=True,
        help="Select all files from one or more February_XX folders.",
        key="data_upload",
    )

    if not uploaded:
        st.info(
            "👈 Upload your telemetry files in the sidebar to get started.\n\n"
            "Select files from your `player_data/February_XX/` folders. "
            "You can select and upload hundreds at once."
        )
        st.stop()

    frames = []
    progress = st.progress(0, text="Reading uploaded files…")
    for i, f in enumerate(uploaded):
        # Guess date from filename if possible, default to February_10
        date_str = _parse_date("February_10")
        for folder in DATE_FOLDERS:
            day = folder.split("_")[1]
            if day in f.name:
                date_str = _parse_date(folder)
                break
        df = _load_file_bytes(f.read(), date_str)
        if df is not None:
            frames.append(df)
        progress.progress((i + 1) / len(uploaded))

    progress.empty()

    if not frames:
        st.error("Could not read any of the uploaded files.")
        st.stop()

    return _finalise(frames)


def get_summary(df: pd.DataFrame) -> dict:
    return {
        "Total events":   f"{len(df):,}",
        "Unique matches": df["match_id"].nunique(),
        "Unique players": df["player_id"].nunique(),
        "Maps":           ", ".join(sorted(df["map_name"].unique())),
        "Date range":     f"{df['date'].min()} → {df['date'].max()}",
    }
