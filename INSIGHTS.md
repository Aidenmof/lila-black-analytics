# Insights

Three observations from exploring the LILA BLACK telemetry data using the tool.

---

## Insight 1: [Write a short title for what you noticed]

**What caught my eye**
[Describe what you saw — e.g. "Most deaths on AmbroseValley cluster in one area of the map"
Use the Heatmaps tab → Death zones to find this. Look for the brightest spot on the heatmap.]

**Evidence**
[Point to something concrete — e.g. "The death zone heatmap on AmbroseValley shows X% of deaths
concentrated in the [area name] region. In the Stats tab, [X] storm deaths vs [Y] player kills
suggests the storm is/isn't the primary cause."]

**What a level designer should do with this**
[e.g. "The choke point at [location] is generating disproportionate deaths early in matches.
Consider widening the path or adding cover. Metric to watch: death spread across the map
(currently too concentrated). Target: no single zone accounting for more than 30% of deaths."]

---

## Insight 2: [Write a short title for what you noticed]

**What caught my eye**
[e.g. "Bot movement patterns are noticeably different from human players"
Use the Player Journeys tab, filter to Humans only then Bots only, compare path shapes.]

**Evidence**
[Point to something concrete — e.g. "Human player paths on GrandRift tend to hug the edges
of the map, while bot paths (BotPosition events) cut directly through the centre.
In [match ID], [X] of [Y] bots died in the Mine Pit area versus [Z] humans."]

**What a level designer should do with this**
[e.g. "Bot pathfinding is routing them through the highest-risk zone. If bots are dying too fast,
matches feel empty quickly. Adjusting bot nav-mesh weights around [area] could extend bot
survival time and keep matches feeling populated longer. Metric: average bot lifetime per match."]

---

## Insight 3: [Write a short title for what you noticed]

**What caught my eye**
[e.g. "Loot pickup events are heavily concentrated near the storm entry point on Lockdown"
Use the Heatmaps tab → Player traffic, then overlay Kill zones on the same map.]

**Evidence**
[Point to something concrete — e.g. "Traffic heatmap on Lockdown shows a strong corridor
in the [direction] quadrant. Cross-referencing with the kill zone heatmap, this corridor
has the highest kill density — [X] kills per match on average versus [Y] on other routes."]

**What a level designer should do with this**
[e.g. "Players are being funnelled into one route by the storm direction, creating a predictable
high-traffic kill corridor. Adding an alternate extraction path on the west side would reduce
funnelling and create more varied match outcomes. Metrics affected: player survival rate,
match duration variance, loot pickup distribution."]
