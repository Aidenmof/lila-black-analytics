# Insights

Three observations from exploring the LILA BLACK telemetry data using the tool.

---

## Insight 1: Deaths and kills cluster in the same bottom-left corner of AmbroseValley

**What caught my eye**

On the Heatmaps tab with Death zones enabled for AmbroseValley, there is a single concentrated
hotspot in the bottom-left corner of the map. Enabling Kill zones on top of it shows near-perfect
overlap — kills and deaths are happening in almost exactly the same small area.

**Evidence**

The death zone and kill zone heatmaps both peak at the same bottom-left location on AmbroseValley,
while the rest of the map shows almost no activity. In individual match inspection (Player Journeys
tab), this same corner is where loot pickups, bot kills, and player deaths all occur together —
suggesting players are landing, looting, and immediately fighting in a tight cluster rather than
spreading across the map.

**What a level designer should do with this**

The map has a severe engagement funnel. Almost all combat is happening in one corner, which means
the majority of the map is going unplayed. This creates predictable, repetitive matches and wastes
designed content. Actionable items:

- Add high-value loot to underplayed areas to incentivise players to spread out on landing
- Review spawn/drop zone placement — if the default drop point lands near this corner, shifting it
  would force route diversity
- Metrics to watch: death spread across map quadrants (target: no single quadrant above 40% of
  deaths), average distance travelled before first combat event

---

## Insight 2: Loot pickups massively outnumber all combat events combined

**What caught my eye**

In the Stats tab Event breakdown chart, Loot is by far the tallest bar at nearly 10,000 events.
BotKill is a distant second at roughly 2,000. Player vs player Kill and Killed events are nearly
flat — almost invisible on the chart.

**Evidence**

Across all 796 matches and 339 players, Loot events (~10,000) outnumber human Kill events by
roughly 20:1. Storm deaths (KilledByStorm) are also very low. This means players are spending
most of their time looting and relatively little time in direct combat or dying to the storm —
suggesting either the storm pressure is too weak, matches end before the storm becomes relevant,
or players are successfully avoiding combat while looting.

**What a level designer should do with this**

The extraction shooter loop depends on tension between looting and threat. If players can loot
freely without combat pressure, matches feel low-stakes. Actionable items:

- Investigate whether the storm speed or direction needs tuning to create earlier pressure and
  force players into contested areas sooner
- Check whether loot density is too high — abundant loot reduces the need to contest other players
- Metrics to watch: average time from match start to first combat event, ratio of Loot events to
  Kill events per match (current ~20:1, a healthier target might be closer to 5:1)

---

## Insight 3: Human players follow looping paths while bots scatter randomly — but kill rates are similar

**What caught my eye**

Filtering the Player Journeys tab to Humans only shows players moving in curved, looping paths
that follow the roads and structures on AmbroseValley. Switching to Bots only shows short,
scattered movement fragments with no clear routing pattern — bots appear to spawn and move in
small disconnected bursts rather than traversing the map.

**Evidence**

Human paths visually hug the road network and circle back on themselves, suggesting players are
looting buildings along a planned route. Bot paths are fragmented and spread across random points,
showing no road-following behaviour. Despite this movement difference, the Stats tab shows
BotKill and Kill events are comparable in frequency — meaning bots are dying to players at a
similar rate to human-vs-human kills, even though bots move very differently.

**What a level designer should do with this**

Bot movement that ignores road layout and building structure breaks immersion and makes them
trivially predictable targets. If bots die at the same rate as humans but move randomly, they are
not providing meaningful combat challenge — they are just moving loot pinatas. Actionable items:

- Work with the AI team to implement road-following and building-entry behaviour for bots so they
  behave more like human players
- Consider whether bot density is appropriate — 22.3% of all events are bot-generated, so bots
  are a significant presence, and low-quality bot behaviour affects overall match feel
- Metrics to watch: average bot survival time per match, bot path overlap with road network
  (currently near zero, target should mirror human overlap), player-reported match quality scores
