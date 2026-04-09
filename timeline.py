"""
timeline.py
-----------
Timeline scrubber and match stats for LILA BLACK matches.
"""

import streamlit as st
import pandas as pd
import plotly.express as px

NON_MOVE_EVENTS = ["Kill", "BotKill", "Killed", "BotKilled", "KilledByStorm", "Loot"]

COLOR_MAP = {
    "Kill":          "#E63946",
    "BotKill":       "#FF6B6B",
    "Killed":        "#2D2D2D",
    "BotKilled":     "#555555",
    "KilledByStorm": "#9B59B6",
    "Loot":          "#FFD700",
}


def render_timeline(df: pd.DataFrame, match_id: str) -> int:
    """Render the playback slider. Returns the selected timestamp."""
    match_df = df[df["match_id"] == match_id]

    if match_df.empty:
        st.warning("No data for this match.")
        return 0

    t_min = int(match_df["timestamp"].min())
    t_max = int(match_df["timestamp"].max())

    if t_min == t_max:
        return t_max

    duration_s = (t_max - t_min) // 1000
    st.markdown(f"**Match duration:** {_fmt(duration_s)}")

    selected_ms = st.slider(
        "⏱️ Playback timeline",
        min_value=t_min,
        max_value=t_max,
        value=t_max,
        step=max(1, (t_max - t_min) // 200),
        format="%d ms",
        help="Drag left to rewind. Map shows only events up to this point.",
    )

    elapsed_s = (selected_ms - t_min) // 1000
    st.caption(f"Showing first **{_fmt(elapsed_s)}** of the match")
    return selected_ms


def render_event_timeline_chart(df: pd.DataFrame, match_id: str) -> None:
    """Bar chart of events per minute for the selected match."""
    match_df = df[
        (df["match_id"] == match_id) &
        (df["event_type"].isin(NON_MOVE_EVENTS))
    ].copy()

    if match_df.empty:
        st.info("No combat/loot events in this match.")
        return

    t_min = match_df["timestamp"].min()
    match_df["minute"] = ((match_df["timestamp"] - t_min) / 60_000).astype(int)

    counts = (
        match_df.groupby(["minute", "event_type"])
        .size()
        .reset_index(name="count")
    )

    fig = px.bar(
        counts, x="minute", y="count", color="event_type",
        barmode="stack",
        labels={"minute": "Minute", "count": "Events", "event_type": "Type"},
        title="Events per minute",
        color_discrete_map=COLOR_MAP,
        height=220,
    )
    fig.update_layout(
        margin=dict(l=0, r=0, t=30, b=0),
        legend=dict(orientation="h", y=-0.4),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, use_container_width=True)


def render_live_stats(df: pd.DataFrame, match_id: str, max_timestamp: int) -> None:
    """Metric cards showing match state at the current timeline position."""
    sub = df[
        (df["match_id"] == match_id) &
        (df["timestamp"] <= max_timestamp)
    ]

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Players",      sub["player_id"].nunique())
    c2.metric("Kills",        (sub["event_type"] == "Kill").sum())
    c3.metric("Bot kills",    (sub["event_type"] == "BotKill").sum())
    c4.metric("Deaths",       sub["event_type"].isin(["Killed","BotKilled"]).sum())
    c5.metric("Storm deaths", (sub["event_type"] == "KilledByStorm").sum())
    c6.metric("Loot",         (sub["event_type"] == "Loot").sum())


def _fmt(seconds: int) -> str:
    m, s = divmod(int(seconds), 60)
    return f"{m:02d}:{s:02d}"
