import streamlit as st
import random
import copy

st.set_page_config(page_title="Depths of Aethermoor", page_icon="⚔️", layout="wide")

CUSTOM_CSS = """
<style>
.stApp { background-color: #0d1117; color: #c9d1d9; }
body { background-color: #0d1117; color: #c9d1d9; }
.stat-card { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 12px; margin: 4px 0; }
.hp-bar { background: linear-gradient(90deg, #2ea043, #56d364); height: 14px; border-radius: 4px; }
.enemy-hp-bar { background: linear-gradient(90deg, #da3633, #f85149); height: 14px; border-radius: 4px; }
.combat-box { background: #161b22; border: 1px solid #58a6ff; border-radius: 6px; padding: 12px; margin: 8px 0; }
.event-box { background: #161b22; border: 1px solid #8b949e; border-radius: 6px; padding: 16px; margin: 8px 0; line-height: 1.55; }
.log-entry { font-size: 0.85em; color: #8b949e; font-style: italic; }
.rarity-common { color: #8b949e; }
.rarity-uncommon { color: #4eca8b; }
.rarity-rare { color: #a855f7; font-weight: bold; }
.rarity-cursed { color: #ef4444; font-style: italic; }
.boss-title { font-size: 1.4em; color: #ef4444; font-weight: bold; }
.ending-box { background: #161b22; border: 2px solid #ffd700; border-radius: 12px; padding: 24px; text-align: center; margin: 16px auto; max-width: 720px; }
.biome-tag { display: inline-block; padding: 4px 10px; border-radius: 12px; background: #21262d; color: #c9d1d9; font-size: 0.85em; border: 1px solid #30363d; }
.intent-tag { display: inline-block; padding: 3px 8px; border-radius: 4px; background: #2d1b1b; color: #f85149; font-size: 0.85em; border: 1px solid #58181f; }
.act-banner { padding: 8px 16px; background: linear-gradient(90deg, #1f6feb22, #161b22); border-left: 3px solid #58a6ff; border-radius: 4px; margin-bottom: 12px; }
.pending-weapon { background: #2d2a14; border: 1px solid #d29922; border-radius: 6px; padding: 10px; margin: 8px 0; }
h1, h2, h3, h4 { color: #f0f6fc; }
hr { border-color: #30363d; }
</style>
"""

# =====================================================================
# CONTENT DATA
# =====================================================================

CLASSES = {
    "iron_warden": {
        "name": "Iron Warden",
        "emoji": "🛡️",
        "flavor": "A scarred veteran who has seen too many dungeons and not enough sunlight.",
        "hp": 35, "max_hp": 35, "attack": 7, "defense": 4, "gold": 15,
        "weapon": "Battered Longsword",
        "passive": "Bulwark — gain +2 defense when below 50% HP",
        "passive_key": "bulwark",
        "skills": [
            {"name": "Shield Bash", "desc": "Stuns enemy for 1 turn. No cost.", "key": "shield_bash", "cost": 0},
            {"name": "Rally", "desc": "Heal 6 HP. Once per combat.", "key": "rally", "cost": 0}
        ]
    },
    "shadowblade": {
        "name": "Shadowblade",
        "emoji": "🗡️",
        "flavor": "Moves through shadows. Charges triple for the privilege.",
        "hp": 26, "max_hp": 26, "attack": 9, "defense": 2, "gold": 20,
        "weapon": "Rusty Dagger",
        "passive": "Opportunist — 30% chance to double damage on first attack",
        "passive_key": "opportunist",
        "skills": [
            {"name": "Backstab", "desc": "Guaranteed critical hit (damage x2). Costs 3 HP.", "key": "backstab", "cost": 3},
            {"name": "Smoke Bomb", "desc": "Flee always succeeds this turn. No cost.", "key": "smoke_bomb", "cost": 0}
        ]
    },
    "arcane_scholar": {
        "name": "Arcane Scholar",
        "emoji": "🔮",
        "flavor": "Knows seventeen words for 'fireball' and uses them all.",
        "hp": 22, "max_hp": 22, "attack": 5, "defense": 1, "gold": 25,
        "weapon": "Gnarled Staff",
        "passive": "Spellweave — scrolls deal +50% damage",
        "passive_key": "spellweave",
        "skills": [
            {"name": "Arcane Bolt", "desc": "8 magic damage, ignores defense. No cost.", "key": "arcane_bolt", "cost": 0},
            {"name": "Mana Shield", "desc": "Absorb next hit completely. Once per combat.", "key": "mana_shield", "cost": 0}
        ]
    },
    "dawnkeeper": {
        "name": "Dawnkeeper",
        "emoji": "✨",
        "flavor": "Priest, healer, last resort. Also surprisingly good at hitting things.",
        "hp": 30, "max_hp": 30, "attack": 6, "defense": 3, "gold": 18,
        "weapon": "Holy Mace",
        "passive": "Sacred Ground — shrines grant double benefit",
        "passive_key": "sacred_ground",
        "skills": [
            {"name": "Smite", "desc": "Deal attack+4 damage (+6 vs undead). No cost.", "key": "smite", "cost": 0},
            {"name": "Mend", "desc": "Heal 10 HP. Once per combat.", "key": "mend", "cost": 0}
        ]
    }
}

WEAPONS = [
    {"name": "Battered Longsword", "damage_bonus": 0, "rarity": "common", "special": None, "description": "A reliable, unremarkable blade."},
    {"name": "Rusty Dagger", "damage_bonus": 0, "rarity": "common", "special": None, "description": "Light and quick. Mostly rust."},
    {"name": "Gnarled Staff", "damage_bonus": 0, "rarity": "common", "special": None, "description": "Channels arcane focus."},
    {"name": "Holy Mace", "damage_bonus": 0, "rarity": "common", "special": "holy", "description": "Bonus damage to undead."},
    {"name": "Iron Hammer", "damage_bonus": 2, "rarity": "uncommon", "special": None, "description": "Heavy. Hits hard."},
    {"name": "Serrated Saber", "damage_bonus": 1, "rarity": "uncommon", "special": "bleed", "description": "Causes bleeding wounds."},
    {"name": "Witchwood Bow", "damage_bonus": 2, "rarity": "uncommon", "special": None, "description": "Carved from a haunted grove."},
    {"name": "Venom Fang", "damage_bonus": 1, "rarity": "uncommon", "special": "poison", "description": "Drips with toxin."},
    {"name": "Dawnsteel Blade", "damage_bonus": 3, "rarity": "rare", "special": "holy", "description": "Forged where the sun first touched stone."},
    {"name": "Frostbrand", "damage_bonus": 3, "rarity": "rare", "special": "freeze", "description": "Cold burns colder."},
    {"name": "Stormcaller Spear", "damage_bonus": 4, "rarity": "rare", "special": "double_strike", "description": "Hums with thunder. Strikes twice sometimes."},
    {"name": "Voidtouched Edge", "damage_bonus": 5, "rarity": "cursed", "special": "drain", "description": "Power costs blood. Drains 2 HP per swing."},
]

MONSTERS = [
    {"name": "Goblin Scrapper", "hp": 14, "attack": 4, "defense": 0, "xp": 8, "special": None,
     "intent_pool": ["lunges with a jagged knife", "throws a rock", "snarls and bites"],
     "description": "Small, mean, and surprisingly persistent."},
    {"name": "Skeleton Archer", "hp": 12, "attack": 5, "defense": 1, "xp": 10, "special": None,
     "intent_pool": ["nocks a brittle arrow", "draws back the bowstring", "fires from a shadow"],
     "description": "Bones held together by spite."},
    {"name": "Cave Spider", "hp": 16, "attack": 4, "defense": 1, "xp": 12, "special": "web",
     "intent_pool": ["skitters forward fangs bared", "spits webbing", "lunges from the ceiling"],
     "description": "Eight legs, no soul."},
    {"name": "Cultist Acolyte", "hp": 18, "attack": 5, "defense": 1, "xp": 14, "special": "sacrifice",
     "intent_pool": ["chants a foul prayer", "slashes with a ritual dagger", "calls dark power"],
     "description": "Robed devotees of something best forgotten."},
    {"name": "Fungal Stalker", "hp": 22, "attack": 5, "defense": 2, "xp": 16, "special": "spore_cloud",
     "intent_pool": ["releases spores", "swings rooty limbs", "shambles closer"],
     "description": "A man-shape made of mold and grudge."},
    {"name": "Hollow Knight", "hp": 28, "attack": 7, "defense": 3, "xp": 22, "special": "shield_block",
     "intent_pool": ["raises shield and advances", "swings a heavy greatsword", "stomps the earth"],
     "description": "An empty suit of armor that refuses to fall."},
    {"name": "Ash Wraith", "hp": 20, "attack": 8, "defense": 0, "xp": 24, "special": "burn",
     "intent_pool": ["flares with ember", "drifts forward burning", "exhales ash"],
     "description": "Smoke given hatred."},
    {"name": "Blood Reaver", "hp": 26, "attack": 7, "defense": 2, "xp": 26, "special": "lifesteal",
     "intent_pool": ["sweeps a crimson axe", "drinks deep from the wound", "laughs wetly"],
     "description": "Took too much. Wants more."},
]

BOSSES = [
    {"name": "The Hollow King", "hp": 60, "attack": 9, "defense": 3, "xp": 60, "special": "shield_block",
     "phase2_trigger": 30, "phase2_attack_bonus": 4,
     "intent_pool": ["crashes down with a rusted greatsword", "summons grave-cold", "shield-charges across the floor", "raises hollow soldiers"],
     "description": "He used to be a king. Now he is mostly a vessel.",
     "intro_text": "The throne room at the end of the dungeon holds something that might once have been royal. The armour is ornate, ceremonial, built for a body that no longer has opinions about its contents. The Hollow King turns to face you. The eyes behind the visor are two points of cold light. It raises its sword not in greeting but in recognition — the way a lock recognises a key. <br><br><i>It has been waiting. Not patiently. Just waiting.</i>"},
    {"name": "Mother of Spores", "hp": 70, "attack": 7, "defense": 2, "xp": 65, "special": "spore_cloud",
     "phase2_trigger": 35, "phase2_attack_bonus": 3,
     "intent_pool": ["releases a vast spore cloud", "lashes with mycelial whips", "births a stalker-spawn", "gurgles a fungal hymn"],
     "description": "The dungeon is her body. The dungeon is hungry.",
     "intro_text": "The cavern ends in a chamber so large the ceiling is just darkness. And in the centre of the darkness, something massive breathes. You have been walking through her body this entire time. The fungal creepers, the spores, the soft floor — all of it was her. She opens what might be eyes. They are not arranged in a way that suggests individual thought. <br><br><i>The dungeon is hungry. The dungeon has found you.</i>"},
    {"name": "Ashen Lich", "hp": 55, "attack": 10, "defense": 1, "xp": 70, "special": "ash_armor",
     "phase2_trigger": 27, "phase2_attack_bonus": 5,
     "intent_pool": ["hurls a bolt of ash and fire", "draws sigils in burning air", "raises a wall of cinders", "whispers your true name"],
     "description": "A scholar who refused to die. Now neither living nor scholarly.",
     "intro_text": "There is a figure in the ash sitting in what was a chair, at what was a desk, studying what was a book. It looks up when you enter. The face is ancient, desiccated, and completely calm — the calm of someone who has solved the problem of mortality and is mildly annoyed that it keeps sending visitors. <br><br>*'You are not the first,'* it says. The ash around it begins to swirl. *'But you may be the last.'*"},
]

RELICS = [
    {"name": "Bloodstone Ring", "rarity": "uncommon", "effect": "vamp_kill", "description": "Restore 3 HP on every kill."},
    {"name": "Merchant's Token", "rarity": "uncommon", "effect": "gold_boost", "description": "Gain 50% more gold from kills."},
    {"name": "Tome of Suffering", "rarity": "rare", "effect": "tome_suffering", "description": "Every 3rd turn in combat: bonus 10 damage to enemy."},
    {"name": "Featherweight Boots", "rarity": "uncommon", "effect": "flee_always", "description": "Flee attempts always succeed."},
    {"name": "Void Compass", "rarity": "rare", "effect": "reveal_hidden", "description": "Hidden passages are always revealed."},
    {"name": "Idol of the Broken God", "rarity": "rare", "effect": "idol_broken", "description": "+3 attack, -5 max HP. Permanent."},
]

CONSUMABLES = [
    {"name": "Health Potion", "effect": "heal", "value": 12, "description": "Restores 12 HP."},
    {"name": "Greater Potion", "effect": "heal", "value": 25, "description": "Restores 25 HP."},
    {"name": "Antidote", "effect": "cure_poison", "value": 0, "description": "Cures poison."},
    {"name": "Smoke Bomb", "effect": "flee", "value": 0, "description": "Guarantees escape from combat."},
    {"name": "Bomb", "effect": "bomb", "value": 14, "description": "Deals 14 damage to enemy."},
    {"name": "Scroll of Flame", "effect": "scroll_flame", "value": 16, "description": "Burns enemy for 16 damage (more with Spellweave)."},
    {"name": "Scroll of Frost", "effect": "scroll_frost", "value": 0, "description": "Freezes enemy for 1 turn."},
    {"name": "Iron Ration", "effect": "ration", "value": 8, "description": "Restores 8 HP and clears fatigue."},
]

BIOMES = {
    "ruined_keep": {
        "name": "The Ruined Keep",
        "emoji": "🏰",
        "description": "Collapsed halls, mossy banners, the smell of old iron.",
        "monsters": ["Goblin Scrapper", "Skeleton Archer", "Hollow Knight"],
        "events": ["cracked_chest", "old_shrine", "collapsed_wall", "goblin_stash"]
    },
    "goblin_tunnels": {
        "name": "The Goblin Tunnels",
        "emoji": "🕯️",
        "description": "Cramped, smoke-filled, lit by sputtering tallow.",
        "monsters": ["Goblin Scrapper", "Cave Spider", "Skeleton Archer"],
        "events": ["goblin_stash", "rigged_trap", "spider_nest", "cracked_chest"]
    },
    "fungal_caverns": {
        "name": "The Fungal Caverns",
        "emoji": "🍄",
        "description": "Glowing fungi pulse in slow rhythm. The walls breathe.",
        "monsters": ["Fungal Stalker", "Cave Spider", "Cultist Acolyte"],
        "events": ["glowing_mushroom", "spore_pool", "fungal_effigy", "mushroom_merchant"]
    },
    "cursed_chapel": {
        "name": "The Cursed Chapel",
        "emoji": "⛪",
        "description": "Stained glass over things that should not be worshipped.",
        "monsters": ["Cultist Acolyte", "Skeleton Archer", "Hollow Knight"],
        "events": ["dark_altar", "holy_shrine", "blood_font", "confession_booth", "hidden_door"]
    },
    "ash_wastes": {
        "name": "The Ash Wastes",
        "emoji": "🌋",
        "description": "Where the world ended once already. Nothing has grown back.",
        "monsters": ["Ash Wraith", "Blood Reaver", "Hollow Knight"],
        "events": ["ember_cache", "wandering_merchant", "forbidden_tome", "crystal_vein"]
    }
}

EVENTS = {
    "cracked_chest": {
        "title": "A Cracked Chest",
        "text": "A wooden chest sits in the corner, lock already broken. The hinges look... eager.",
        "choices": [
            {"text": "Open it carefully", "outcome_key": "loot_or_trap"},
            {"text": "Leave it alone", "outcome_key": "nothing"},
        ]
    },
    "old_shrine": {
        "title": "An Old Shrine",
        "text": "A weathered shrine to a forgotten saint. The eyes of the statue have been chiseled out.",
        "choices": [
            {"text": "Pray respectfully", "outcome_key": "pray_shrine"},
            {"text": "Pocket the offerings", "outcome_key": "desecrate_shrine"},
        ]
    },
    "collapsed_wall": {
        "title": "Collapsed Wall",
        "text": "A wall has fallen open, revealing a tighter passage forward. The masonry shifts slightly when you breathe.",
        "choices": [
            {"text": "Squeeze through (3 damage)", "outcome_key": "shortcut"},
            {"text": "Take the long way", "outcome_key": "nothing"},
        ]
    },
    "goblin_stash": {
        "title": "Goblin Stash",
        "text": "Behind a loose stone: a sack of coin and a few teeth. Someone's been hoarding.",
        "choices": [
            {"text": "Take everything", "outcome_key": "loot_goblin_stash"},
            {"text": "Leave it (respect)", "outcome_key": "nothing"},
        ]
    },
    "rigged_trap": {
        "title": "A Rigged Trap",
        "text": "A tripwire, a row of darts, and what looks like... is that a bear-trap glued to a brick?",
        "choices": [
            {"text": "Attempt to disarm", "outcome_key": "disarm_trap"},
            {"text": "Trigger it deliberately to clear the path", "outcome_key": "trigger_trap"},
        ]
    },
    "spider_nest": {
        "title": "Spider Nest",
        "text": "Eggs the size of fists hang in heavy webs. Something many-legged watches from the shadows.",
        "choices": [
            {"text": "Burn the nest (loot, 5 damage)", "outcome_key": "burn_nest"},
            {"text": "Sneak past", "outcome_key": "sneak_nest"},
        ]
    },
    "glowing_mushroom": {
        "title": "A Glowing Mushroom",
        "text": "Tall, pulsing, blue-green. It hums when you approach.",
        "choices": [
            {"text": "Eat it", "outcome_key": "eat_mushroom"},
            {"text": "Pocket a piece", "outcome_key": "pocket_mushroom"},
        ]
    },
    "spore_pool": {
        "title": "Spore Pool",
        "text": "A milky pool, surface stirring like it's almost breathing. Steam rises in faint sigils.",
        "choices": [
            {"text": "Bathe in the pool", "outcome_key": "bathe_pool"},
            {"text": "Move along", "outcome_key": "nothing"},
        ]
    },
    "fungal_effigy": {
        "title": "Fungal Effigy",
        "text": "A figure has been built out of stacked mushrooms. It has hands. They are pointed at you.",
        "choices": [
            {"text": "Destroy the effigy", "outcome_key": "destroy_effigy"},
            {"text": "Bow to it (worship)", "outcome_key": "worship_effigy"},
        ]
    },
    "mushroom_merchant": {
        "title": "Mushroom Merchant",
        "text": "A figure made mostly of mushroom-cap and patience. It opens a satchel that should not fit inside its sleeve.",
        "choices": [
            {"text": "Trade with it", "outcome_key": "open_merchant"},
            {"text": "Rob it", "outcome_key": "rob_merchant"},
            {"text": "Move on", "outcome_key": "nothing"},
        ]
    },
    "dark_altar": {
        "title": "Dark Altar",
        "text": "Black stone, deep grooves channeling toward a basin. The smell is old and copper.",
        "choices": [
            {"text": "Offer your blood (6 HP, +corruption, relic)", "outcome_key": "offer_blood"},
            {"text": "Smash the altar", "outcome_key": "smash_altar"},
            {"text": "Pray over it (cleric only)", "outcome_key": "cleric_altar_relic"},
        ]
    },
    "holy_shrine": {
        "title": "Holy Shrine",
        "text": "Sunlight finds this place through a hole in the ceiling. The statue still smiles.",
        "choices": [
            {"text": "Pray", "outcome_key": "holy_shrine_pray"},
            {"text": "Donate 10 gold", "outcome_key": "donate_shrine"},
        ]
    },
    "blood_font": {
        "title": "Blood Font",
        "text": "A baptismal font filled with something dark. It is warm. It is moving.",
        "choices": [
            {"text": "Drink (heal, +corruption)", "outcome_key": "drink_font"},
            {"text": "Bless it (cleric only)", "outcome_key": "bless_font"},
        ]
    },
    "confession_booth": {
        "title": "Confession Booth",
        "text": "An old wooden booth. The grill is intact. From the other side, something exhales softly.",
        "choices": [
            {"text": "Confess honestly", "outcome_key": "confess"},
            {"text": "Lie beautifully (+gold, +corruption)", "outcome_key": "lie_confess"},
        ]
    },
    "hidden_door": {
        "title": "Hidden Door",
        "text": "A door behind the tapestry. It has no handle. The keyhole is shaped like nothing.",
        "choices": [
            {"text": "Try to enter", "outcome_key": "enter_hidden"},
            {"text": "Leave it sealed", "outcome_key": "nothing"},
        ]
    },
    "ember_cache": {
        "title": "Ember Cache",
        "text": "Something glints under the ash. Could be coin. Could be a buried fire still hungry.",
        "choices": [
            {"text": "Dig it out", "outcome_key": "dig_cache"},
            {"text": "Mark the location and move on", "outcome_key": "mark_cache"},
        ]
    },
    "wandering_merchant": {
        "title": "Wandering Merchant",
        "text": "A figure pulling a cart across the wastes. Their face is wrapped. Their wares are not.",
        "choices": [
            {"text": "Trade goods", "outcome_key": "barter_trade"},
            {"text": "Shop normally", "outcome_key": "open_merchant"},
            {"text": "Walk past", "outcome_key": "nothing"},
        ]
    },
    "forbidden_tome": {
        "title": "Forbidden Tome",
        "text": "A book bound in something that was once a person. The pages turn themselves a little when no one looks.",
        "choices": [
            {"text": "Read it", "outcome_key": "read_tome"},
            {"text": "Burn it", "outcome_key": "burn_tome"},
            {"text": "Take it (study later)", "outcome_key": "take_tome"},
        ]
    },
    "crystal_vein": {
        "title": "Crystal Vein",
        "text": "A seam of dark crystal in the ash wall. It sings, faintly, at a pitch only your teeth can hear.",
        "choices": [
            {"text": "Mine for gold", "outcome_key": "mine_crystals"},
            {"text": "Pry a large shard free", "outcome_key": "take_crystal"},
        ]
    },
}

SHOP_CATALOG = [
    {"name": "Health Potion", "price": 8, "type": "consumable"},
    {"name": "Greater Potion", "price": 15, "type": "consumable"},
    {"name": "Antidote", "price": 5, "type": "consumable"},
    {"name": "Bomb", "price": 10, "type": "consumable"},
    {"name": "Scroll of Flame", "price": 12, "type": "consumable"},
    {"name": "Iron Ration", "price": 6, "type": "consumable"},
    {"name": "Smoke Bomb", "price": 14, "type": "consumable"},
    {"name": "Scroll of Frost", "price": 10, "type": "consumable"},
]

# =====================================================================
# NARRATIVE — all story/transition/approach text
# =====================================================================

# Opening monologue per class — shown on the very first node
CLASS_OPENINGS = {
    "iron_warden": (
        "You have done this before. Different dungeon, same smell — damp stone, old blood, "
        "the faint metallic tang of something that hasn't been aired out since before you were born. "
        "You check your sword. You check your shield. You go in anyway. "
        "**Some people call it bravery. You call it a lack of better options.**"
    ),
    "shadowblade": (
        "The job was supposed to be simple: retrieve something from inside and bring it out. "
        "The client didn't mention the seal, or the things that broke it, or the way the entrance "
        "breathes like a sleeping animal. You note the exits. You note the shadows. "
        "**You are already calculating how much of this you can cut corners on.**"
    ),
    "arcane_scholar": (
        "Your notes from the university describe Aethermoor as a 'transitional locus of residual thaumic energy.' "
        "Your notes from the university were written by people who had never been inside. "
        "You can feel the magic already — old magic, the kind that doesn't care about your credentials. "
        "**You open your notebook. Then you close it. Some things you just have to walk into.**"
    ),
    "dawnkeeper": (
        "The Dawn Temple sent you here with a blessing and a vague mandate: 'cleanse what can be cleansed, "
        "contain what cannot.' Standard language. You've learned that 'what cannot' tends to be most of it. "
        "Your mace is warm in your hand. The light at the entrance flickers. "
        "**You make the sign of the Dawn. The dungeon, notably, does not respond in kind.**"
    ),
}

# Act transition text — shown once when moving into each act
ACT_TRANSITIONS = {
    1: None,  # Act 1 uses the class opening instead
    2: {
        "ruined_keep":   "The upper halls fall behind you. Deeper in, the architecture changes — older, stranger, built for things that didn't need doors at the same heights you do.",
        "fungal_caverns":"The stone gives way to something softer. The walls breathe here, faintly, in and out with a rhythm that doesn't match any wind you can account for.",
        "cursed_chapel": "The iconography shifts. Saints' faces have been chiselled away and replaced with other faces. You don't recognize them. You suspect that's intentional.",
        "ash_wastes":    "The air tastes of old fires. Whatever burned here burned completely — walls, floor, the very idea of this place — and what's left is the skeleton of something that used to be enormous.",
        "goblin_tunnels":"The passages narrow. Someone has scratched tallies into the walls. You count them. You stop counting them. There are too many to count.",
    },
    3: "Something changes. The dungeon knows you've come this far. The air pressure shifts. The sounds stop. It's waiting.",
}

# Biome approach lines — shown at the start of each node as a brief 'you arrive' sentence
BIOME_APPROACH = {
    "ruined_keep": [
        "Flagstones give way underfoot. Something scurries behind a collapsed archway.",
        "A draft carries the smell of iron and old leather through the passage.",
        "The ceiling here is intact, which is the best thing you can say about it.",
        "You move through a hall where the tapestries have rotted to silhouettes.",
        "Moonlight — impossible at this depth — pools in a crack in the ceiling.",
        "The corridor opens into something that was once a barracks. Once.",
    ],
    "fungal_caverns": [
        "Bioluminescent caps dot the walls in clusters. They pulse when you pass.",
        "Your boots sink slightly with each step. The floor is not stone here.",
        "The air is thick enough to taste. You taste it anyway. You regret this.",
        "Mycelium threads hang like curtains between the stalagmites.",
        "Something in the dark releases a faint, sweet spore. You hold your breath.",
        "The cavern opens into a chamber that glows a faint, sick green.",
    ],
    "cursed_chapel": [
        "A row of pews faces an altar that faces the wrong direction.",
        "Candles burn here, which would be comforting if they cast any shadows.",
        "The floor is inscribed with a prayer in a language you don't recognize.",
        "Glass from shattered windows crunches underfoot. The frames hold only dark.",
        "A confessional booth stands in the corner, door slightly ajar.",
        "The hymn you can almost hear is not one you know from the hymnal.",
    ],
    "ash_wastes": [
        "The heat hasn't entirely left. It radiates from the walls like a grudge.",
        "Ash drifts in from somewhere. There is no wind. There is no reason for the ash.",
        "The ruins here suggest something large once stood. It was not made to fall.",
        "Your footprints in the cinders are the first in a very long time.",
        "Scorched stone and the outlines of things that melted. You move quickly.",
        "The sky, where visible through the ceiling holes, is the wrong shade of red.",
    ],
    "goblin_tunnels": [
        "The tunnels branch and re-branch. Someone mapped this once. They are gone.",
        "Crude totems of bone and wire hang from the ceiling at head height.",
        "The smell of cooked meat from somewhere. You hope it's meat.",
        "Claw marks along the left wall. Someone left in a hurry. Going right.",
        "A tripwire at ankle height. You step over it. You wonder how many others didn't.",
        "The passage widens into a crude common room. No one is home. Probably.",
    ],
}

# Node-type preamble — what you see/hear as you arrive at each type of encounter
NODE_PREAMBLE = {
    "combat": {
        "ruined_keep":   ["Something moves in the far corner. Then it stops trying to be subtle.",
                          "The sound of metal. Then the sound of something wanting blood."],
        "fungal_caverns":["A shape detaches from the wall — you thought it was part of the cave.",
                          "The spores shift and something steps through them toward you."],
        "cursed_chapel": ["A figure at the altar turns. It was not praying.",
                          "Movement behind the pews. It resolves itself into something hostile."],
        "ash_wastes":    ["A silhouette in the haze takes on weight and purpose.",
                          "You hear it before you see it. Then you see it."],
        "goblin_tunnels":["High-pitched screaming from ahead. The enthusiastic kind.",
                          "They were waiting. Not patiently, but effectively."],
    },
    "elite_combat": {
        "ruined_keep":   "Something bigger than the others. The others were not small.",
        "fungal_caverns":"The largest thing in the cavern has noticed you first.",
        "cursed_chapel": "An elite among the damned. The corruption here runs deeper.",
        "ash_wastes":    "This one has survived everything the wastes could throw at it. Now it's throwing you.",
        "goblin_tunnels":"A champion, by goblin standards. Those standards involve a lot of corpses.",
    },
    "boss": {
        "default": "The chamber at the end. The thing at the centre. You knew it was here. Here it is.",
    },
    "event": {
        "ruined_keep":   "You pause. Something in the room is worth your attention — or wants it.",
        "fungal_caverns":"The cavern offers you something. Most things the cavern offers are tricks. Not all.",
        "cursed_chapel": "The chapel presses something on you. A choice, dressed up as chance.",
        "ash_wastes":    "A moment's pause in the grey. An opportunity or a trap. Possibly both.",
        "goblin_tunnels":"Something the goblins left behind, or left as bait, or didn't think was bait.",
    },
    "rest": {
        "default": "A moment's breath. The dungeon continues on either side, but here, briefly, nothing is trying to kill you.",
    },
    "merchant": {
        "default": "Someone is selling things down here. You've stopped asking why.",
    },
    "treasure": {
        "default": "Something valuable, unattended. Which means either luck or a trap. Possibly you've earned some luck.",
    },
    "secret": {
        "default": "A passage no one else found. Or no one else survived to use.",
    },
    "fork": {
        "default": "The path splits. Both ways look wrong in different directions. You choose.",
    },
}

# Post-result connector text — shown on the "Continue →" beat after a combat/event resolves
# Pulled by the next node's type to bridge the gap
POST_COMBAT_WIN = [
    "The body settles. You catch your breath. The dungeon continues, indifferent.",
    "You wipe your blade. The silence after a fight is its own kind of noise.",
    "Done. For now. Further in, something didn't hear this and isn't slowing down.",
    "Victory, technically. You move before the adrenaline has time to reconsider.",
    "The enemy is down. The dungeon is not impressed. Neither are you, really. Onward.",
]
POST_COMBAT_FLEE = [
    "You put distance between yourself and the problem. The problem remembers.",
    "Running feels cowardly. Dying would have felt worse. You keep running.",
    "The corridor swallows you. The sound of pursuit fades, then stops. Probably stops.",
    "Not a win. Not a loss. A postponement. The dungeon doesn't forget.",
]
POST_EVENT = [
    "The room releases you. You step forward into whatever comes next.",
    "Choice made. Consequence pending. The dungeon doesn't bill immediately.",
    "You file it away — what you did here, what it cost — and keep moving.",
]

# =====================================================================
# STATE
# =====================================================================

def init_state():
    st.session_state["gs"] = {
        "screen": "title",
        "player": None,
        "run_seed": None,
        "rng": None,
        "run_nodes": [],
        "current_node_idx": 0,
        "current_node": None,
        "combat_state": None,
        "shop_items": None,
        "log": [],
        "flags": {
            "corruption": 0,
            "fate": 0,
            "chapel_key": False,
            "has_tome": False,
            "found_cache": False,
            "relic_shard": False,
            "robbed_merchant": False,
            "altar_visited": False,
            "void_compass_used": False,
            "boss_defeated": False,
            "combat_count": 0,
        },
        "run_complete": False,
        "ending_key": None,
        "fork_choices": None,
        "pending_loot": None,
        "act": 1,
        "prev_act": 1,
        "show_act_transition": False,
        "show_class_opening": True,
        "node_intro_dismissed": False,
        "post_result_text": None,
        "event_resolved": False,
        "rest_used": False,
        "rest_searched": False,
        "secret_taken": False,
    }

# =====================================================================
# HELPERS
# =====================================================================

def add_log(gs, msg):
    gs["log"].insert(0, msg)
    if len(gs["log"]) > 8:
        gs["log"] = gs["log"][:8]

def get_node_approach(gs, node):
    """Return a 1–2 sentence atmospheric approach line for the current node."""
    ntype = node.get("type", "combat")
    biome = node.get("biome") or "ruined_keep"
    rng = gs["rng"]
    if ntype in ("combat", "elite_combat"):
        key = "elite_combat" if ntype == "elite_combat" else "combat"
        pool = NODE_PREAMBLE.get(key, {})
        lines = pool.get(biome, pool.get("ruined_keep", ["Something waits ahead."]))
        if isinstance(lines, list):
            # use node index as stable offset so it doesn't re-roll on rerun
            idx = gs["current_node_idx"] % len(lines)
            return lines[idx]
        return lines
    elif ntype == "boss":
        return NODE_PREAMBLE["boss"]["default"]
    elif ntype in ("event", "merchant", "rest", "treasure", "secret", "fork"):
        pool = NODE_PREAMBLE.get(ntype, {})
        if isinstance(pool, dict):
            line = pool.get(biome, pool.get("default", ""))
            if not line:
                line = pool.get("default", "")
            return line
        return pool
    return ""

def get_biome_flavour(gs, biome_key):
    """Return a rotating atmospheric one-liner for the current biome."""
    pool = BIOME_APPROACH.get(biome_key, ["The dungeon stretches on."])
    idx = gs["current_node_idx"] % len(pool)
    return pool[idx]

def get_post_result_text(gs, result_type):
    """Return a connector sentence for the Continue beat."""
    rng = gs["rng"]
    if result_type == "combat_win":
        idx = gs["current_node_idx"] % len(POST_COMBAT_WIN)
        return POST_COMBAT_WIN[idx]
    elif result_type == "combat_flee":
        idx = gs["current_node_idx"] % len(POST_COMBAT_FLEE)
        return POST_COMBAT_FLEE[idx]
    else:
        idx = gs["current_node_idx"] % len(POST_EVENT)
        return POST_EVENT[idx]

def get_weapon(name):
    for w in WEAPONS:
        if w["name"] == name:
            return w
    return WEAPONS[0]

def get_monster(name):
    for m in MONSTERS:
        if m["name"] == name:
            return m
    return MONSTERS[0]

def get_relic(name):
    for r in RELICS:
        if r["name"] == name:
            return r
    return None

def has_relic(gs, effect_key):
    if not gs.get("player"):
        return False
    for rname in gs["player"].get("relics", []):
        r = get_relic(rname)
        if r and r["effect"] == effect_key:
            return True
    return False

def add_to_inventory(gs, item):
    if len(gs["player"]["inventory"]) < 6:
        gs["player"]["inventory"].append(copy.copy(item))
        return True
    return False

def rarity_class(rarity):
    return {
        "common": "rarity-common",
        "uncommon": "rarity-uncommon",
        "rare": "rarity-rare",
        "cursed": "rarity-cursed",
    }.get(rarity, "rarity-common")

# =====================================================================
# LOOT & GENERATION
# =====================================================================

def roll_loot(rng, quality="normal"):
    gold_ranges = {"poor": (1, 6), "normal": (2, 12), "good": (3, 18), "elite": (4, 24)}
    item_chances = {"poor": 0.2, "normal": 0.4, "good": 0.6, "elite": 0.7}
    weapon_chances = {"poor": 0.0, "normal": 0.1, "good": 0.25, "elite": 0.45}
    lo, hi = gold_ranges.get(quality, (2, 12))
    gold = rng.randint(lo, hi)
    item = None
    weapon = None
    if rng.random() < item_chances.get(quality, 0.4):
        pool = [c for c in CONSUMABLES]
        item = copy.copy(rng.choice(pool))
    if rng.random() < weapon_chances.get(quality, 0.1):
        if quality == "elite":
            pool = [w for w in WEAPONS if w["rarity"] in ("uncommon", "rare")]
        else:
            pool = [w for w in WEAPONS if w["rarity"] == "uncommon"]
        if pool:
            weapon = rng.choice(pool)
    return {"gold": gold, "item": item, "weapon": weapon}

def generate_run(rng, player_class_key):
    nodes = []
    act1_biome = rng.choice(["ruined_keep", "goblin_tunnels"])
    b1 = BIOMES[act1_biome]
    monsters1 = rng.sample(b1["monsters"], min(2, len(b1["monsters"])))
    events1 = rng.sample(b1["events"], min(2, len(b1["events"])))
    nodes.append({"type": "combat", "biome": act1_biome, "monster": monsters1[0], "act": 1, "loot": "normal", "is_elite": False, "is_boss": False})
    nodes.append({"type": "event", "biome": act1_biome, "event_key": events1[0], "act": 1, "loot": "normal", "is_elite": False, "is_boss": False})
    nodes.append({"type": "combat", "biome": act1_biome, "monster": monsters1[-1], "act": 1, "loot": "normal", "is_elite": False, "is_boss": False})
    nodes.append({"type": "rest", "biome": act1_biome, "act": 1, "loot": "poor", "is_elite": False, "is_boss": False})
    elite1 = rng.choice(b1["monsters"])
    nodes.append({"type": "elite_combat", "biome": act1_biome, "monster": elite1, "act": 1, "loot": "good", "is_elite": True, "is_boss": False})
    if len(events1) > 1:
        nodes.append({"type": "event", "biome": act1_biome, "event_key": events1[1], "act": 1, "loot": "normal", "is_elite": False, "is_boss": False})
    act2_options = rng.sample(["fungal_caverns", "cursed_chapel", "ash_wastes"], 2)
    nodes.append({"type": "fork", "biome": act1_biome, "act": 1, "fork_options": act2_options, "is_elite": False, "is_boss": False})
    nodes.append({"type": "act2_placeholder", "biome": None, "act": 2, "is_elite": False, "is_boss": False})
    boss = rng.choice(BOSSES)
    nodes.append({"type": "boss", "biome": "ash_wastes", "monster": boss["name"], "boss": boss, "act": 3, "loot": "elite", "is_elite": False, "is_boss": True})
    nodes.append({"type": "ending", "biome": None, "act": 3, "is_elite": False, "is_boss": False})
    return nodes

def expand_act2(gs, chosen_biome):
    rng = gs["rng"]
    b = BIOMES[chosen_biome]
    act2_nodes = []
    monsters2 = rng.sample(b["monsters"], min(3, len(b["monsters"])))
    events2 = rng.sample(b["events"], min(3, len(b["events"])))
    act2_nodes.append({"type": "combat", "biome": chosen_biome, "monster": monsters2[0], "act": 2, "loot": "normal", "is_elite": False, "is_boss": False})
    act2_nodes.append({"type": "event", "biome": chosen_biome, "event_key": events2[0], "act": 2, "loot": "normal", "is_elite": False, "is_boss": False})
    act2_nodes.append({"type": "merchant", "biome": chosen_biome, "act": 2, "is_elite": False, "is_boss": False})
    act2_nodes.append({"type": "combat", "biome": chosen_biome, "monster": monsters2[1 % len(monsters2)], "act": 2, "loot": "normal", "is_elite": False, "is_boss": False})
    if len(events2) > 1:
        act2_nodes.append({"type": "event", "biome": chosen_biome, "event_key": events2[1], "act": 2, "loot": "normal", "is_elite": False, "is_boss": False})
    elite2 = monsters2[-1]
    act2_nodes.append({"type": "elite_combat", "biome": chosen_biome, "monster": elite2, "act": 2, "loot": "good", "is_elite": True, "is_boss": False})
    if gs["flags"].get("relic_shard") or has_relic(gs, "reveal_hidden"):
        secret_event = events2[2 % len(events2)] if len(events2) > 0 else "cracked_chest"
        act2_nodes.append({"type": "secret", "biome": chosen_biome, "event_key": secret_event, "act": 2, "loot": "elite", "is_elite": False, "is_boss": False})
    act3_biome = "ash_wastes"
    act3_monster = rng.choice(BIOMES[act3_biome]["monsters"])
    act2_nodes.append({"type": "combat", "biome": act3_biome, "monster": act3_monster, "act": 3, "loot": "normal", "is_elite": False, "is_boss": False})
    act2_nodes.append({"type": "event", "biome": act3_biome, "event_key": rng.choice(BIOMES[act3_biome]["events"]), "act": 3, "loot": "normal", "is_elite": False, "is_boss": False})
    new_nodes = []
    for n in gs["run_nodes"]:
        if n["type"] == "act2_placeholder":
            new_nodes.extend(act2_nodes)
        else:
            new_nodes.append(n)
    gs["run_nodes"] = new_nodes

# =====================================================================
# COMBAT
# =====================================================================

def start_combat(gs, node):
    monster_name = node.get("monster") or node.get("boss", {}).get("name", "Goblin Scrapper")
    if node.get("is_boss"):
        boss_data = node["boss"]
        enemy = copy.deepcopy(boss_data)
        enemy["is_boss"] = True
        enemy_hp = boss_data["hp"]
    else:
        m = get_monster(monster_name)
        enemy = copy.deepcopy(m)
        enemy["is_boss"] = False
        enemy_hp = m["hp"]
        if node.get("is_elite"):
            enemy["hp"] = int(enemy["hp"] * 1.5)
            enemy["attack"] = enemy["attack"] + 2
            enemy_hp = enemy["hp"]
            enemy["name"] = "Elite " + enemy["name"]
    gs["combat_state"] = {
        "enemy": enemy,
        "enemy_hp": enemy_hp,
        "enemy_max_hp": enemy_hp,
        "turn": 1,
        "phase2_triggered": False,
        "first_turn": True,
        "player_stunned": False,
        "enemy_frozen": 0,
        "enemy_poisoned": 0,
        "enemy_bleed": 0,
        "intent_idx": 0,
        "rally_used": False,
        "mana_shield_active": False,
        "mana_shield_used": False,
        "mend_used": False,
        "shield_bash_used": False,
        "combat_log": [],
        "result": None,
        "node_loot_quality": node.get("loot", "normal"),
        "weapon_drop": None,
    }
    add_log(gs, f"⚔️ Combat begins: {enemy['name']}!")

def get_current_intent(cs):
    enemy = cs["enemy"]
    pool = enemy.get("intent_pool", enemy.get("intents", ["attacks"]))
    if not pool:
        return "attacks"
    idx = cs["intent_idx"] % len(pool)
    return pool[idx]

def apply_combat_action(gs, action, skill_key=None, item_idx=None):
    cs = gs["combat_state"]
    p = gs["player"]
    enemy = cs["enemy"]
    clog = []
    if cs["result"] is not None:
        return

    # PLAYER TURN
    if cs["player_stunned"]:
        clog.append("🌀 You are stunned and lose your turn!")
        cs["player_stunned"] = False
    else:
        weapon = get_weapon(p["weapon"])
        base_dmg = max(1, p["attack"] + weapon["damage_bonus"] + gs["rng"].randint(-1, 2))

        if action == "attack":
            dmg = base_dmg
            if p.get("passive_key") == "opportunist" and cs["first_turn"]:
                if gs["rng"].random() < 0.30:
                    dmg *= 2
                    clog.append("🗡️ **Opportunist!** Double damage on opening strike!")
            undead_names = ["Skeleton Archer", "Hollow Knight", "Elite Skeleton Archer", "Elite Hollow Knight", "The Hollow King", "Ashen Lich"]
            if weapon.get("special") == "holy" and enemy["name"] in undead_names:
                dmg += 5
                clog.append("✨ Holy weapon blazes against the undead!")
            extra_hit = 0
            if weapon.get("special") == "double_strike" and gs["rng"].random() < 0.35:
                extra_hit = base_dmg
                clog.append("⚡ Stormcaller strikes twice!")
            if weapon.get("special") == "freeze" and gs["rng"].random() < 0.20 and cs["enemy_frozen"] == 0:
                cs["enemy_frozen"] = 1
                clog.append("❄️ Frostbrand freezes the enemy!")
            cs["enemy_hp"] -= dmg + extra_hit
            clog.append(f"⚔️ You strike for **{dmg + extra_hit}** damage.")
            if weapon.get("special") == "bleed" and cs["enemy_bleed"] == 0:
                cs["enemy_bleed"] = 3
                clog.append("🩸 Target is bleeding!")
            if weapon.get("special") == "poison" and cs["enemy_poisoned"] == 0:
                cs["enemy_poisoned"] = 3
                clog.append("☠️ Target is poisoned!")
            if weapon.get("special") == "drain":
                p["hp"] -= 2
                clog.append("💀 Cursed blade drains 2 HP from you.")

        elif action == "skill":
            sk_key = skill_key
            if sk_key == "shield_bash":
                dmg = base_dmg
                cs["enemy_hp"] -= dmg
                cs["enemy_frozen"] = 1
                clog.append(f"🛡️ Shield Bash! {dmg} damage, enemy stunned!")
            elif sk_key == "rally":
                if cs["rally_used"]:
                    clog.append("Rally already used this combat.")
                else:
                    p["hp"] = min(p["max_hp"], p["hp"] + 6)
                    cs["rally_used"] = True
                    clog.append("💪 Rally! Restored 6 HP.")
            elif sk_key == "backstab":
                if p["hp"] > 3:
                    p["hp"] -= 3
                    dmg = base_dmg * 2
                    cs["enemy_hp"] -= dmg
                    clog.append(f"🗡️ Backstab! Spent 3 HP for **{dmg}** damage!")
                else:
                    clog.append("Not enough HP for Backstab!")
            elif sk_key == "smoke_bomb":
                cs["result"] = "flee"
                cs["combat_log"] = ["💨 Smoke Bomb — vanished into shadow!"]
                add_log(gs, "💨 Smoke Bomb — vanished into shadow!")
                return
            elif sk_key == "arcane_bolt":
                dmg = 8
                if p.get("passive_key") == "spellweave":
                    dmg = 12
                cs["enemy_hp"] -= dmg
                clog.append(f"🔮 Arcane Bolt! {dmg} magic damage (ignores armor)!")
            elif sk_key == "mana_shield":
                if cs["mana_shield_used"]:
                    clog.append("Mana Shield already used this combat.")
                else:
                    cs["mana_shield_active"] = True
                    cs["mana_shield_used"] = True
                    clog.append("🔵 Mana Shield raised — next hit absorbed!")
            elif sk_key == "smite":
                dmg = p["attack"] + 4
                undead_names = ["Skeleton Archer", "Hollow Knight", "Elite Skeleton Archer", "Elite Hollow Knight", "The Hollow King", "Ashen Lich"]
                if enemy["name"] in undead_names:
                    dmg += 6
                    clog.append(f"☀️ Smite blazes against undead! **{dmg}** damage!")
                else:
                    clog.append(f"☀️ Smite! **{dmg}** damage!")
                cs["enemy_hp"] -= dmg
            elif sk_key == "mend":
                if cs["mend_used"]:
                    clog.append("Mend already used this combat.")
                else:
                    p["hp"] = min(p["max_hp"], p["hp"] + 10)
                    cs["mend_used"] = True
                    clog.append("💚 Mend! Restored 10 HP.")

        elif action == "item" and item_idx is not None:
            inv = p["inventory"]
            if 0 <= item_idx < len(inv):
                itm = inv[item_idx]
                msg = apply_item_effect(gs, itm, cs)
                clog.append(msg)
                p["inventory"].pop(item_idx)
                if cs["result"] == "flee":
                    cs["combat_log"] = clog
                    return

        elif action == "flee":
            flee_ok = False
            if has_relic(gs, "flee_always"):
                flee_ok = True
            elif enemy.get("is_boss"):
                flee_ok = False
                clog.append("🚫 Cannot flee from a boss!")
                cs["combat_log"] = clog
                cs["turn"] += 1
                return
            elif cs["enemy"].get("is_elite", False) or "Elite" in enemy["name"]:
                flee_ok = gs["rng"].random() < 0.30
            else:
                flee_ok = gs["rng"].random() < 0.50
            if flee_ok:
                cs["result"] = "flee"
                cs["combat_log"] = ["💨 You fled the battle!"]
                add_log(gs, "💨 You fled the battle!")
                return
            else:
                clog.append("❌ Couldn't flee!")

    cs["first_turn"] = False

    # Check if enemy died from player turn
    if cs["enemy_hp"] <= 0:
        cs["combat_log"] = clog[-5:]
        _resolve_combat_win(gs, cs, clog)
        return

    # ENEMY TURN
    if cs["enemy_frozen"] > 0:
        clog.append(f"❄️ {enemy['name']} is frozen! Loses turn.")
        cs["enemy_frozen"] -= 1
    else:
        intent = get_current_intent(cs)
        e_atk = enemy["attack"] + gs["rng"].randint(-1, 2)

        if enemy.get("is_boss") and not cs["phase2_triggered"]:
            phase2_hp = enemy.get("phase2_trigger", enemy["hp"] // 2)
            if cs["enemy_hp"] <= phase2_hp:
                cs["phase2_triggered"] = True
                bonus = enemy.get("phase2_attack_bonus", 3)
                enemy["attack"] += bonus
                clog.append(f"💥 **{enemy['name']} ENRAGES!** Attack increased!")

        eff_defense = p["defense"]
        if p.get("passive_key") == "bulwark" and p["hp"] < p["max_hp"] // 2:
            eff_defense += 2
        e_dmg = max(0, e_atk - max(0, eff_defense - 1))

        special = enemy.get("special")
        if special == "shield_block" and gs["rng"].random() < 0.40:
            e_dmg = e_dmg // 2
            clog.append("🛡️ Enemy blocked part of your last attack!")
        if special == "web" and gs["rng"].random() < 0.30:
            cs["player_stunned"] = True
            clog.append("🕸️ You're caught in a web! Next turn lost.")
        if special == "poison_atk" and gs["rng"].random() < 0.25:
            p["status_effects"]["poison"] = max(p["status_effects"].get("poison", 0), 3)
            clog.append("☠️ Enemy poisoned you!")
        if special == "lifesteal":
            cs["enemy_hp"] = min(cs["enemy_max_hp"], cs["enemy_hp"] + 3)
            clog.append("🩸 Enemy siphons vitality!")
        if special == "burn":
            e_dmg += 2
            p["status_effects"]["burn"] = max(p["status_effects"].get("burn", 0), 2)
            clog.append("🔥 Burning aura scorches you!")
        if special == "sacrifice" and gs["rng"].random() < 0.20:
            cs["enemy_hp"] -= 5
            e_dmg += 8
            clog.append("💀 Cultist spills own blood for power!")
        if special == "spore_cloud" and gs["rng"].random() < 0.30:
            p["status_effects"]["poison"] = p["status_effects"].get("poison", 0) + 2
            clog.append("🍄 Spore cloud poisons you!")
        if special == "ash_armor" and cs["phase2_triggered"] and gs["rng"].random() < 0.25:
            e_dmg = max(0, e_dmg - 3)
            clog.append("🌋 Ash armor absorbs some damage!")

        if cs.get("mana_shield_active"):
            e_dmg = 0
            cs["mana_shield_active"] = False
            clog.append("🔵 Mana Shield absorbs the hit!")

        if e_dmg > 0:
            p["hp"] -= e_dmg
            clog.append(f"💥 {enemy['name']} {intent} — deals **{e_dmg}** damage!")
        else:
            clog.append(f"🛡️ {enemy['name']} {intent} — blocked/negated!")

        cs["intent_idx"] += 1

    # STATUS TICKS
    if cs["enemy_bleed"] > 0:
        cs["enemy_hp"] -= 2
        cs["enemy_bleed"] -= 1
        clog.append("🩸 Enemy bleeds for 2 damage.")
    if cs["enemy_poisoned"] > 0:
        cs["enemy_hp"] -= 2
        cs["enemy_poisoned"] -= 1
        clog.append("☠️ Enemy writhes in poison.")
    if p["status_effects"].get("poison", 0) > 0:
        p["hp"] -= 2
        p["status_effects"]["poison"] -= 1
        clog.append("☠️ Poison burns through you for 2 damage.")
    if p["status_effects"].get("burn", 0) > 0:
        p["hp"] -= 2
        p["status_effects"]["burn"] -= 1
        clog.append("🔥 Burns for 2 damage.")
    if p["status_effects"].get("bleed", 0) > 0:
        p["hp"] -= 2
        p["status_effects"]["bleed"] -= 1
        clog.append("🩸 Bleeding for 2 damage.")

    if has_relic(gs, "tome_suffering"):
        gs["flags"]["combat_count"] = gs["flags"].get("combat_count", 0) + 1
        if gs["flags"]["combat_count"] % 3 == 0:
            cs["enemy_hp"] -= 10
            clog.append("📕 Tome of Suffering — bonus 10 damage!")

    cs["combat_log"] = clog[-6:]
    cs["turn"] += 1

    if cs["enemy_hp"] <= 0:
        _resolve_combat_win(gs, cs, clog)
        return
    if p["hp"] <= 0:
        p["hp"] = 0
        cs["result"] = "lose"
        gs["ending_key"] = "tragic_failure"
        add_log(gs, "💀 You have fallen...")

def _resolve_combat_win(gs, cs, clog):
    p = gs["player"]
    enemy = cs["enemy"]
    cs["result"] = "win"
    loot = roll_loot(gs["rng"], cs["node_loot_quality"])
    if has_relic(gs, "gold_boost"):
        loot["gold"] = int(loot["gold"] * 1.5)
    p["gold"] += loot["gold"]
    xp_gain = enemy.get("xp", 10)
    p["kills"] = p.get("kills", 0) + 1
    if has_relic(gs, "vamp_kill"):
        p["hp"] = min(p["max_hp"], p["hp"] + 3)
        add_log(gs, "🩸 Bloodstone Ring — killing blow restores 3 HP!")
    add_log(gs, f"✅ Defeated {enemy['name']}! +{loot['gold']} gold, +{xp_gain} XP")
    if loot["item"]:
        if add_to_inventory(gs, loot["item"]):
            add_log(gs, f"🎒 Found: {loot['item']['name']}")
        else:
            add_log(gs, f"🎒 Inventory full — left behind {loot['item']['name']}")
    if loot["weapon"]:
        cs["weapon_drop"] = loot["weapon"]["name"]
        gs["flags"]["pending_weapon"] = loot["weapon"]["name"]
        add_log(gs, f"⚔️ Weapon dropped: {loot['weapon']['name']}!")
    if enemy.get("is_boss"):
        gs["flags"]["boss_defeated"] = True

def apply_item_effect(gs, item, cs=None):
    p = gs["player"]
    effect = item.get("effect")
    val = item.get("value", 0)
    if effect == "heal":
        p["hp"] = min(p["max_hp"], p["hp"] + val)
        return f"💊 {item['name']}: restored {val} HP."
    elif effect == "cure_poison":
        p["status_effects"]["poison"] = 0
        return "🧪 Antidote: cured poison."
    elif effect == "flee" and cs:
        cs["result"] = "flee"
        return "💨 Smoke Bomb: escaped!"
    elif effect == "bomb" and cs:
        dmg = val
        cs["enemy_hp"] -= dmg
        return f"💣 Bomb: {dmg} damage!"
    elif effect == "scroll_flame" and cs:
        dmg = int(val * (1.5 if p.get("passive_key") == "spellweave" else 1))
        cs["enemy_hp"] -= dmg
        return f"🔥 Scroll of Flame: {dmg} fire damage!"
    elif effect == "scroll_frost" and cs:
        cs["enemy_frozen"] = 1
        return "❄️ Scroll of Frost: enemy frozen 1 turn!"
    elif effect == "ration":
        p["hp"] = min(p["max_hp"], p["hp"] + val)
        p["status_effects"]["fatigue"] = 0
        return f"🍖 Iron Ration: restored {val} HP."
    return f"Used {item['name']}."

# =====================================================================
# EVENTS
# =====================================================================

def apply_relic_passive(gs, relic):
    p = gs["player"]
    effect = relic.get("effect")
    if effect == "idol_broken":
        p["attack"] += 3
        p["max_hp"] = max(5, p["max_hp"] - 5)
        p["hp"] = min(p["hp"], p["max_hp"])
        add_log(gs, "🗿 Idol of the Broken God: +3 attack, -5 max HP.")
    elif effect == "reveal_hidden":
        add_log(gs, "🧭 Void Compass: hidden routes may now be revealed.")

def resolve_event_choice(gs, event_key, choice_idx):
    event = EVENTS.get(event_key)
    if not event:
        advance_node(gs)
        return
    p = gs["player"]
    rng = gs["rng"]
    choice = event["choices"][choice_idx]
    outcome = choice.get("outcome_key", "nothing")

    if outcome == "loot_or_trap":
        if rng.random() < 0.30:
            dmg = rng.randint(5, 10)
            p["hp"] -= dmg
            add_log(gs, f"💥 Trap! Took {dmg} damage!")
        else:
            loot = roll_loot(rng, "normal")
            p["gold"] += loot["gold"]
            add_log(gs, f"💰 Opened chest: +{loot['gold']} gold!")
            if loot["item"]:
                add_to_inventory(gs, loot["item"])
                add_log(gs, f"🎒 Found: {loot['item']['name']}")
    elif outcome == "pray_shrine":
        heal = 8 if p.get("passive_key") != "sacred_ground" else 16
        if rng.random() < 0.20:
            gs["flags"]["corruption"] = gs["flags"].get("corruption", 0) + 1
            add_log(gs, "⚠️ The shrine was cursed! +1 corruption.")
        else:
            p["hp"] = min(p["max_hp"], p["hp"] + heal)
            add_log(gs, f"🙏 Shrine restored {heal} HP.")
    elif outcome == "desecrate_shrine":
        p["gold"] += 5
        gs["flags"]["corruption"] = gs["flags"].get("corruption", 0) + 1
        add_log(gs, "💰 Pocketed 5 gold. +1 corruption.")
    elif outcome == "shortcut":
        p["hp"] -= 3
        add_log(gs, "🧱 Squeezed through. Took 3 damage. Shortcut taken.")
        gs["flags"]["took_shortcut"] = True
    elif outcome == "eat_mushroom":
        if rng.random() < 0.5:
            heal = 10 if p.get("passive_key") != "sacred_ground" else 20
            p["hp"] = min(p["max_hp"], p["hp"] + heal)
            add_log(gs, f"🍄 Delicious! Restored {heal} HP.")
        else:
            p["status_effects"]["poison"] = p["status_effects"].get("poison", 0) + 2
            add_log(gs, "🍄 Hallucinations and nausea. Poisoned!")
    elif outcome == "pocket_mushroom":
        antidote = next((c for c in CONSUMABLES if c["effect"] == "cure_poison"), None)
        if antidote and add_to_inventory(gs, antidote):
            add_log(gs, "🎒 Pocketed: Antidote.")
        else:
            add_log(gs, "🎒 Inventory full.")
    elif outcome == "bathe_pool":
        if rng.random() < 0.5:
            p["max_hp"] += 5
            p["hp"] = min(p["max_hp"], p["hp"] + 5)
            add_log(gs, "🌊 Pool invigorates you! +5 max HP.")
        else:
            p["status_effects"]["poison"] = p["status_effects"].get("poison", 0) + 3
            add_log(gs, "🌊 Spores enter your bloodstream. Poisoned!")
        gs["flags"]["used_pool"] = True
    elif outcome == "open_merchant":
        open_shop(gs)
        gs["event_resolved"] = True
        return
    elif outcome == "rob_merchant":
        p["gold"] += 15
        gs["flags"]["robbed_merchant"] = True
        gs["flags"]["corruption"] = gs["flags"].get("corruption", 0) + 2
        add_log(gs, "🔪 Robbed the merchant! +15 gold, +2 corruption.")
    elif outcome == "rest_fire":
        p["hp"] = min(p["max_hp"], p["hp"] + 5)
        add_log(gs, "🔥 Warmed by the fire. +5 HP.")
    elif outcome == "enter_hidden":
        if gs["flags"].get("chapel_key") or has_relic(gs, "reveal_hidden"):
            gs["flags"]["relic_shard"] = True
            add_log(gs, "🗝️ Hidden passage! Found a relic shard.")
        else:
            add_log(gs, "🚪 Locked. Needs a chapel key or special compass.")
    elif outcome == "offer_blood":
        p["hp"] -= 6
        gs["flags"]["corruption"] = gs["flags"].get("corruption", 0) + 2
        pool = [r for r in RELICS if r["rarity"] in ("uncommon", "rare")]
        relic = rng.choice(pool)
        if relic["name"] not in p["relics"]:
            p["relics"].append(relic["name"])
            apply_relic_passive(gs, relic)
            add_log(gs, f"🩸 Dark altar empowers you! Gained: {relic['name']}")
        gs["flags"]["altar_visited"] = True
    elif outcome == "cleric_altar_relic":
        if p.get("passive_key") == "sacred_ground":
            relic = rng.choice(RELICS)
            if relic["name"] not in p["relics"]:
                p["relics"].append(relic["name"])
                apply_relic_passive(gs, relic)
                add_log(gs, f"✨ Sacred power grants you: {relic['name']}")
        else:
            add_log(gs, "🙏 You pray, but nothing responds.")
    elif outcome == "smash_altar":
        gs["flags"]["fate"] = gs["flags"].get("fate", 0) + 1
        p["gold"] = max(0, p["gold"] - 5)
        add_log(gs, "🔨 Altar smashed. +1 fate. Lost 5 gold in the chaos.")
    elif outcome == "holy_shrine_pray":
        if p.get("passive_key") == "sacred_ground":
            p["hp"] = p["max_hp"]
            add_log(gs, "🌟 Sacred Ground! Fully restored!")
        else:
            heal = 12
            p["hp"] = min(p["max_hp"], p["hp"] + heal)
            add_log(gs, f"✨ Holy light restored {heal} HP.")
    elif outcome == "donate_shrine":
        if p["gold"] >= 10:
            p["gold"] -= 10
            bonus = 15 if p.get("passive_key") == "sacred_ground" else 10
            p["max_hp"] += max(2, bonus // 5)
            p["hp"] += max(2, bonus // 5)
            add_log(gs, f"💰 Donated 10 gold. +{max(2, bonus // 5)} max HP.")
        else:
            add_log(gs, "💸 Not enough gold to donate.")
    elif outcome == "confess":
        gs["flags"]["corruption"] = max(0, gs["flags"].get("corruption", 0) - 2)
        add_log(gs, "🙏 Confession reduces corruption by 2.")
    elif outcome == "lie_confess":
        p["gold"] += 8
        gs["flags"]["corruption"] = gs["flags"].get("corruption", 0) + 1
        add_log(gs, "😈 Lied beautifully. +8 gold, +1 corruption.")
    elif outcome == "read_tome":
        if p.get("passive_key") == "spellweave":
            p["attack"] += 2
            add_log(gs, "📚 Arcane Scholar absorbs the tome! +2 attack permanently.")
        else:
            p["hp"] -= 5
            add_log(gs, "📚 Psychic backlash! Took 5 damage.")
        gs["flags"]["has_tome"] = True
    elif outcome == "burn_tome":
        gs["flags"]["fate"] = gs["flags"].get("fate", 0) + 2
        add_log(gs, "🔥 Tome burns. +2 fate.")
    elif outcome == "take_tome":
        gs["flags"]["has_tome"] = True
        add_log(gs, "📖 Tome taken. Its pages whisper to you...")
    elif outcome == "drink_font":
        p["hp"] = min(p["max_hp"], p["hp"] + 15)
        gs["flags"]["corruption"] = gs["flags"].get("corruption", 0) + 2
        add_log(gs, "🩸 Blood font restored 15 HP. +2 corruption. Worth it?")
    elif outcome == "bless_font":
        if p.get("passive_key") == "sacred_ground":
            holy_water = {"name": "Holy Water", "effect": "heal", "value": 20, "description": "Blessed water. Heals 20 HP."}
            if add_to_inventory(gs, holy_water):
                add_log(gs, "✨ Purified font. Gained Holy Water.")
            else:
                add_log(gs, "🎒 Inventory full.")
        else:
            add_log(gs, "🙏 You bless it, but lack the power to purify.")
    elif outcome == "dig_cache":
        if rng.random() < 0.5:
            loot = roll_loot(rng, "good")
            p["gold"] += loot["gold"]
            add_log(gs, f"🔥 Found items in the ash! +{loot['gold']} gold.")
            if loot["item"]:
                add_to_inventory(gs, loot["item"])
        else:
            p["hp"] -= 8
            add_log(gs, "🔥 Ash erupts! Burned for 8 damage.")
    elif outcome == "mark_cache":
        gs["flags"]["found_cache"] = True
        add_log(gs, "📍 Marked location. Useful later?")
    elif outcome == "barter_trade":
        inv = p["inventory"]
        if inv:
            inv.pop(0)
            pool = [w for w in WEAPONS if w["rarity"] == "uncommon"]
            w = rng.choice(pool)
            gs["flags"]["pending_weapon"] = w["name"]
            add_log(gs, f"🔄 Traded consumable for: {w['name']}!")
        else:
            add_log(gs, "🎒 Nothing to trade.")
    elif outcome == "loot_goblin_stash":
        gold = rng.randint(2, 12)
        if p.get("passive_key") == "opportunist":
            gold *= 2
            add_log(gs, f"🪙 Rogue instincts! Double gold: +{gold}!")
        else:
            add_log(gs, f"🪙 Looted goblin stash: +{gold} gold.")
        p["gold"] += gold
    elif outcome == "disarm_trap":
        if p.get("passive_key") == "opportunist":
            parts = {"name": "Trap Parts", "effect": "bomb", "value": 12, "description": "Repurposed trap mechanism."}
            add_to_inventory(gs, parts)
            p["gold"] += 5
            add_log(gs, "🔧 Rogue disarms trap perfectly. +5 gold + trap parts!")
        else:
            if rng.random() < 0.5:
                add_log(gs, "🔧 Disarmed! Safe passage.")
            else:
                p["hp"] -= 8
                add_log(gs, "💥 Trap triggered! Took 8 damage.")
    elif outcome == "trigger_trap":
        p["hp"] -= 8
        add_log(gs, "💥 Triggered trap. Took 8 damage. Path clear now.")
    elif outcome == "burn_nest":
        p["hp"] -= 5
        p["gold"] += 15
        add_log(gs, "🔥 Burned the nest. +15 gold, 5 damage from angry spiders.")
    elif outcome == "sneak_nest":
        if p.get("passive_key") == "opportunist":
            add_log(gs, "🕷️ Rogue slips past effortlessly.")
        else:
            if rng.random() < 0.60:
                add_log(gs, "🕷️ Sneaked past the nest.")
            else:
                p["hp"] -= 8
                add_log(gs, "🕷️ Bitten! 8 damage.")
    elif outcome == "mine_crystals":
        p["gold"] += 8
        add_log(gs, "💎 Mined 8 gold worth of crystals.")
        if rng.random() < 0.20:
            pool = [w for w in WEAPONS if w["rarity"] == "uncommon"]
            w = rng.choice(pool)
            gs["flags"]["pending_weapon"] = w["name"]
            add_log(gs, f"⚔️ Crystal resonance reveals a weapon: {w['name']}!")
    elif outcome == "take_crystal":
        gs["flags"]["relic_shard"] = True
        add_log(gs, "💎 Kept crystal shard. Something feels significant...")
    elif outcome == "destroy_effigy":
        if p.get("status_effects", {}).get("curse", 0):
            p["status_effects"]["curse"] = 0
            add_log(gs, "🔥 Curse lifted by destroying the effigy!")
        else:
            add_log(gs, "🔥 Effigy destroyed. A small relief.")
    elif outcome == "worship_effigy":
        if p.get("passive_key") in ("opportunist", "spellweave"):
            p["gold"] += 3
            add_log(gs, "🔥 Effigy rewards your alignment. +3 gold.")
        else:
            add_log(gs, "🔥 Nothing happens. The effigy ignores you.")
    else:
        add_log(gs, f"You chose: {choice['text']}.")

    gs["event_resolved"] = True

# =====================================================================
# SHOP
# =====================================================================

def open_shop(gs):
    rng = gs["rng"]
    base_items = [
        {"name": "Health Potion", "price": 8, "type": "consumable"},
        {"name": "Greater Potion", "price": 15, "type": "consumable"},
        {"name": "Antidote", "price": 5, "type": "consumable"},
        {"name": "Bomb", "price": 10, "type": "consumable"},
        {"name": "Scroll of Flame", "price": 12, "type": "consumable"},
        {"name": "Iron Ration", "price": 6, "type": "consumable"},
        {"name": "Smoke Bomb", "price": 14, "type": "consumable"},
        {"name": "Scroll of Frost", "price": 10, "type": "consumable"},
    ]
    selected = rng.sample(base_items, 4)
    uncommon_w = [w for w in WEAPONS if w["rarity"] == "uncommon"]
    rare_w = [w for w in WEAPONS if w["rarity"] == "rare"]
    selected.append({"name": rng.choice(uncommon_w)["name"], "price": 20, "type": "weapon"})
    if rng.random() < 0.5 and rare_w:
        selected.append({"name": rng.choice(rare_w)["name"], "price": 35, "type": "weapon"})
    gs["shop_items"] = selected

def render_shop(gs):
    p = gs["player"]
    st.markdown("### 🏪 Merchant")
    st.write(f"**Gold:** {p['gold']} 🪙")
    items = gs["shop_items"] or []
    for i, item in enumerate(items):
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.write(f"**{item['name']}** ({item['type']})")
        with col2:
            st.write(f"{item['price']} g")
        with col3:
            if st.button("Buy", key=f"buy_{i}"):
                if p["gold"] >= item["price"]:
                    p["gold"] -= item["price"]
                    if item["type"] == "consumable":
                        cons = next((c for c in CONSUMABLES if c["name"] == item["name"]), None)
                        if cons and add_to_inventory(gs, cons):
                            add_log(gs, f"🛒 Bought: {item['name']}")
                        else:
                            p["gold"] += item["price"]
                            add_log(gs, "🎒 Inventory full!")
                    elif item["type"] == "weapon":
                        w = get_weapon(item["name"])
                        gs["flags"]["pending_weapon"] = w["name"]
                        add_log(gs, f"⚔️ Bought weapon: {w['name']}!")
                    st.rerun()
                else:
                    add_log(gs, "💸 Not enough gold!")
                    st.rerun()
    if st.button("Leave Shop"):
        gs["shop_items"] = None
        gs["event_resolved"] = True
        advance_node(gs)
        st.rerun()

# =====================================================================
# NODE ADVANCEMENT
# =====================================================================

def advance_node(gs):
    gs["current_node_idx"] += 1
    gs["event_resolved"] = False
    gs["rest_used"] = False
    gs["rest_searched"] = False
    gs["secret_taken"] = False
    gs["node_intro_dismissed"] = False
    gs["post_result_text"] = None
    if gs["current_node_idx"] >= len(gs["run_nodes"]):
        gs["screen"] = "ending"
        if not gs.get("ending_key"):
            gs["ending_key"] = determine_ending(gs)
        return
    gs["current_node"] = gs["run_nodes"][gs["current_node_idx"]]
    gs["combat_state"] = None
    prev_act = gs["act"]
    new_act = gs["current_node"].get("act", gs["act"])
    if new_act != prev_act:
        gs["prev_act"] = prev_act
        gs["show_act_transition"] = True
    gs["act"] = new_act
    if gs["current_node"]["type"] == "ending":
        gs["screen"] = "ending"
        gs["ending_key"] = determine_ending(gs)
        return
    if gs["current_node"]["type"] in ("combat", "elite_combat", "boss"):
        start_combat(gs, gs["current_node"])

def determine_ending(gs):
    p = gs["player"]
    flags = gs["flags"]
    if p["hp"] <= 0:
        return "tragic_failure"
    if flags.get("has_tome") and flags.get("relic_shard") and flags.get("corruption", 0) <= 2 and flags.get("boss_defeated"):
        return "true_ending"
    if flags.get("boss_defeated"):
        if flags.get("corruption", 0) >= 6:
            return "corrupted_power"
        return "heroic_victory"
    if p["hp"] < 5:
        return "escape_survival"
    return "escape_survival"

# =====================================================================
# UI RENDERING
# =====================================================================

def render_pending_weapon(gs):
    pname = gs["flags"].get("pending_weapon")
    if not pname:
        return
    w = get_weapon(pname)
    st.markdown(
        f"<div class='pending-weapon'>⚔️ <b>Weapon available:</b> "
        f"<span class='{rarity_class(w['rarity'])}'>{w['name']}</span> "
        f"(+{w['damage_bonus']} dmg, {w['rarity']}) — <i>{w['description']}</i></div>",
        unsafe_allow_html=True
    )
    c1, c2, _ = st.columns([1, 1, 4])
    with c1:
        if st.button("Equip", key="equip_pending"):
            gs["player"]["weapon"] = pname
            gs["flags"]["pending_weapon"] = None
            add_log(gs, f"⚔️ Equipped {pname}!")
            st.rerun()
    with c2:
        if st.button("Discard", key="discard_pending"):
            gs["flags"]["pending_weapon"] = None
            add_log(gs, "🗑️ Weapon discarded.")
            st.rerun()

def render_sidebar(gs):
    p = gs["player"]
    if not p:
        return
    with st.sidebar:
        cls = CLASSES.get(p.get("class_key"), {})
        st.markdown(f"### {cls.get('emoji','')} {cls.get('name','Adventurer')}")
        st.caption(p.get("passive_desc", ""))

        hp_ratio = max(0, p["hp"] / max(1, p["max_hp"]))
        st.markdown(f"**HP:** {p['hp']} / {p['max_hp']}")
        st.progress(hp_ratio)

        st.markdown("---")
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("⚔️ ATK", p["attack"])
        with c2: st.metric("🛡️ DEF", p["defense"])
        with c3: st.metric("🪙 Gold", p["gold"])

        w = get_weapon(p["weapon"])
        st.markdown(
            f"**Weapon:** <span class='{rarity_class(w['rarity'])}'>{w['name']}</span> (+{w['damage_bonus']})",
            unsafe_allow_html=True
        )

        st.markdown("---")
        st.markdown("**🏺 Relics**")
        if p["relics"]:
            for r_name in p["relics"]:
                r = get_relic(r_name)
                if r:
                    st.markdown(f"- <span class='{rarity_class(r['rarity'])}'>{r['name']}</span> — *{r['description']}*", unsafe_allow_html=True)
        else:
            st.caption("None yet.")

        st.markdown("**🎒 Inventory**")
        inv = p["inventory"]
        if not inv:
            st.caption("Empty.")
        else:
            in_combat = gs.get("combat_state") and gs["combat_state"].get("result") is None
            for i, itm in enumerate(inv):
                cols = st.columns([4, 1])
                with cols[0]:
                    st.caption(f"• {itm['name']} — {itm.get('description','')}")
                with cols[1]:
                    if not in_combat:
                        if st.button("Use", key=f"inv_use_{i}"):
                            msg = apply_item_effect(gs, itm, None)
                            add_log(gs, msg)
                            inv.pop(i)
                            st.rerun()

        status = p.get("status_effects", {})
        active = [(k, v) for k, v in status.items() if v and v > 0]
        if active:
            st.markdown("**⚠️ Status**")
            for k, v in active:
                st.caption(f"{k}: {v} turn(s)")

        st.markdown("---")
        corr = gs["flags"].get("corruption", 0)
        fate = gs["flags"].get("fate", 0)
        st.markdown(f"**Corruption:** {'🔴' * min(corr, 10)}" + (f" ({corr})" if corr > 10 else ""))
        st.markdown(f"**Fate:** {'⭐' * min(fate, 10)}" + (f" ({fate})" if fate > 10 else ""))

        st.markdown("---")
        node = gs.get("current_node") or {}
        biome_key = node.get("biome")
        if biome_key and biome_key in BIOMES:
            b = BIOMES[biome_key]
            st.markdown(f"<span class='biome-tag'>{b['emoji']} {b['name']}</span>", unsafe_allow_html=True)
        st.caption(f"Act {gs.get('act', 1)} · Node {gs['current_node_idx']+1}/{len(gs['run_nodes'])}")

        st.markdown("**📜 Recent Log**")
        for entry in gs["log"][:4]:
            st.markdown(f"<div class='log-entry'>• {entry}</div>", unsafe_allow_html=True)

def render_title():
    st.markdown("<h1 style='text-align:center; font-size:3em; letter-spacing:0.05em;'>⚔️ DEPTHS OF AETHERMOOR</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#8b949e; font-size:1.1em;'>A Rogue-like Text RPG</p>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(
        "<div class='event-box'>The dungeon called Aethermoor was sealed three centuries ago for reasons "
        "no living scholar agrees on. Last week the seal cracked. Wisps of pale light have been seen "
        "drifting from the entrance. Goats refuse to graze nearby. Children draw it without being asked. "
        "<br><br>"
        "You go in because the reward is enormous, or because nobody else will, or because there is "
        "nothing left for you above. The reason changes nothing. The descent is the same."
        "</div>",
        unsafe_allow_html=True
    )
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("⚔️ Begin Your Descent", use_container_width=True, type="primary"):
            st.session_state["gs"]["screen"] = "class_select"
            st.rerun()
    with st.expander("How to Play"):
        st.markdown("""
- Pick a **class** — each has unique stats, passives, and skills.
- Each run is a sequence of **nodes**: combat, events, rest, shops, and a final boss.
- In combat: **Attack**, use **Skills**, **items**, or **Flee** (not from bosses).
- Watch the enemy **intent** to plan your move.
- Choose your path at the **fork** halfway through.
- Discover the **forbidden tome** and a **relic shard** while keeping **corruption** low to unlock the **true ending**.
- Five endings total. Most are not happy.
        """)

def render_class_select(gs):
    st.markdown("## Choose Your Path")
    st.caption("Each class plays differently. Each death is final.")
    cols = st.columns(4)
    class_keys = list(CLASSES.keys())
    for i, key in enumerate(class_keys):
        c = CLASSES[key]
        with cols[i]:
            st.markdown(f"<div class='stat-card'><h3>{c['emoji']} {c['name']}</h3><i>{c['flavor']}</i></div>", unsafe_allow_html=True)
            st.markdown(f"**HP** {c['hp']} · **ATK** {c['attack']} · **DEF** {c['defense']}")
            st.markdown(f"**Starting Gold:** {c['gold']}")
            st.markdown(f"**Weapon:** {c['weapon']}")
            st.markdown(f"**Passive:** *{c['passive']}*")
            st.markdown("**Skills:**")
            for s in c["skills"]:
                st.caption(f"• **{s['name']}** — {s['desc']}")
            if st.button(f"Choose {c['name']}", key=f"choose_{key}", use_container_width=True):
                seed = random.randint(0, 10**9)
                rng = random.Random(seed)
                gs["run_seed"] = seed
                gs["rng"] = rng
                player = {
                    "class_key": key,
                    "class_name": c["name"],
                    "hp": c["hp"],
                    "max_hp": c["max_hp"],
                    "attack": c["attack"],
                    "defense": c["defense"],
                    "gold": c["gold"],
                    "weapon": c["weapon"],
                    "passive_key": c["passive_key"],
                    "passive_desc": c["passive"],
                    "skills": c["skills"],
                    "inventory": [],
                    "relics": [],
                    "kills": 0,
                    "status_effects": {},
                }
                gs["player"] = player
                gs["run_nodes"] = generate_run(rng, key)
                gs["current_node_idx"] = -1
                gs["screen"] = "game"
                advance_node(gs)
                st.rerun()

def render_combat(gs):
    cs = gs["combat_state"]
    if not cs:
        return
    enemy = cs["enemy"]
    p = gs["player"]
    node = gs.get("current_node", {})

    is_boss = enemy.get("is_boss", False)

    # Boss: show cinematic intro text on first turn only
    if is_boss:
        st.markdown(f"<div class='boss-title'>👑 {enemy['name']}</div>", unsafe_allow_html=True)
        intro = enemy.get("intro_text") or enemy.get("description", "")
        if intro and cs.get("turn", 1) == 1 and cs["result"] is None:
            st.markdown(
                f"<div class='event-box' style='border-color:#ef4444; color:#c9d1d9; margin-bottom:12px;'>"
                f"{intro}</div>",
                unsafe_allow_html=True
            )
    elif node.get("is_elite"):
        st.markdown(f"### ⚠️ {enemy['name']} *(Elite)*")
        st.caption(enemy.get("description", ""))
    else:
        st.markdown(f"### 👹 {enemy['name']}")
        st.caption(enemy.get("description", ""))

    enemy_ratio = max(0.0, cs["enemy_hp"] / max(1, cs["enemy_max_hp"]))
    st.markdown(f"**Enemy HP:** {max(0, cs['enemy_hp'])} / {cs['enemy_max_hp']}")
    st.progress(enemy_ratio)

    intent = get_current_intent(cs)
    if cs["result"] is None:
        st.markdown(f"<span class='intent-tag'>Intent: {intent}</span>", unsafe_allow_html=True)

    st.markdown("<div class='combat-box'>", unsafe_allow_html=True)
    if cs["combat_log"]:
        for line in cs["combat_log"]:
            st.markdown(f"<div class='log-entry'>{line}</div>", unsafe_allow_html=True)
    else:
        st.caption("Combat begins. Choose your action.")
    st.markdown("</div>", unsafe_allow_html=True)

    if cs["result"] is None:
        cols = st.columns(4)
        with cols[0]:
            if st.button("⚔️ Attack", use_container_width=True, key="atk"):
                apply_combat_action(gs, "attack")
                st.rerun()
        with cols[1]:
            skills = p.get("skills", [])
            if skills:
                with st.expander("🎯 Skills"):
                    for s in skills:
                        if st.button(f"{s['name']}", key=f"sk_{s['key']}"):
                            apply_combat_action(gs, "skill", skill_key=s["key"])
                            st.rerun()
                        st.caption(s["desc"])
        with cols[2]:
            inv = p.get("inventory", [])
            if inv:
                with st.expander("🎒 Use Item"):
                    for i, itm in enumerate(inv):
                        if st.button(f"Use {itm['name']}", key=f"comb_item_{i}"):
                            apply_combat_action(gs, "item", item_idx=i)
                            st.rerun()
                        st.caption(itm.get("description", ""))
            else:
                st.caption("No items.")
        with cols[3]:
            if st.button("💨 Flee", use_container_width=True, key="flee"):
                apply_combat_action(gs, "flee")
                st.rerun()
    else:
        if cs["result"] == "win":
            st.success(f"✅ Victory! Defeated {enemy['name']}.")
            if cs.get("weapon_drop"):
                st.info(f"⚔️ A {cs['weapon_drop']} was dropped — check the banner to equip.")
            connector = get_post_result_text(gs, "combat_win")
            st.markdown(
                f"<div style='color:#8b949e; font-style:italic; font-size:0.9em; "
                f"margin-top:10px;'>{connector}</div>",
                unsafe_allow_html=True
            )
            if st.button("Continue →", type="primary"):
                advance_node(gs)
                st.rerun()
        elif cs["result"] == "flee":
            st.warning("💨 You escaped.")
            connector = get_post_result_text(gs, "combat_flee")
            st.markdown(
                f"<div style='color:#8b949e; font-style:italic; font-size:0.9em; "
                f"margin-top:10px;'>{connector}</div>",
                unsafe_allow_html=True
            )
            if st.button("Continue →"):
                advance_node(gs)
                st.rerun()
        elif cs["result"] == "lose":
            st.error("💀 You have fallen.")
            if st.button("View Ending →", type="primary"):
                gs["screen"] = "ending"
                gs["ending_key"] = "tragic_failure"
                st.rerun()

def render_event(gs):
    node = gs["current_node"]
    if not node:
        return
    ev = EVENTS.get(node.get("event_key"))
    if not ev:
        st.write("An empty room. Nothing of note.")
        if st.button("Continue →"):
            advance_node(gs)
            st.rerun()
        return

    st.markdown(f"### {ev['title']}")
    st.markdown(f"<div class='event-box'>{ev['text']}</div>", unsafe_allow_html=True)

    if not gs.get("event_resolved"):
        for i, ch in enumerate(ev["choices"]):
            if st.button(f"➤ {ch['text']}", key=f"ev_ch_{i}", use_container_width=True):
                gs["node_intro_dismissed"] = True
                resolve_event_choice(gs, node["event_key"], i)
                st.rerun()
    else:
        if gs.get("shop_items"):
            render_shop(gs)
        else:
            connector = get_post_result_text(gs, "event")
            st.markdown(
                f"<div style='color:#8b949e; font-style:italic; font-size:0.9em; "
                f"margin-top:10px;'>{connector}</div>",
                unsafe_allow_html=True
            )
            if st.button("Continue →", type="primary"):
                advance_node(gs)
                st.rerun()

def render_rest(gs):
    p = gs["player"]
    node = gs.get("current_node", {})
    biome_key = node.get("biome", "ruined_keep")

    # Biome-specific rest camp flavour
    rest_texts = {
        "ruined_keep":   ("A Quiet Camp",
                          "You find a defensible alcove. A small fire crackles where someone else, "
                          "long ago, had the same idea. Their bones make decent kindling. "
                          "The dungeon presses in on all sides, but here — briefly, provisionally — nothing is trying to kill you."),
        "fungal_caverns":("A Dry Ledge",
                          "A shelf of stone above the mycelium, dry enough to sit on without your legs going numb. "
                          "The bioluminescent caps pulse in slow rhythm. In another context this would be peaceful. "
                          "In this context you eat standing up and keep one eye on the dark."),
        "cursed_chapel": ("A Forgotten Vestry",
                          "A side room off the main chapel, locked from the inside by someone who understood "
                          "the value of a door. They are gone but the lock held. You bar it again. "
                          "The singing, faint and atonal, continues through the wall. You choose to ignore it."),
        "ash_wastes":    ("A Scorched Overhang",
                          "Thin shelter under a fallen arch. The heat here is old — ambient, bone-deep, the kind "
                          "that doesn't go away but stops getting worse. You rest. The wastes drift past the opening "
                          "in grey curtains. Something out there makes no sound whatsoever."),
        "goblin_tunnels":("An Abandoned Bolt-hole",
                          "A side tunnel too narrow for anything large. Someone small left a cold fire pit and "
                          "a broken knife. You don't fit comfortably but you fit. The sounds of the tunnels "
                          "continue — distant, arguing, occasionally wet. None of it gets closer."),
    }
    title, text = rest_texts.get(biome_key, rest_texts["ruined_keep"])

    st.markdown(f"### 🔥 {title}")
    st.markdown(f"<div class='event-box'>{text}</div>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("💤 Rest (heal 10 HP)", use_container_width=True, disabled=gs.get("rest_used", False)):
            p["hp"] = min(p["max_hp"], p["hp"] + 10)
            add_log(gs, "🔥 Rested. +10 HP.")
            gs["rest_used"] = True
            st.rerun()
    with c2:
        if st.button("🔍 Search the camp", use_container_width=True, disabled=gs.get("rest_searched", False)):
            loot = roll_loot(gs["rng"], "poor")
            p["gold"] += loot["gold"]
            add_log(gs, f"🔍 Found {loot['gold']} gold.")
            if loot["item"]:
                add_to_inventory(gs, loot["item"])
                add_log(gs, f"🎒 Found: {loot['item']['name']}")
            gs["rest_searched"] = True
            st.rerun()
    with c3:
        if st.button("➤ Move on", use_container_width=True, type="primary"):
            advance_node(gs)
            st.rerun()

def render_fork(gs):
    node = gs["current_node"]
    # Narrative fork intro — ties what came before to the choice ahead
    prev_nodes_done = gs["current_node_idx"]
    if prev_nodes_done <= 3:
        fork_preamble = (
            "The upper halls are behind you. The fighting and the finding and whatever else "
            "passed for the first stretch of this descent. Now the dungeon offers you a choice, "
            "which is unusual. Dungeons don't typically negotiate. Pay attention to what that means."
        )
    else:
        fork_preamble = (
            "You've come far enough that the dungeon has begun to feel specific. Less like a building, "
            "more like an argument someone never finished. Two passages. Two different directions "
            "that argument is willing to take. You get one. The other becomes hypothetical."
        )
    st.markdown("### 🛤️ The Path Splits")
    st.markdown(
        f"<div class='event-box'>{fork_preamble}</div>",
        unsafe_allow_html=True
    )
    st.markdown("---")
    options = node.get("fork_options", [])
    cols = st.columns(len(options))
    for i, biome_key in enumerate(options):
        b = BIOMES.get(biome_key, {})
        # Per-biome fork flavour
        fork_flavours = {
            "fungal_caverns": "The air here smells of earth and something sweet that you haven't decided is good yet.",
            "cursed_chapel": "Faint singing. You cannot identify the song. You are not sure it wants to be identified.",
            "ash_wastes": "Heat. The remnants of something immense. Whatever it was, it lost.",
            "goblin_tunnels": "High voices, distant. Something being argued about with great enthusiasm.",
            "ruined_keep": "The smell of iron and old stone. Familiar. Comfortable. You distrust this.",
        }
        flavour = fork_flavours.get(biome_key, "")
        with cols[i]:
            st.markdown(
                f"<div class='stat-card' style='min-height:120px;'>"
                f"<h3>{b.get('emoji','?')} {b.get('name','???')}</h3>"
                f"<div style='color:#8b949e; font-style:italic; font-size:0.9em;'>{flavour}</div>"
                f"</div>",
                unsafe_allow_html=True
            )
            if st.button(f"➤ Take this path", key=f"fork_{i}", use_container_width=True):
                expand_act2(gs, biome_key)
                add_log(gs, f"➤ Descended into: {b.get('name','???')}")
                advance_node(gs)
                st.rerun()

def render_secret(gs):
    node = gs["current_node"]
    p = gs["player"]
    rng = gs["rng"]
    st.markdown("### 🗝️ Hidden Passage")
    st.markdown(
        "<div class='event-box'>A draft of cold air where there should be wall. You press against the stone "
        "and it gives. A passage no one has used in a long, long time.<br><br>"
        "There is something at the end of it. There is always something at the end of these.</div>",
        unsafe_allow_html=True
    )
    if not gs.get("secret_taken"):
        c1, c2 = st.columns(2)
        with c1:
            if st.button("📦 Open the cache (elite loot)", use_container_width=True):
                loot = roll_loot(rng, "elite")
                if has_relic(gs, "gold_boost"):
                    loot["gold"] = int(loot["gold"] * 1.5)
                p["gold"] += loot["gold"]
                add_log(gs, f"💰 Hidden cache: +{loot['gold']} gold.")
                if loot["item"]:
                    add_to_inventory(gs, loot["item"])
                    add_log(gs, f"🎒 Found: {loot['item']['name']}")
                if loot["weapon"]:
                    gs["flags"]["pending_weapon"] = loot["weapon"]["name"]
                    add_log(gs, f"⚔️ Weapon: {loot['weapon']['name']}!")
                gs["secret_taken"] = True
                st.rerun()
        with c2:
            if st.button("🏺 Take the relic instead", use_container_width=True):
                available = [r for r in RELICS if r["name"] not in p["relics"]]
                if available:
                    relic = rng.choice(available)
                    p["relics"].append(relic["name"])
                    apply_relic_passive(gs, relic)
                    add_log(gs, f"🏺 Found relic: {relic['name']}")
                else:
                    p["gold"] += 30
                    add_log(gs, "🏺 No new relics. +30 gold instead.")
                gs["secret_taken"] = True
                st.rerun()
    else:
        if st.button("Continue →", type="primary"):
            advance_node(gs)
            st.rerun()

def render_merchant_node(gs):
    st.markdown("### 🏪 A Merchant's Stall")
    st.markdown(
        "<div class='event-box'>A figure waits behind a board laid out with goods. They smile. "
        "It is the smile of someone who has watched many adventurers spend their last coin.</div>",
        unsafe_allow_html=True
    )
    if not gs.get("shop_items"):
        open_shop(gs)
    render_shop(gs)

def render_treasure(gs):
    p = gs["player"]
    rng = gs["rng"]
    st.markdown("### 📦 A Treasure Chamber")
    st.markdown("<div class='event-box'>Nothing guards it. That alone should worry you.</div>", unsafe_allow_html=True)
    if not gs.get("event_resolved"):
        if st.button("Open the chest"):
            loot = roll_loot(rng, "good")
            p["gold"] += loot["gold"]
            add_log(gs, f"💰 +{loot['gold']} gold")
            if loot["item"]:
                add_to_inventory(gs, loot["item"])
                add_log(gs, f"🎒 {loot['item']['name']}")
            if loot["weapon"]:
                gs["flags"]["pending_weapon"] = loot["weapon"]["name"]
            gs["event_resolved"] = True
            st.rerun()
    else:
        if st.button("Continue →", type="primary"):
            advance_node(gs)
            st.rerun()

def render_act_transition(gs):
    """Show a full-screen-style transition card between acts. Returns True if still showing."""
    act = gs["act"]
    node = gs.get("current_node", {})
    biome_key = node.get("biome")

    if act == 2:
        text = ACT_TRANSITIONS[2].get(biome_key or "ruined_keep", ACT_TRANSITIONS[2]["ruined_keep"])
        title = "— DEEPER —"
    else:
        text = ACT_TRANSITIONS[3]
        title = "— THE FINAL STRETCH —"

    st.markdown(f"""
<div class='event-box' style='border-color:#58a6ff; text-align:center; padding:28px;'>
<div style='font-size:0.8em; letter-spacing:0.25em; color:#8b949e; margin-bottom:12px;'>ACT {act}</div>
<div style='font-size:1.3em; letter-spacing:0.1em; color:#c9d1d9; margin-bottom:20px;'>{title}</div>
<div style='font-size:1em; color:#8b949e; line-height:1.8; max-width:560px; margin:0 auto;'>{text}</div>
</div>
""", unsafe_allow_html=True)
    if st.button("Press on →", type="primary", use_container_width=False):
        gs["show_act_transition"] = False
        st.rerun()
    return True


def render_scene(gs):
    node = gs.get("current_node")
    if not node:
        st.write("The dungeon stretches on...")
        if st.button("Continue"):
            advance_node(gs)
            st.rerun()
        return

    # ── Act transition screen ──────────────────────────────────────────────
    if gs.get("show_act_transition"):
        render_act_transition(gs)
        return

    biome_key = node.get("biome")
    b = BIOMES.get(biome_key, {}) if biome_key else {}

    # ── Header bar ────────────────────────────────────────────────────────
    total = len(gs["run_nodes"])
    idx = gs["current_node_idx"] + 1
    act_label = f"Act {gs['act']}"
    biome_label = f"{b.get('emoji','')} {b.get('name','')}" if b else ""
    st.markdown(
        f"<div class='act-banner'><b>{biome_label}</b> · <i>{act_label}</i> · "
        f"<span style='color:#8b949e;'>Node {idx}/{total}</span></div>",
        unsafe_allow_html=True
    )

    render_pending_weapon(gs)

    # ── Class opening (first node only) ───────────────────────────────────
    if gs.get("show_class_opening") and gs["current_node_idx"] == 0:
        class_key = gs["player"].get("class_key", "iron_warden")
        opening = CLASS_OPENINGS.get(class_key, "")
        if opening:
            st.markdown(
                f"<div class='event-box' style='border-color:#30363d; color:#8b949e;'>{opening}</div>",
                unsafe_allow_html=True
            )
        gs["show_class_opening"] = False

    # ── Biome flavour + node approach (shown until dismissed, then collapses) ──
    ntype = node["type"]
    if not gs.get("node_intro_dismissed") and ntype not in ("fork",):
        flavour = get_biome_flavour(gs, biome_key or "ruined_keep")
        approach = get_node_approach(gs, node)
        intro_lines = [l for l in [flavour, approach] if l]
        if intro_lines:
            st.markdown(
                "<div style='color:#8b949e; font-style:italic; font-size:0.92em; "
                "border-left:3px solid #30363d; padding-left:12px; margin-bottom:12px;'>"
                + "<br>".join(intro_lines) + "</div>",
                unsafe_allow_html=True
            )

    # ── Dispatch to node renderer ──────────────────────────────────────────
    if ntype in ("combat", "elite_combat", "boss"):
        if not gs.get("combat_state"):
            start_combat(gs, node)
        render_combat(gs)
    elif ntype == "event":
        render_event(gs)
    elif ntype == "rest":
        render_rest(gs)
    elif ntype == "treasure":
        render_treasure(gs)
    elif ntype == "merchant":
        render_merchant_node(gs)
    elif ntype == "fork":
        render_fork(gs)
    elif ntype == "secret":
        render_secret(gs)
    elif ntype == "ending":
        gs["screen"] = "ending"
        gs["ending_key"] = determine_ending(gs)
        st.rerun()
    else:
        st.write(f"Unknown node: {ntype}")
        if st.button("Continue"):
            advance_node(gs)
            st.rerun()

def render_ending(gs):
    p = gs["player"] or {}
    ekey = gs.get("ending_key") or determine_ending(gs)
    flags = gs.get("flags", {})

    endings = {
        "heroic_victory": {
            "title": "THE DUNGEON FALLS",
            "color": "#4eca8b",
            "text": "You emerged from Aethermoor with your blade red and your spirit unbroken. The dungeon will remember this day, and so will the few who survive to tell of it. The light hits different when you have earned it. You walk into the dawn and the dawn, for once, has the decency not to look away.",
        },
        "corrupted_power": {
            "title": "WHAT HAVE YOU BECOME",
            "color": "#a855f7",
            "text": "You defeated the dungeon's worst. The price was your humanity. The shadows welcome you home like an old friend who has been waiting patiently in the back of every mirror. Your eyes no longer hold light. People will cross streets to avoid you. They will be right to.",
        },
        "escape_survival": {
            "title": "NARROWLY ALIVE",
            "color": "#d29922",
            "text": "Battered, barely breathing, you dragged yourself out. Not a victory. Not exactly a defeat. A cautionary tale you'll tell no one — not because they wouldn't believe you, but because you can't quite face what you did to survive. The dungeon remains. So do you. For now.",
        },
        "tragic_failure": {
            "title": "DARKNESS CLAIMS ANOTHER",
            "color": "#ef4444",
            "text": "Your torch guttered. Your weapons failed. The dungeon adds your bones to a collection it has been curating for a long time. Every dungeon needs a cautionary tale. This run, you were it. Somewhere above, the wind moves a tavern sign and someone almost remembers your name.",
        },
        "true_ending": {
            "title": "THE SECRET OF AETHERMOOR",
            "color": "#ffd700",
            "text": "With the forbidden tome and the relic shard aligned, the dungeon reveals what it truly is: not a ruin, but a gate. The walls were never walls. The bosses were never bosses — they were locks, and you had the key in your hands the whole time without knowing.\n\nYou do not escape Aethermoor. You open it. What lies on the other side has been waiting for someone exactly like you. The next chapter is unwritten. The pen, when you find it, will not be made of any material you recognize.",
        },
    }
    e = endings.get(ekey, endings["escape_survival"])

    st.markdown(
        f"<div class='ending-box' style='border-color:{e['color']};'>"
        f"<h1 style='color:{e['color']}; letter-spacing:0.08em;'>{e['title']}</h1>"
        f"<p style='font-size:1.05em; line-height:1.7;'>{e['text']}</p>"
        "</div>",
        unsafe_allow_html=True
    )

    st.markdown("### 📊 Run Summary")
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Class", p.get("class_name", "—"))
    with c2: st.metric("Kills", p.get("kills", 0))
    with c3: st.metric("Gold", p.get("gold", 0))
    with c4: st.metric("HP at End", f"{max(0, p.get('hp', 0))}/{p.get('max_hp', 0)}")

    c5, c6, c7, c8 = st.columns(4)
    with c5: st.metric("Corruption", flags.get("corruption", 0))
    with c6: st.metric("Fate", flags.get("fate", 0))
    with c7: st.metric("Relics", len(p.get("relics", [])))
    with c8: st.metric("Nodes Cleared", gs.get("current_node_idx", 0))

    if ekey == "true_ending":
        st.success("🌟 You unlocked the **True Ending**. The gate is open.")
    elif ekey == "corrupted_power":
        st.warning("☠️ Corrupted ending. Try staying purer next time — or don't.")

    st.markdown("---")
    cc1, cc2, _ = st.columns([1, 1, 2])
    with cc1:
        if st.button("🔄 New Run", type="primary", use_container_width=True):
            init_state()
            st.rerun()
    with cc2:
        if st.button("🏠 Title Screen", use_container_width=True):
            init_state()
            st.rerun()

# =====================================================================
# MAIN
# =====================================================================

def main():
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    if "gs" not in st.session_state:
        init_state()
    gs = st.session_state["gs"]

    if gs["screen"] != "title":
        render_sidebar(gs)

    screen = gs["screen"]
    if screen == "title":
        render_title()
    elif screen == "class_select":
        render_class_select(gs)
    elif screen == "game":
        render_scene(gs)
    elif screen == "ending":
        render_ending(gs)
    else:
        st.write("Unknown screen state. Resetting...")
        init_state()
        st.rerun()

if __name__ == "__main__":
    main()