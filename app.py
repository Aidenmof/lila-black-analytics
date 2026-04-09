"""
app.py — LILA BLACK Game Analytics Dashboard
---------------------------------------------
Run with:   streamlit run app.py
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from PIL import Image

st.set_page_config(
    page_title="LILA BLACK Analytics",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded",
)

from src.data_loader import load_all_data, get_summary
from src.filters import render_filters, get_selected_match
from src.coordinate_mapper import add_pixel_coords, get_minimap_path
from src.journey_plotter import plot_journeys
from src.event_markers import add_event_markers, render_event_toggle, NON_MOVE_EVENTS
from src.heatmap import add_heatmap_overlay, render_heatmap_controls
from src.timeline import render_timeline, render_event_timeline_chart, render_live_stats


# ── Sidebar header ────────────────────────────────────────────────────────────
st.sidebar.title("🎮 LILA BLACK Analytics")
st.sidebar.markdown("---")

# ── Load data ─────────────────────────────────────────────────────────────────
raw_df = load_all_data()

with st.sidebar.expander("📊 Dataset summary", expanded=False):
    for k, v in get_summary(raw_df).items():
        st.write(f"**{k}:** {v}")

st.sidebar.markdown("---")

# ── Filters ───────────────────────────────────────────────────────────────────
filtered_df, selected_map = render_filters(raw_df)

# ── Event & heatmap controls ──────────────────────────────────────────────────
available_events = filtered_df["event_type"].unique().tolist()
show_events      = render_event_toggle(available_events)
selected_heatmaps, heatmap_opacity = render_heatmap_controls()


# ── Main area ─────────────────────────────────────────────────────────────────
st.title("🗺️ LILA BLACK — Player Behavior Explorer")

if filtered_df.empty:
    st.warning("No data matches the current filters.")
    st.stop()

# Get minimap image
minimap_path = get_minimap_path(selected_map)
if minimap_path:
    minimap_img = Image.open(minimap_path)
    img_w, img_h = minimap_img.size
else:
    minimap_img = None
    img_w, img_h = 1024, 1024
    st.info(f"Minimap image not found for {selected_map}. Check assets/minimaps/.")

# Convert world coords → pixel coords
display_df = add_pixel_coords(filtered_df, selected_map)


# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_journey, tab_heatmap, tab_stats = st.tabs([
    "🧭 Player Journeys",
    "🌡️ Heatmaps",
    "📈 Stats",
])


# ── Tab 1: Player Journeys ────────────────────────────────────────────────────
with tab_journey:
    match_id = get_selected_match(display_df)

    if match_id:
        st.markdown("---")
        max_ts = render_timeline(display_df, match_id)

        st.markdown("---")
        render_live_stats(display_df, match_id, max_ts)
        st.markdown("---")

        fig = plot_journeys(
            df=display_df,
            map_name=selected_map,
            minimap_path=minimap_path,
            match_id=match_id,
            max_timestamp=max_ts,
        )

        if show_events:
            fig = add_event_markers(
                fig=fig,
                df=display_df,
                match_id=match_id,
                max_timestamp=max_ts,
                show_events=show_events,
            )

        st.plotly_chart(fig, use_container_width=True)

        with st.expander("📊 Events per minute"):
            render_event_timeline_chart(display_df, match_id)


# ── Tab 2: Heatmaps ───────────────────────────────────────────────────────────
with tab_heatmap:
    st.markdown(
        "Heatmaps aggregate **all filtered matches**. "
        "Use the sidebar to narrow by date or match."
    )

    if not selected_heatmaps:
        st.info("Enable a heatmap overlay in the sidebar under **Heatmap overlays**.")
    else:
        fig_hm = go.Figure()

        if minimap_img:
            fig_hm.add_layout_image(dict(
                source=minimap_img,
                x=0, y=img_h,
                xref="x", yref="y",
                sizex=img_w, sizey=img_h,
                sizing="stretch",
                layer="below",
                opacity=1.0,
            ))

        for hm_type in selected_heatmaps:
            fig_hm = add_heatmap_overlay(
                fig=fig_hm,
                df=display_df,
                heatmap_type=hm_type,
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


# ── Tab 3: Stats ──────────────────────────────────────────────────────────────
with tab_stats:
    st.markdown("### Aggregate stats across all filtered matches")

    events_df = display_df[display_df["event_type"].isin(NON_MOVE_EVENTS)]

    col_a, col_b = st.columns(2)

    with col_a:
        counts = events_df["event_type"].value_counts().reset_index()
        counts.columns = ["Event", "Count"]
        fig_ec = px.bar(
            counts, x="Event", y="Count", color="Event",
            title="Event breakdown",
            color_discrete_map={
                "Kill": "#E63946", "BotKill": "#FF6B6B",
                "Killed": "#2D2D2D", "BotKilled": "#555555",
                "KilledByStorm": "#9B59B6", "Loot": "#FFD700",
            },
            height=320,
        )
        fig_ec.update_layout(showlegend=False,
                             plot_bgcolor="rgba(0,0,0,0)",
                             paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_ec, use_container_width=True)

    with col_b:
        pt = (
            display_df.groupby("is_bot")["event_type"]
            .count().reset_index()
        )
        pt["Type"] = pt["is_bot"].map({True: "Bot", False: "Human"})
        fig_pt = px.pie(
            pt, names="Type", values="event_type",
            title="Human vs Bot event share",
            color="Type",
            color_discrete_map={"Human": "#457B9D", "Bot": "#E9C46A"},
            height=320,
        )
        fig_pt.update_layout(plot_bgcolor="rgba(0,0,0,0)",
                             paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_pt, use_container_width=True)

    st.markdown("#### Top 20 players by kills")
    kills_df = (
        display_df[display_df["event_type"].isin(["Kill", "BotKill"])]
        .groupby(["player_id", "is_bot"])
        .size()
        .reset_index(name="kills")
        .sort_values("kills", ascending=False)
        .head(20)
    )
    kills_df["player_id"] = kills_df["player_id"].astype(str).str[:16]
    kills_df["is_bot"] = kills_df["is_bot"].map({True: "🤖 Bot", False: "👤 Human"})
    kills_df.columns = ["Player ID", "Type", "Kills"]
    st.dataframe(kills_df, use_container_width=True, hide_index=True)
