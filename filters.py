"""
filters.py
----------
Sidebar filter widgets. Returns a filtered DataFrame based on user selections.
"""

import streamlit as st
import pandas as pd


def render_filters(df: pd.DataFrame) -> tuple[pd.DataFrame, str]:
    """
    Draw sidebar filters and return (filtered_df, selected_map_name).
    """
    st.sidebar.header("🗺️ Filters")

    # ── 1. Map ───────────────────────────────────────────────────────────────
    available_maps = sorted(df["map_name"].unique().tolist())
    selected_map = st.sidebar.selectbox(
        "Map",
        options=available_maps,
        help="Choose which map to display.",
    )
    df = df[df["map_name"] == selected_map]

    # ── 2. Date range ────────────────────────────────────────────────────────
    min_date = df["date"].min()
    max_date = df["date"].max()

    date_range = st.sidebar.date_input(
        "Date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
        start_date, end_date = date_range
        df = df[(df["date"] >= start_date) & (df["date"] <= end_date)]

    # ── 3. Match selector ────────────────────────────────────────────────────
    available_matches = sorted(df["match_id"].unique().tolist())[:200]
    selected_matches = st.sidebar.multiselect(
        "Match IDs",
        options=available_matches,
        default=[],
        placeholder="All matches",
        help="Leave blank for all. Select one or more to focus.",
    )
    if selected_matches:
        df = df[df["match_id"].isin(selected_matches)]

    # ── 4. Player type ───────────────────────────────────────────────────────
    player_type = st.sidebar.radio(
        "Player type",
        options=["Humans + Bots", "Humans only", "Bots only"],
    )
    if player_type == "Humans only":
        df = df[~df["is_bot"]]
    elif player_type == "Bots only":
        df = df[df["is_bot"]]

    # ── Summary ──────────────────────────────────────────────────────────────
    st.sidebar.markdown("---")
    st.sidebar.caption(
        f"**{len(df):,}** events · "
        f"**{df['match_id'].nunique()}** matches · "
        f"**{df['player_id'].nunique()}** players"
    )

    return df, selected_map


def get_selected_match(df: pd.DataFrame) -> str | None:
    """Pick a single match to inspect in the journey and timeline views."""
    matches = sorted(df["match_id"].unique().tolist())
    if not matches:
        st.warning("No matches found with the current filters.")
        return None
    return st.selectbox(
        "Select a match to inspect",
        options=matches,
        help="All players in this match will be shown on the map.",
    )
