"""
app.py
------
Game Analytics Dashboard — main Streamlit entry point.

Run with:
    streamlit run app.py

To deploy (free hosting):
    1. Push this repo to GitHub
    2. Go to https://share.streamlit.io
    3. Connect your repo and set the main file to app.py
    4. Done — you get a shareable URL

Folder structure expected:
    data/          ← put your .parquet files here
    assets/
      minimaps/    ← put your minimap .png images here
    src/           ← all modules live here
"""

import streamlit as st
from pathlib import Path
from PIL import Image

# ── Page config (must be the very first Streamlit call) ──────────────────────
st.set_page_config(
    page_title="Game Analytics",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Local imports ─────────────────────────────────────────────────────────────
from src.data_loader import load_all_parquet, get_summary
from src.filters import render_filters, get_selected_match
from src.coordinate_mapper import add_pixel_coords, get_minimap_path
from src.journey_plotter import plot_journeys
from src.event_markers import add_event_markers, render_event_toggle
from src.heatmap import add_heatmap_overlay, render_heatmap_controls
from src.timeline import (
    render_timeline,
    render_event_timeline_chart,
    render_live_stats,
)

# ── Constants ─────────────────────────────────────────────────────────────────
DATA_FOLDER = "data"          # folder containing .parquet files
MINIMAP_SIZE = (1024, 1024)   # expected pixel dimensions of minimap images


# ═════════════════════════════════════════════════════════════════════════════
# Sidebar: data upload + filters
# ═════════════════════════════════════════════════════════════════════════════

st.sidebar.title("🎮 Game Analytics")
st.sidebar.markdown("---")

# Allow users to optionally upload a parquet file directly in the browser
uploaded_file = st.sidebar.file_uploader(
    "Upload a parquet file (optional)",
    type=["parquet"],
    help="Upload your own telemetry data. Alternatively, drop files into the data/ folder.",
)


# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Loading telemetry…")
def load_uploaded(file_bytes: bytes) -> "pd.DataFrame":
    import pandas as pd, io
    return pd.read_parquet(io.BytesIO(file_bytes))


if uploaded_file:
    import pandas as pd
    raw_df = load_uploaded(uploaded_file.read())
    # Minimal validation: show columns if something looks wrong
    st.sidebar.success(f"Loaded {len(raw_df):,} rows from upload.")
else:
    raw_df = load_all_parquet(DATA_FOLDER)

# ── Summary stats ─────────────────────────────────────────────────────────────
summary = get_summary(raw_df)
with st.sidebar.expander("📊 Dataset summary", expanded=False):
    for k, v in summary.items():
        st.write(f"**{k}:** {v}")

st.sidebar.markdown("---")

# ── Filters ────────────────────────────────────────────────────────────────────
filtered_df, selected_map = render_filters(raw_df)

# ── Event marker toggles ───────────────────────────────────────────────────────
available_event_types = filtered_df["event_type"].unique().tolist()
show_events = render_event_toggle(available_event_types)

# ── Heatmap controls ───────────────────────────────────────────────────────────
selected_heatmaps, heatmap_opacity = render_heatmap_controls()


# ═════════════════════════════════════════════════════════════════════════════
# Main area
# ═════════════════════════════════════════════════════════════════════════════

st.title("🗺️ Player Behavior Explorer")

if filtered_df.empty:
    st.warning("No data matches the current filters. Try adjusting the sidebar.")
    st.stop()

# ── Get minimap image & convert coordinates ────────────────────────────────────
minimap_path = get_minimap_path(selected_map)

if minimap_path:
    minimap_img = Image.open(minimap_path)
    img_w, img_h = minimap_img.size
else:
    minimap_img = None
    img_w, img_h = MINIMAP_SIZE
    st.info(
        f"No minimap image found for **{selected_map}**. "
        f"Add a PNG to `assets/minimaps/` and register it in `coordinate_mapper.py`."
    )

# Map world coords → pixel coords for the selected map
display_df = add_pixel_coords(filtered_df, selected_map, img_w, img_h)


# ── Tabs for the three main views ─────────────────────────────────────────────
tab_journey, tab_heatmap, tab_stats = st.tabs([
    "🧭 Player Journeys",
    "🌡️ Heatmaps",
    "📈 Match Stats",
])


# ─────────────────────────────────────────────────────────────────────────────
# TAB 1: Player Journeys + Timeline
# ─────────────────────────────────────────────────────────────────────────────
with tab_journey:
    st.markdown("### Select a match")
    match_id = get_selected_match(display_df)

    if match_id:
        # Timeline scrubber
        st.markdown("---")
        max_ts = render_timeline(display_df, match_id)

        # Live stats at the current playback position
        st.markdown("---")
        render_live_stats(display_df, match_id, max_ts)
        st.markdown("---")

        # Build the figure
        fig = plot_journeys(
            df=display_df,
            map_name=selected_map,
            minimap_path=minimap_path,
            match_id=match_id,
            max_timestamp=max_ts,
        )

        # Overlay event markers
        if show_events:
            fig = add_event_markers(
                fig=fig,
                df=display_df,
                match_id=match_id,
                max_timestamp=max_ts,
                show_events=show_events,
            )

        st.plotly_chart(fig, use_container_width=True)

        # Events-per-minute chart
        with st.expander("📊 Events per minute", expanded=False):
            render_event_timeline_chart(display_df, match_id)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 2: Heatmaps (across all matches in the filter)
# ─────────────────────────────────────────────────────────────────────────────
with tab_heatmap:
    st.markdown(
        "Heatmaps aggregate **all filtered matches** — "
        "select a map and date range in the sidebar to narrow the scope."
    )

    if not selected_heatmaps:
        st.info("Enable at least one heatmap overlay in the sidebar (🌡️ Heatmap overlays).")
    else:
        import plotly.graph_objects as go

        # Start with a blank figure sized to the minimap
        fig_hm = go.Figure()

        if minimap_img:
            fig_hm.add_layout_image(
                dict(
                    source=minimap_img,
                    x=0, y=img_h,
                    xref="x", yref="y",
                    sizex=img_w, sizey=img_h,
                    sizing="stretch",
                    layer="below",
                    opacity=1.0,
                )
            )

        for hm_type in selected_heatmaps:
            fig_hm = add_heatmap_overlay(
                fig=fig_hm,
                df=display_df,
                heatmap_type=hm_type,
                image_width=img_w,
                image_height=img_h,
                opacity=heatmap_opacity,
            )

        fig_hm.update_layout(
            xaxis=dict(range=[0, img_w], showgrid=False, visible=False),
            yaxis=dict(range=[0, img_h], showgrid=False, visible=False, scaleanchor="x"),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=0, t=0, b=0),
            height=600,
        )

        st.plotly_chart(fig_hm, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 3: Aggregate Statistics
# ─────────────────────────────────────────────────────────────────────────────
with tab_stats:
    import plotly.express as px

    st.markdown("### Aggregate match statistics")

    # Non-movement events only
    events_df = display_df[display_df["event_type"] != "move"]

    col_a, col_b = st.columns(2)

    with col_a:
        # Event type breakdown
        event_counts = events_df["event_type"].value_counts().reset_index()
        event_counts.columns = ["Event type", "Count"]
        fig_ec = px.bar(
            event_counts,
            x="Event type",
            y="Count",
            color="Event type",
            title="Event breakdown",
            color_discrete_map={
                "kill": "#E63946",
                "death": "#2D2D2D",
                "loot": "#FFD700",
                "storm_death": "#9B59B6",
            },
        )
        fig_ec.update_layout(showlegend=False, height=300,
                             plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_ec, use_container_width=True)

    with col_b:
        # Human vs bot event share
        player_type_counts = (
            events_df.groupby("is_bot")["event_type"]
            .count()
            .reset_index()
        )
        player_type_counts["Player type"] = player_type_counts["is_bot"].map(
            {True: "Bot", False: "Human"}
        )
        fig_pt = px.pie(
            player_type_counts,
            names="Player type",
            values="event_type",
            title="Human vs Bot event share",
            color="Player type",
            color_discrete_map={"Human": "#457B9D", "Bot": "#E9C46A"},
        )
        fig_pt.update_layout(height=300,
                             plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_pt, use_container_width=True)

    # Top killers table
    st.markdown("#### Top players by kills")
    kills_df = (
        display_df[display_df["event_type"] == "kill"]
        .groupby(["player_id", "is_bot"])
        .size()
        .reset_index(name="kills")
        .sort_values("kills", ascending=False)
        .head(20)
    )
    kills_df["player_id"] = kills_df["player_id"].str[:12]
    kills_df["is_bot"] = kills_df["is_bot"].map({True: "🤖 Bot", False: "👤 Human"})
    kills_df.columns = ["Player ID", "Type", "Kills"]
    st.dataframe(kills_df, use_container_width=True, hide_index=True)
