"""
event_markers.py
----------------
Overlays event markers on the map for LILA BLACK events:

  Kill / BotKill   → red X      (you killed someone)
  Killed/BotKilled → dark skull (you were killed)
  KilledByStorm    → purple dot (storm death)
  Loot             → gold diamond
"""

import plotly.graph_objects as go
import pandas as pd
import streamlit as st

# Map LILA BLACK event names to display style
EVENT_STYLES = {
    "Kill": {
        "symbol": "x", "color": "#E63946", "size": 10, "label": "🔴 Kill (you killed)",
    },
    "BotKill": {
        "symbol": "x", "color": "#FF6B6B", "size": 9, "label": "🔴 Bot kill",
    },
    "Killed": {
        "symbol": "circle-x", "color": "#2D2D2D", "size": 10, "label": "💀 Killed by player",
    },
    "BotKilled": {
        "symbol": "circle-x", "color": "#555555", "size": 9, "label": "💀 Killed by bot",
    },
    "KilledByStorm": {
        "symbol": "circle", "color": "#9B59B6", "size": 10, "label": "🟣 Storm death",
    },
    "Loot": {
        "symbol": "diamond", "color": "#FFD700", "size": 8, "label": "💛 Loot",
    },
}

# Events that are NOT movement (used for filtering)
NON_MOVE_EVENTS = set(EVENT_STYLES.keys())


def add_event_markers(
    fig: go.Figure,
    df: pd.DataFrame,
    match_id: str,
    max_timestamp: int | None = None,
    show_events: list[str] | None = None,
) -> go.Figure:
    """Add event marker traces to an existing Plotly figure."""
    if show_events is None:
        show_events = list(EVENT_STYLES.keys())

    sub = df[
        (df["match_id"] == match_id) &
        (df["event_type"].isin(show_events))
    ].copy()

    if max_timestamp is not None:
        sub = sub[sub["timestamp"] <= max_timestamp]

    for event_type, style in EVENT_STYLES.items():
        if event_type not in show_events:
            continue
        rows = sub[sub["event_type"] == event_type]
        if rows.empty:
            continue

        fig.add_trace(go.Scatter(
            x=rows["pixel_x"],
            y=rows["pixel_y"],
            mode="markers",
            name=style["label"],
            marker=dict(
                symbol=style["symbol"],
                color=style["color"],
                size=style["size"],
                line=dict(color="white", width=1),
            ),
            hovertemplate=(
                f"<b>{style['label']}</b><br>"
                "Player: %{customdata}<br>"
                "X: %{x:.0f}, Y: %{y:.0f}<extra></extra>"
            ),
            customdata=rows["player_id"].str[:8],
        ))

    return fig


def render_event_toggle(available_events: list[str]) -> list[str]:
    """Sidebar checkboxes to show/hide each event type."""
    st.sidebar.markdown("### Event markers")
    selected = []
    for event_type, style in EVENT_STYLES.items():
        if event_type not in available_events:
            continue
        if st.sidebar.checkbox(style["label"], value=True, key=f"evt_{event_type}"):
            selected.append(event_type)
    return selected
