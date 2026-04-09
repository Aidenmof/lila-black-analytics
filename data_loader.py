"""
data_loader.py
--------------
Loads LILA BLACK telemetry files from the date subfolders.

Your files:
  - Live in subfolders: data/February_10/, data/February_11/, etc.
  - Have no .parquet extension (they end in .nakama-0) but ARE valid parquet files
  - Each file = one player's journey through one match
  - The 'event' column is stored as bytes and needs to be decoded to text
  - is_bot is determined by the user_id: UUID = human, short number = bot
"""

import streamlit as st
import pandas as pd
import pyarrow.parquet as pq
import pathlib
import re

DATA_FOLDER = "data"

DATE_FOLDERS = [
    "February_10",
    "February_11",
    "February_12",
    "February_13",
    "February_14",
]

# Rename your columns to standard names used throughout the app
COLUMN_RENAME = {
    "user_id": "player_id",
    "map_id":  "map_name",
    "ts":      "timestamp",
    "event":   "event_type",
}

# A UUID looks like: f4e072fa-b7af-4761-b567-1d95b7ad0108
UUID_PATTERN = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE,
)


def _is_bot(user_id: str) -> bool:
    """Bots have short numeric IDs like '1440'. Humans have UUIDs."""
    return not bool(UUID_PATTERN.match(str(user_id)))


def _parse_date(folder_name: str) -> str:
    """'February_10' → '2026-02-10'"""
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


def _load_single_file(filepath: pathlib.Path, date_str: str) -> pd.DataFrame | None:
    """Load one .nakama-0 parquet file. Returns None if unreadable."""
    try:
        df = pq.read_table(str(filepath)).to_pandas()
    except Exception:
        return None

    if df.empty:
        return None

    # Decode event bytes → string
    if "event" in df.columns:
        df["event"] = df["event"].apply(
            lambda x: x.decode("utf-8") if isinstance(x, bytes) else str(x)
        )

    # Add date and is_bot columns
    df["date"] = _parse_date(date_str)
    if "user_id" in df.columns:
        df["is_bot"] = df["user_id"].apply(_is_bot)

    df = df.rename(columns=COLUMN_RENAME)
    return df


@st.cache_data(show_spinner="Loading telemetry data… (first load takes ~30 seconds)")
def load_all_data(data_folder: str = DATA_FOLDER) -> pd.DataFrame:
    """
    Walk all date subfolders and load every file into one big DataFrame.
    Cached — only slow on the very first load.
    """
    base = pathlib.Path(data_folder)
    all_frames = []
    progress = st.progress(0, text="Reading files…")

    for i, folder_name in enumerate(DATE_FOLDERS):
        folder_path = base / folder_name
        if not folder_path.exists():
            continue
        for f in folder_path.iterdir():
            if f.is_file():
                df = _load_single_file(f, folder_name)
                if df is not None:
                    all_frames.append(df)
        progress.progress((i + 1) / len(DATE_FOLDERS), text=f"Loaded {folder_name}…")

    progress.empty()

    if not all_frames:
        st.error(
            f"No data files found in '{data_folder}/'. "
            "Make sure your February_10 … February_14 subfolders are inside data/."
        )
        st.stop()

    combined = pd.concat(all_frames, ignore_index=True)
    combined["timestamp"] = pd.to_numeric(combined["timestamp"], errors="coerce")
    combined["date"] = pd.to_datetime(combined["date"]).dt.date
    combined = combined.dropna(subset=["x", "z", "timestamp"])
    return combined


def get_summary(df: pd.DataFrame) -> dict:
    return {
        "Total events":   f"{len(df):,}",
        "Unique matches": df["match_id"].nunique(),
        "Unique players": df["player_id"].nunique(),
        "Maps":           ", ".join(sorted(df["map_name"].unique())),
        "Date range":     f"{df['date'].min()} → {df['date'].max()}",
    }
