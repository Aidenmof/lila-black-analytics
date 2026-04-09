# LILA BLACK — Player Behavior Explorer

A web-based analytics tool for level designers to explore player behavior across LILA BLACK's
three maps using 5 days of production telemetry data.

**Live tool:** https://lila-black-analytics-psqtcqxyej5b6wzofcxew7.streamlit.app

---

## Tech Stack

| Tool | Purpose |
|------|---------|
| Python + Streamlit | App framework — single-file web app, no separate frontend needed |
| Pandas + PyArrow | Load and process parquet telemetry files |
| Plotly | Interactive map visualisations, heatmaps, charts |
| SciPy (Gaussian KDE) | Smooth density heatmaps from sparse event data |
| Pillow | Load minimap PNG/JPG images as plot backgrounds |
| Streamlit Community Cloud | Free hosting with shareable URL, deploys from GitHub |

---

## Setup — run locally

**1. Clone the repo**
```
git clone https://github.com/Aidenmof/lila-black-analytics
cd lila-black-analytics
```

**2. Install dependencies**
```
pip install -r requirements.txt
```

**3. Add your data**

Place your telemetry files in a `data/` folder with date subfolders:
```
data/
  February_10/
  February_11/
  February_12/
  February_13/
  February_14/
```

**4. Add minimap images**

Place minimap images in `assets/minimaps/`:
```
assets/minimaps/
  AmbroseValley_Minimap.png
  GrandRift_Minimap.png
  Lockdown_Minimap.jpg
```

**5. Run**
```
streamlit run app.py
```

Open http://localhost:8501 in your browser.

> No local data? The deployed version shows a file uploader in the sidebar —
> drag telemetry files directly into the browser.

---

## Environment variables

None required. No API keys or secrets needed.

---

## Feature walkthrough

### Sidebar filters
Use the left sidebar to narrow down what you're looking at:
- **Map** — switch between AmbroseValley, GrandRift, and Lockdown
- **Date range** — filter to specific days (Feb 10–14)
- **Match IDs** — leave blank for all matches, or select one or more specific matches
- **Player type** — show Humans + Bots together, or isolate one group
- **Event markers** — toggle individual event types on/off (kills, deaths, loot, storm)
- **Heatmap overlays** — enable kill zones, death zones, or player traffic overlays

---

### Tab 1 — Player Journeys

Shows individual player movement paths drawn on top of the minimap.

1. Select a match from the dropdown at the top
2. Use the **Playback timeline** slider to scrub through the match — drag left to rewind, right to fast-forward. The map updates in real time showing only events up to that moment.
3. The **live stats bar** below the slider shows kills, bot kills, deaths, storm deaths, and loot at the current timeline position
4. Human players are shown as **solid lines**; bots are shown as **dotted lines**
5. Event markers appear on the map:
   - 🔴 Red X = kill
   - 💀 Dark circle-X = death
   - 💛 Gold diamond = loot pickup
   - 🟣 Purple circle = storm death
6. Expand **Events per minute** at the bottom to see a bar chart of match intensity over time

---

### Tab 2 — Heatmaps

Shows aggregated density overlays across all matches in the current filter.

1. In the sidebar, tick one or more overlays:
   - **Kill zones** (red) — where kills are concentrated
   - **Death zones** (purple) — where players die most
   - **Player traffic** (blue) — where players spend the most time
2. Use the **Heatmap opacity** slider to make the overlay more or less transparent
3. Zoom and pan the map using the Plotly toolbar (top right of the map)
4. Change the map or date range in the sidebar to compare heatmaps across days or maps

---

### Tab 3 — Stats

Shows aggregate statistics across all filtered matches.

- **Event breakdown** bar chart — how many kills, deaths, loot pickups, and storm deaths occurred
- **Human vs Bot event share** pie chart — what proportion of all activity is human-generated vs bot-generated
- **Top 20 players by kills** table — leaderboard of the most lethal players, with human/bot label

---

## Repo structure

```
lila-black-analytics/
├── app.py                  ← Streamlit entry point
├── requirements.txt
├── README.md               ← this file
├── ARCHITECTURE.md         ← system design and coordinate mapping explained
├── INSIGHTS.md             ← three data insights with evidence and recommendations
├── data_loader.py          ← loads .nakama-0 parquet files, decodes event bytes
├── coordinate_mapper.py    ← world (x,z) → minimap pixel conversion
├── filters.py              ← sidebar filter widgets
├── journey_plotter.py      ← player path lines on minimap
├── event_markers.py        ← kill/death/loot/storm markers
├── heatmap.py              ← Gaussian KDE density overlays
├── timeline.py             ← playback scrubber and match stats
└── assets/
    └── minimaps/
        ├── AmbroseValley_Minimap.png
        ├── GrandRift_Minimap.png
        └── Lockdown_Minimap.jpg
```
