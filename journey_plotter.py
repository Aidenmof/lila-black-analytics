"""
journey_plotter.py
------------------
Draws player movement paths on the minimap.

Movement events in LILA BLACK:
  - 'Position'    → human player moved
  - 'BotPosition' → bot moved

Humans get solid lines, bots get dotted lines.
Each player gets a distinct colour.
"""

import plotly.graph_objects as go
import pandas as pd
from PIL import Image
from pathlib import Path

PLAYER_COLORS = [
    "#E63946", "#457B9D", "#2A9D8F", "#E9C46A", "#F4A261",
    "#A8DADC", "#264653", "#E76F51", "#6A4C93", "#1982C4",
    "#8AC926", "#FF595E", "#FFCA3A", "#52B788", "#D62828",
    "#023E8A", "#80B918", "#E07A5F", "#3D405B", "#9B59B6",
]

# Events that represent movement
MOVE_EVENTS = {"Position", "BotPosition"}


def plot_journeys(
    df: pd.DataFrame,
    map_name: str,
    minimap_path: Path | None,
    match_id: str,
    max_timestamp: int | None = None,
) -> go.Figure:
    """
    Build a Plotly figure showing all player paths for one match.
    """
    match_df = df[
        (df["match_id"] == match_id) &
        (df["event_type"].isin(MOVE_EVENTS))
    ].copy()

    if max_timestamp is not None:
        match_df = match_df[match_df["timestamp"] <= max_timestamp]

    match_df = match_df.sort_values(["player_id", "timestamp"])

    # Canvas size
    if minimap_path and minimap_path.exists():
        img = Image.open(minimap_path)
        img_w, img_h = img.size
    else:
        img = None
        img_w, img_h = 1024, 1024

    fig = go.Figure()

    # Minimap as background
    if img:
        fig.add_layout_image(dict(
            source=img,
            x=0, y=img_h,
            xref="x", yref="y",
            sizex=img_w, sizey=img_h,
            sizing="stretch",
            layer="below",
            opacity=1.0,
        ))

    # One line per player
    players = match_df["player_id"].unique()
    for i, player_id in enumerate(players):
        player_df = match_df[match_df["player_id"] == player_id]
        if player_df.empty:
            continue

        is_bot = bool(player_df["is_bot"].iloc[0])
        color = PLAYER_COLORS[i % len(PLAYER_COLORS)]
        label = f"{'🤖 Bot' if is_bot else '👤 Human'}: {str(player_id)[:8]}"

        fig.add_trace(go.Scatter(
            x=player_df["pixel_x"],
            y=player_df["pixel_y"],
            mode="lines",
            name=label,
            line=dict(color=color, width=2, dash="dot" if is_bot else "solid"),
            hovertemplate=f"<b>{label}</b><br>X: %{{x:.0f}}, Y: %{{y:.0f}}<extra></extra>",
            opacity=0.85,
        ))

    fig.update_layout(
        title=f"Player journeys — {map_name} / {str(match_id)[:16]}…",
        xaxis=dict(range=[0, img_w], showgrid=False, zeroline=False, visible=False),
        yaxis=dict(range=[0, img_h], showgrid=False, zeroline=False, visible=False,
                   scaleanchor="x"),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(bgcolor="rgba(0,0,0,0.5)", font=dict(color="white", size=11),
                    x=1.01, y=1),
        margin=dict(l=0, r=0, t=40, b=0),
        height=600,
    )
    return fig
