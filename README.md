# ⚔️ Depths of Aethermoor

A text-based **rogue-like RPG** built entirely in Streamlit. Every run is procedurally assembled from a pool of biomes, encounters, monsters, events, and loot — no two descents are quite the same.

> *"The dungeon called Aethermoor was sealed three centuries ago for reasons no living scholar agrees on. Last week the seal cracked."*

---

## Features

- **4 distinct classes** with unique stats, passives, and active skills:
  - **Iron Warden** — tanky, with Shield Bash and Rally.
  - **Shadowblade** — glass cannon, with Backstab and Smoke Bomb.
  - **Arcane Scholar** — fragile but devastating, with Arcane Bolt and Mana Shield.
  - **Dawnkeeper** — balanced healer-fighter, with Smite and Mend.
- **3-act run structure** (Ruined Keep / Goblin Tunnels → branching biome → Ash Wastes → Boss).
- **5 biomes** with their own monster pools and events: Ruined Keep, Goblin Tunnels, Fungal Caverns, Cursed Chapel, Ash Wastes.
- **20 narrative events** with multiple choices, class-conditional outcomes, and lasting flag effects.
- **8 monster types + 3 multi-phase bosses** with intent telegraphing and unique specials (lifesteal, spore cloud, ash armor, etc.).
- **12 weapons** across 4 rarity tiers, with effects like bleed, poison, freeze, double-strike, and HP drain.
- **6 relics** providing permanent run-long bonuses.
- **8 consumables** including scrolls, bombs, potions, and rations.
- **Branching path** at the end of Act 1 — choose your Act 2 biome.
- **Hidden secret nodes** unlocked by carrying a relic shard or the Void Compass.
- **5 endings** including a true ending that requires the forbidden tome + relic shard + low corruption + boss kill.
- **Corruption & Fate** meta-meters that influence outcomes and ending eligibility.
- **Dark GitHub-style UI** with rarity coloring, HP bars, combat log, and biome banners.

---

## Quick Start

```bash
pip install -r requirements.txt
streamlit run app.py
```

Then open the URL Streamlit prints (default: http://localhost:8501).

---

## How to Play

1. From the **title screen**, click *Begin Your Descent*.
2. Choose one of four **classes**. Read their passive and skills carefully — they shape the whole run.
3. Each **node** is one of: combat, elite combat, boss, event, rest, merchant, fork, or secret.
4. In **combat**:
   - **Attack** — basic strike, modified by weapon and passives.
   - **Skills** — class-specific actions (some are once-per-combat).
   - **Item** — use a consumable from your inventory.
   - **Flee** — 50% on normal foes, 30% on elites, never on bosses.
5. Watch the **enemy intent** — it tells you what they're planning next turn.
6. At the **fork**, pick one of two biomes for Act 2. The other path is gone forever.
7. Defeat the **boss** in Act 3 to win. Bosses have a **phase 2** at low HP that enrages them.

---

## The Five Endings

| Ending | How to Get It |
|--------|---------------|
| **The Dungeon Falls** (heroic) | Defeat the boss with corruption ≤ 5 |
| **What Have You Become** (corrupted) | Defeat the boss with corruption ≥ 6 |
| **Narrowly Alive** (survival) | Reach the end without killing the boss |
| **Darkness Claims Another** (death) | HP drops to 0 anywhere |
| **The Secret of Aethermoor** (true) | Defeat boss + own the Forbidden Tome + have a Relic Shard + corruption ≤ 2 |

Tips for the true ending:
- Read (or take) the **Forbidden Tome** in the Ash Wastes.
- Take the **Crystal Shard** at the Crystal Vein, or find a hidden chapel passage.
- Keep **corruption** low — avoid the Dark Altar, Blood Font, robbing merchants, and lying in confession.

---

## Tech

- Python 3.9+
- Streamlit 1.32+
- Pure session-state architecture — no database, no external API.
- Procedural run generation via per-run RNG seed.
- Single-file (`app.py`), ~1100 lines.

---

## File Layout

```
.
├── app.py           # Game logic, content data, and UI
├── requirements.txt # streamlit pin
└── README.md        # This file
```

---

## Credits

Built as a self-contained Streamlit rogue-like demo. All flavor text and content are original. Inspired in spirit by Slay the Spire's act structure, Darkest Dungeon's tone, and every text adventure that ever ate someone's afternoon.

Enjoy the descent. Don't expect to come back the same.