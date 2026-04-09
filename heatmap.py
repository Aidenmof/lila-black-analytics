"""
heatmap.py
----------
Density heatmap overlays using all filtered matches (not just one match).

Kill zone   → where kills/bot-kills happened (red)
Death zone  → where players died (purple)
Traffic     → where players spent time (blue)
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy.stats import gaussian_kde
import streamlit as st

HEATMAP_CONFIG = {
    "kill_zone": {
        "event_types": ["Kill", "BotKill"],
        "colorscale": "Reds",
        "label": "Kill zones",
    },
    "death_zone": {
        "event_types": ["Killed", "BotKilled", "KilledByStorm"],
        "colorscale": "Purples",
        "label": "Death zones",
    },
    "traffic": {
        "event_types": ["Position", "BotPosition"],
        "colorscale": "Blues",
        "label": "Player traffic",
    },
}


def _compute_density(
    df: pd.DataFrame,
    event_types: list[str],
    resolution: int = 100,
) -> np.ndarray | None:
    """Compute 2D KDE density grid. Returns None if not enough data."""
    sub = df[df["event_type"].isin(event_types)][["pixel_x", "pixel_y"]].dropna()
    if len(sub) < 2:
        return None

    xs = np.linspace(0, 1024, resolution)
    ys = np.linspace(0, 1024, resolution)
    xx, yy = np.meshgrid(xs, ys)

    kde = gaussian_kde(
        np.vstack([sub["pixel_x"].values, sub["pixel_y"].values]),
        bw_method="scott",
    )
    density = kde(np.vstack([xx.ravel(), yy.ravel()])).reshape(resolution, resolution)

    d_min, d_max = density.min(), density.max()
    if d_max > d_min:
        density = (density - d_min) / (d_max - d_min)

    return density


def add_heatmap_overlay(
    fig: go.Figure,
    df: pd.DataFrame,
    heatmap_type: str,
    opacity: float = 0.5,
    resolution: int = 100,
) -> go.Figure:
    """Add one heatmap trace to the figure."""
    cfg = HEATMAP_CONFIG[heatmap_type]
    density = _compute_density(df, cfg["event_types"], resolution)
    if density is None:
        return fig

    xs = np.linspace(0, 1024, resolution)
    ys = np.linspace(0, 1024, resolution)
    density_masked = np.where(density < 0.05, np.nan, density)

    fig.add_trace(go.Heatmap(
        x=xs, y=ys, z=density_masked,
        colorscale=cfg["colorscale"],
        opacity=opacity,
        showscale=False,
        name=cfg["label"],
        hoverinfo="skip",
        zsmooth="best",
    ))
    return fig


def render_heatmap_controls() -> tuple[list[str], float]:
    """Sidebar checkboxes and opacity slider for heatmaps."""
    st.sidebar.markdown("### Heatmap overlays")
    selected = []
    for key, cfg in HEATMAP_CONFIG.items():
        if st.sidebar.checkbox(cfg["label"], value=False, key=f"hm_{key}"):
            selected.append(key)

    opacity = st.sidebar.slider(
        "Heatmap opacity", 0.1, 1.0, 0.5, 0.05,
        disabled=len(selected) == 0,
    )
    return selected, opacity
