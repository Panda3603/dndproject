from textwrap import wrap
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from flask import Flask, render_template, jsonify, request, send_file
import smtplib
from dotenv import load_dotenv
from email.mime.text import MIMEText
import random
import os
script_dir = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
application = app

def load_race_name_pool(race, folder_path=None):
    if folder_path is None:
        folder_path = os.path.join(os.path.dirname(__file__), "race_names")

    normalized_race = race.lower().replace(" ", "").replace("-", "")
    print(f"[DEBUG 1] Race passed to name loader: '{race}'")
    print(f"[DEBUG 2] Normalized race name: '{normalized_race}'")

    first_path = os.path.join(folder_path, f"{normalized_race}_first.txt")
    last_path = os.path.join(folder_path, f"{normalized_race}_last.txt")
    
    print(f"[DEBUG 3] Checking for files:")
    print(f"  First: {first_path}")
    print(f"  Last: {last_path}")
    print(f"[DEBUG 4] First exists? {os.path.exists(first_path)}")
    print(f"[DEBUG 5] Last exists? {os.path.exists(last_path)}")

    if not os.path.exists(first_path) or not os.path.exists(last_path):
        print("[DEBUG 6] One or both files missing. Falling back to generic names.")
        return (
            ["Arin", "Lira", "Thorne", "Kara", "Dain", "Mira", "Jarek", "Sylva"],
            ["Ironwood", "Duskblade", "Stormborn", "Brightflame", "Shadowstep", "Frostbane"]
        )

    with open(first_path, 'r', encoding='utf-8') as f:
        first_names = [line.strip() for line in f if line.strip()]
    
    with open(last_path, 'r', encoding='utf-8') as f:
        last_names = [line.strip() for line in f if line.strip()]
    
    return first_names, last_names
    

# Sample data sets
races = [
    "Dragonborn", "Dwarf", "Elf", "Gnome", "Half-Elf", "Half-Orc", "Halfling", "Human", "Tiefling",
    "Aarakocra", "Aasimar", "Bugbear", "Centaur", "Firbolg", "Genasi", "Gith", "Goblin", "Goliath",
    "Hobgoblin", "Kenku", "Kobold", "Leonin", "Lizardfolk", "Minotaur", "Orc", "Satyr", "Tabaxi",
    "Tortle", "Triton", "Yuan-ti Pureblood", "Warforged", "Changeling", "Kalashtar", "Shifter",
    "Vedalken", "Loxodon", "Simic Hybrid", "Verdan", "Owlin", "Harengon"
]

classes = ["Fighter", "Wizard", "Rogue", "Cleric", "Ranger", "Paladin", "Bard"]
subclasses = {
    "Fighter": ["Champion", "Battle Master", "Eldritch Knight"],
    "Wizard": ["Evocation", "Illusion", "Necromancy"],
    "Rogue": ["Thief", "Assassin", "Arcane Trickster"],
    "Cleric": ["Life Domain", "Light Domain", "War Domain"],
    "Ranger": ["Hunter", "Beast Master"],
    "Paladin": ["Oath of Devotion", "Oath of Vengeance"],
    "Bard": ["College of Lore", "College of Valor"]
}
genders = ["Male", "Female", "Non-binary"]
backgrounds = ["Acolyte", "Soldier", "Noble", "Criminal", "Hermit", "Folk Hero"]
themes = [
    {"name": "Warrior's Valor", "colors": ["#A52A2A", "#DAA520", "#8B4513"]},
    {"name": "Shadowblade Legacy", "colors": ["#2F4F4F", "#708090", "#000000"]},
    {"name": "Arcane Whispers", "colors": ["#6A5ACD", "#8A2BE2", "#4B0082"]},
    {"name": "Nature's Wrath", "colors": ["#228B22", "#556B2F", "#8FBC8F"]}
]
hair_colors = ["jet black", "silver", "fiery red", "golden blond", "deep brown", "ash gray", "blue-tinted"]
eye_colors = ["emerald green", "icy blue", "amber", "violet", "hazel", "stormy gray", "piercing black"]
body_mods = ["a nose ring", "a lip piercing", "a set of ear cuffs", "an intricate tattoo sleeve", "a ritualistic scar", "a hidden brand"]
clothing_details = [
    "a cloak patterned with falling stars", 
    "boots stitched with runes", 
    "a belt adorned with teeth of beasts", 
    "a robe that shifts in color",
    "a scarf woven with moonlight thread"
]

hit_dice = {
    "Barbarian": 12,
    "Fighter": 10, "Paladin": 10, "Ranger": 10,
    "Bard": 8, "Cleric": 8, "Druid": 8, "Monk": 8, "Rogue": 8, "Warlock": 8,
    "Sorcerer": 6, "Wizard": 6
}
   
def generate_stats(level):
    stats = {}
    for stat in ["STR", "DEX", "CON", "INT", "WIS", "CHA"]:
        rolls = sorted([random.randint(1, 6) for _ in range(4)])[1:]
        stats[stat] = sum(rolls) + (level // 2)
    return stats

# Tiefling specific appearance
def generate_tiefling_appearance():
    skin_colors = [
        "obsidian black", "lavender-toned", "deep crimson", "dusky violet",
        "ashen gray", "burnt umber", "steel gray", "cracked magma-like", 
        "coal-dark", "amethyst-toned"
    ]

    eye_descriptions = [
        "eyes that burn like embers of Avernus",
        "glowing silver eyes, touched by the Silver Void",
        "molten gold eyes from the Nine Hells",
        "twin void-black eyes that reflect no light",
        "eyes flickering with blue flame from the Plane of Fire",
        "green-glowing eyes reminiscent of the Shadowfell",
        "lidless fiery orange eyes, predatory and intense",
        "pale blue eyes that chill the soul",
        "star-like eyes that shimmer with distant light"
    ]

    horn_styles = [
        "ram-like horns etched with infernal runes",
        "spiraled horns like a crown",
        "jagged horns, chipped from battle",
        "short, forward-curving horns",
        "flame-shaped horns twisted like stone",
        "blade-like horns polished to a shine",
        "one horn cracked or broken — a mark of rebellion",
        "horns engraved with celestial constellations"
    ]

    tattoos = [
        "arcane glyphs trailing across their back",
        "a tattoo of broken chains up their arm",
        "infernal verses inked from jaw to collarbone",
        "burning chain patterns looped around their limbs",
        "sigils of old pacts glowing faintly",
        "a fiendish contract torn in half, inked across their chest",
        "celestial names crossed out in infernal script"
    ]

    scars = [
        "a charred ritual brand beneath one eye",
        "a faded scar slicing through one eyebrow",
        "a missing horn tip, sheared in defiance",
        "burns from pact-severing flames",
        "arcane branding from an infernal rite"
    ]

    clothing = [
        "a high-collared coat singed at the hem",
        "tattered robes enchanted for flame resistance",
        "layered leather armor with scorched silver filigree",
        "a cloak clasped with a pentagram-shaped brooch",
        "sleeveless garb swaying like smoke",
        "boots partially melted and reinforced with demonhide"
    ]

    # Random selection
    skin = random.choice(skin_colors)
    eyes = random.choice(eye_descriptions)
    horns = random.choice(horn_styles)
    tattoo = random.choice(tattoos)
    scar = random.choice(scars)
    clothes = random.choice(clothing)

    # Final description
    description = (
        f"This Tiefling has {skin} skin and {horns}. "
        f"They have {eyes}, and {tattoo}. "
        f"{scar.capitalize()}, and they wear {clothes}."
    )

    return description

# Example use
print(generate_tiefling_appearance())

def generate_appearance(race, theme_name): 
    if race == "Tiefling":
        return generate_tiefling_appearance()
    
    
    elif race == "Dragonborn":
        scale_colors = ["bronze", "emerald", "obsidian", "ruby red", "sapphire blue", "glacial white", "burnished gold"]
        build = random.choice(["broad-shouldered", "towering", "serpentine", "muscle-ridged"])
        tail_detail = random.choice(["a ridged tail tipped in steel", "a thick tail used for balance", "a scaled tail adorned with ritual beads"])
        clothing = random.choice(["a battle-worn sash across the chest", "a tunic split for movement", "an armored cloak pinned with a claw-shaped clasp"])
        return f"has {random.choice(scale_colors)} scales, a {build} frame, {tail_detail}, and wears {clothing} reflecting the {theme_name} theme."
    
    elif race == "Elf":
        skin_tones = ["porcelain-pale", "sun-kissed bronze", "silver-hued", "moonlight-pale"]
        eyes = ["amber eyes that seem to pierce the veil", "glowing green eyes like a forest spirit", "stormy blue eyes full of memory"]
        hair_styles = ["braided platinum hair", "long silken black hair", "wavy auburn hair with leaf ornaments"]
        clothing = ["a flowing robe stitched with constellations", "a moss-lined cloak", "a tunic woven from spider silk"]
        return f"has {random.choice(skin_tones)} skin, {random.choice(eyes)}, {random.choice(hair_styles)}, and wears {random.choice(clothing)} reflecting the {theme_name} theme."
        
    elif race == "Dwarf":
        beard_styles = ["a thick braided beard wrapped in gold rings", "a forked beard stained with soot", "a trimmed beard with hidden runes"]
        skin_tones = ["ruddy skin", "stone-gray complexion", "weathered tan skin"]
        clothing = ["a smith's apron engraved with clan markings", "a reinforced vest of chainmail and leather", "a cloak lined with wolf fur"]
        return f"has {random.choice(skin_tones)}, {random.choice(beard_styles)}, and wears {random.choice(clothing)} reflecting the {theme_name} theme."
        
    elif race == "Gnome":
        skin_tones = ["rosy-cheeked", "light olive", "nut-brown"]
        eyes = ["bright sapphire eyes", "twinkling green eyes", "curious hazel eyes"]
        hair_styles = ["a frizzled mess of chestnut curls", "neatly parted silver hair", "a shocking teal mohawk"]
        clothing = ["a vest full of gear loops", "patched robes with arcane symbols", "boots with spring-loaded heels"]
        return f"has {random.choice(skin_tones)} skin, {random.choice(eyes)}, {random.choice(hair_styles)}, and wears {random.choice(clothing)} reflecting the {theme_name} theme."
        
    elif race == "Halfling":
        features = ["freckles scattered across the nose", "a perpetual grin", "dirt-smudged cheeks"]
        hair_styles = ["curly sandy hair", "dark brown hair tied in a ribbon", "short copper-red hair"]
        clothing = ["a tunic with too many pockets", "a scarf that doubles as a sling", "an oversized waistcoat"]
        return f"has {random.choice(features)}, {random.choice(hair_styles)}, and wears {random.choice(clothing)} reflecting the {theme_name} theme."
        
    elif race == "Half-Elf":
        features = ["a sharp jawline softened by kindness", "mismatched eyes", "ears subtly pointed"]
        skin_tones = ["lightly tanned", "peach-toned", "faintly silvered"]
        hair_styles = ["straight golden locks", "shoulder-length raven hair", "loose curls dyed with streaks of blue"]
        clothing = ["an elegant coat with family crests", "a travel-worn cape that hints at nobility", "robes sewn with dual heritage motifs"]
        return f"has {random.choice(skin_tones)} skin, {random.choice(features)}, {random.choice(hair_styles)}, and wears {random.choice(clothing)} reflecting the {theme_name} theme."
        
    elif race == "Half-Orc":
        features = ["a broken tusk from battle", "a jagged scar over one eyebrow", "green-gray skin weathered by conflict"]
        build = ["massive shoulders", "a towering frame", "a powerfully thick neck"]
        clothing = ["fur-lined leathers", "a war kilt made from beast hide", "a chain-wrapped gauntlet over one arm"]
        return f"has {random.choice(features)}, {random.choice(build)}, and wears {random.choice(clothing)} reflecting the {theme_name} theme."
        
    elif race == "Human":
        skin_tones = ["light caramel", "sun-bronzed", "pale freckled", "olive-toned"]
        eyes = ["amber-flecked", "ice blue", "hazel-green"]
        hair = ["short-cropped", "long and braided", "shaved at the sides"]
        clothing = ["a doublet with noble trim", "a threadbare cloak stitched by hand", "a surcoat bearing a faded sigil"]
        return f"has {random.choice(skin_tones)} skin, {random.choice(eyes)} eyes, {random.choice(hair)} hair, and wears {random.choice(clothing)} reflecting the {theme_name} theme."

    elif race == "Aarakocra":
        feather_colors = ["snow-white", "fiery red and gold", "storm-gray", "deep jungle green"]
        eye_types = ["hawk-like yellow eyes", "piercing black eyes", "sun-bright eyes with no pupil"]
        clothing = ["a sash covered in tribal beads", "light leather harnesses", "a mantle made of bones and feathers"]
        return f"has {random.choice(feather_colors)} feathers, {random.choice(eye_types)}, and wears {random.choice(clothing)} reflecting the {theme_name} theme."
    
    elif race == "Kenku":
        skin = "feathers in soot-black and streaked rust-red"
        eyes = "gleaming black eyes full of mimicry's mischief"
        mod = "a series of claw-etched glyphs along their wings"
        clothes = "a patchwork cloak stitched from stolen banners"
        return f"has {skin}, {eyes}, {mod}, and wears {clothes} reflecting the {theme_name} theme."
    
    elif race == "Kobold":
        skin = "scale patterns of dull copper and ember-flecked brown"
        eyes = "narrow slits glowing faintly with cunning"
        mod = "a crude earring looped through one frilled ear"
        clothes = "a harness of leather scraps adorned with tiny charms"
        return f"has {skin}, {eyes}, {mod}, and wears {clothes} reflecting the {theme_name} theme."

    elif race == "Leonin":
        fur = "golden fur streaked with storm-gray around the muzzle"
        eyes = "amber eyes that pierce with pride"
        mod = "braided beads and claws woven into their mane"
        clothes = "a warcloak of lionhide and carved bone toggles"
        return f"has {fur}, {eyes}, {mod}, and wears {clothes} reflecting the {theme_name} theme."

    elif race == "Lizardfolk":
        skin = "scales of swamp green with hints of ochre"
        eyes = "cold reptilian eyes that never blink"
        mod = "a ritual scar branded across their chest"
        clothes = "strips of hide armor held by bone clasps"
        return f"has {skin}, {eyes}, {mod}, and wears {clothes} reflecting the {theme_name} theme."
    
    elif race == "Minotaur":
        fur = "coarse russet-brown fur over a stone-carved frame"
        eyes = "burning red eyes under a heavy brow"
        mod = "ceremonial piercings along both nostrils"
        clothes = "shoulder armor forged from shattered axes"
        return f"has {fur}, {eyes}, {mod}, and wears {clothes} reflecting the {theme_name} theme."

    elif race == "Orc":
        skin = "mossy green skin marred with battle scars"
        eyes = "steel-gray eyes hardened by conflict"
        mod = "a war tattoo crossing their throat"
        clothes = "a chest harness decorated with bones of past foes"
        return f"has {skin}, {eyes}, {mod}, and wears {clothes} reflecting the {theme_name} theme."

    elif race == "Satyr":
        fur = "chestnut-brown fur with a silver-streaked tail"
        eyes = "bright hazel eyes sparkling with mischief"
        mod = "rings looped through one curled horn"
        clothes = "a musician’s tunic covered in wine-stained embroidery"
        return f"has {fur}, {eyes}, {mod}, and wears {clothes} reflecting the {theme_name} theme."

    elif race == "Tabaxi":
        fur = "sleek spotted fur patterned like jungle shadows"
        eyes = "sharp emerald eyes that miss nothing"
        mod = "an ornate nose ring from a distant tribe"
        clothes = "light wraps sewn with golden feline patterns"
        return f"has {fur}, {eyes}, {mod}, and wears {clothes} reflecting the {theme_name} theme."

    elif race == "Tortle":
        skin = "mottled teal skin with a ridged shell of brown and tan"
        eyes = "gentle eyes deep as tidepools"
        mod = "barnacle-like carvings along their forearms"
        clothes = "a weathered sash slung over one shoulder, heavy with charms"
        return f"has {skin}, {eyes}, {mod}, and wears {clothes} reflecting the {theme_name} theme."

    elif race == "Triton":
        skin = "pearl-blue skin with hints of coral and shimmer"
        eyes = "sea-green eyes that pulse like the tide"
        mod = "gill markings traced with bioluminescent ink"
        clothes = "scaled mail glistening with oceanic hues"
        return f"has {skin}, {eyes}, {mod}, and wears {clothes} reflecting the {theme_name} theme."
    
    elif race == "Aasimar":
        skin = "radiant skin that shimmers faintly in the light"
        eyes = "pupil-less eyes glowing silver or gold"
        mod = "a faint celestial sigil glowing beneath the collarbone"
        clothes = "robes threaded with starlight and divine script"
        return f"has {skin}, {eyes}, {mod}, and wears {clothes} reflecting the {theme_name} theme."

    elif race == "Bugbear":
        fur = "patchy fur in muddied gray and tawny shades"
        eyes = "small, amber eyes under a heavy brow"
        mod = "a crude iron ring pierced through one ear"
        clothes = "strapped-together hides still bearing old battle stains"
        return f"has {fur}, {eyes}, {mod}, and wears {clothes} reflecting the {theme_name} theme."

    elif race == "Centaur":
        skin = "bronzed upper skin atop a dappled equine lower body"
        eyes = "keen brown eyes with a glint of wilderness"
        mod = "leather cords braided into the tail and mane"
        clothes = "a chest harness fitted with pouches and tribal carvings"
        return f"has {skin}, {eyes}, {mod}, and wears {clothes} reflecting the {theme_name} theme."

    elif race == "Firbolg":
        skin = "earthy blue-gray skin with moss-like undertones"
        eyes = "soft violet eyes that glow gently in dim light"
        mod = "floral tattoos blooming across broad shoulders"
        clothes = "a druidic cloak woven from forest leaves and bark"
        return f"has {skin}, {eyes}, {mod}, and wears {clothes} reflecting the {theme_name} theme."

    elif race == "Genasi":
        skin = "elementally touched skin — cracked stone, flowing water, flickering flame, or swirling wind patterns"
        eyes = "elemental eyes devoid of pupils, glowing with inner energy"
        mod = "veins or hair that spark, ripple, or drift with their elemental type"
        clothes = "attire shaped from raw elemental materials like obsidian, mist-thread, or charcloth"
        return f"has {skin}, {eyes}, {mod}, and wears {clothes} reflecting the {theme_name} theme."

    elif race == "Goblin":
        skin = "sickly green skin covered in scrapes and smudges"
        eyes = "wide yellow eyes brimming with mischief"
        mod = "an oversized nose ring or bone needle through the ear"
        clothes = "rag-tag leathers and belts filled with stolen trinkets"
        return f"has {skin}, {eyes}, {mod}, and wears {clothes} reflecting the {theme_name} theme."

    elif race == "Goliath":
        skin = "stone-like gray skin marbled with darker patches"
        eyes = "ice-blue or pale green eyes, sharp and assessing"
        mod = "tribal tattoos that trace strength and victory"
        clothes = "minimalist furs or armor etched with clan symbols"
        return f"has {skin}, {eyes}, {mod}, and wears {clothes} reflecting the {theme_name} theme."

    elif race == "Hobgoblin":
        skin = "deep crimson or slate-colored skin stretched taut over wiry muscle"
        eyes = "narrow golden eyes brimming with discipline"
        mod = "military brands scorched into one shoulder"
        clothes = "rigid uniforms trimmed in rank-bands and polished steel"
        return f"has {skin}, {eyes}, {mod}, and wears {clothes} reflecting the {theme_name} theme."

    elif race == "Warforged":
        plating = "worn steel plating engraved with arcane sigils"
        eyes = "glowing blue or red eye-lenses built into their helm-like head"
        mod = "runic cores visible through chest slats"
        clothes = "utility wraps and reinforced belts built into their frame"
        return f"has {plating}, {eyes}, {mod}, and wears {clothes} reflecting the {theme_name} theme."

    elif race == "Yuan-ti Pureblood":
        skin = "pale skin with serpent scale patches across the neck and arms"
        eyes = "slitted emerald or gold eyes that never blink"
        mod = "fang tattoos and subtle forked tongue movements"
        clothes = "silken robes layered in serpentine patterns and jeweled cuffs"
        return f"has {skin}, {eyes}, {mod}, and wears {clothes} reflecting the {theme_name} theme."

    elif race == "Changeling":
        skin = "smooth pale-gray skin shifting subtly with emotion"
        eyes = "solid color eyes — black, white, or violet — without iris"
        mod = "a barely perceptible ripple beneath their features"
        clothes = "adaptive clothing that mirrors nearby styles and cultures"
        return f"has {skin}, {eyes}, {mod}, and wears {clothes} reflecting the {theme_name} theme."

    elif race == "Kalashtar":
        skin = "lightly glowing skin with a faint ethereal shimmer"
        eyes = "serene eyes lit with a quiet inner light"
        mod = "ghostly wisps trailing from their hair when calm or focused"
        clothes = "robes or armor stylized with dream-motif embroidery"
        return f"has {skin}, {eyes}, {mod}, and wears {clothes} reflecting the {theme_name} theme."

    elif race == "Shifter":
        features = "feral features — elongated canines, tufted ears, and claw-like nails"
        eyes = "animalistic eyes that shift hue with emotion"
        mod = "patches of fur or bristles along arms and back"
        clothes = "clothing reinforced with stretchable leather, fit for rapid movement"
        return f"has {features}, {eyes}, {mod}, and wears {clothes} reflecting the {theme_name} theme."
        
    
    # Fallback for races not yet implemented
    else:
        hair = random.choice(hair_colors)
        eyes = random.choice(eye_colors)
        mod = random.choice(body_mods)
        clothing = random.choice(clothing_details)
        return f"has {hair} hair, {eyes} eyes, {mod}, and wears {clothing} reflecting the {theme_name} theme."

def generate_backstory(name, race, char_class, background, appearance, personal_item):
    backstory_openings = [
        "Born of the {race} bloodline, {name} defied what was expected of them and chose the path of the {char_class}.",
        "Where most {race}s cling to tradition, {name} pursued the unorthodox life of a {char_class}.",
        "{name} never fit the mold of a typical {race} — their heart beat to the rhythm of the {char_class}.",
        "Among the {race}, it’s rare to find a {char_class}. Rarer still is one as driven as {name}.",
        "The {char_class}'s path is not common for a {race}, but {name} was never one for common roads.",
        "{name} was shaped by {race} roots, but the calling of the {char_class} reshaped their destiny.",
        "Though born a {race}, {name} felt a spark — a pull toward the way of the {char_class}.",
        "The traditions of the {race}s taught discipline, but {name} found freedom in the chaos of a {char_class}'s journey.",
        "{name}'s kin walked the path of predictability. They chose another — one forged in the fires of the {char_class}.",
        "While their blood whispered the old ways of the {race}, {name} listened instead to the beckoning of the {char_class}."
    ]

    events = [
        "was exiled from their homeland",
        "survived a betrayal within their guild",
        "was chosen by a mysterious prophecy",
        "endured trials in a cursed forest",
        "escaped an ancient beast’s wrath",
        "lost their voice to a magical pact"
    ]
    
    goals = [
        "seeks to reclaim their lost honor",
        "wants to uncover a forbidden truth",
        "hopes to reunite with their family",
        "aims to bring peace to their homeland",
        "is on a quest for self-discovery",
        "protects those who cannot protect themselves"
    ]
    
    quirks = [
        "recites lullabies in battle",
        "collects feathers from every journey",
        "talks to their weapon as if it were alive",
        "has a deep fear of mirrors",
        "writes messages on stones and leaves them behind",
        "wears mismatched gloves intentionally"
    ]

    # Pick and format dynamic intro
    opening = random.choice(backstory_openings).format(name=name, race=race, char_class=char_class)
    event = random.choice(events)
    goal = random.choice(goals)
    quirk = random.choice(quirks)

    return (
        f"{opening} Once a {background.lower()}, they {event}. "
        f"Their appearance {appearance} marks them as someone unforgettable. "
        f"They carry {personal_item}. This character {goal} and {quirk}."
    )

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route("/generate")
def generate_character():
    level = int(request.args.get("level", 1))
    personal_item = request.args.get("personal_item", "a mysterious token with a forgotten past")
    race = random.choice(races)
    char_class = random.choice(classes)
    subclass = random.choice(subclasses[char_class])
    gender = random.choice(genders)
    background = random.choice(backgrounds)
    theme = random.choice(themes)
    appearance = generate_appearance(race, theme["name"])
    stats = generate_stats(level)
    con_score = stats.get("Constitution", 10)
    con_mod = (con_score - 10) // 2        
    first_names, last_names = load_race_name_pool(race)
    full_name = f"{random.choice(first_names)} {random.choice(last_names)}"
    backstory = generate_backstory(full_name, race, char_class, background, appearance, personal_item)

    hd = hit_dice.get(char_class, 8)  # fallback to d8

    # Level 1: Max die + CON mod
    base_hp = hd + con_mod

    # Each level after 1:
    worst_hp = base_hp + (level - 1) * (1 + con_mod)
    best_hp = base_hp + (level - 1) * (hd + con_mod)

    # Prevent negatives
    worst_hp = max(worst_hp, level)

    hp_range = f"{worst_hp}–{best_hp}"
    
    #Generate max lvel preview (12)
    max_level = 12
    max_worst_hp = base_hp + (max_level -1) * (1 + con_mod)
    max_best_hp = base_hp + (max_level -1) * (hd + con_mod)
    max_worst_hp = max(max_worst_hp, max_level)
    max_hp_range = f"{max_worst_hp}-{max_best_hp}"
    max_stats = generate_stats(12)
    max_con_score = max_stats.get("Constitution", 10)
    max_con_mod = (max_con_score - 10) // 2


    return jsonify({
        "name": full_name,
        "race": race,
        "class": char_class,
        "subclass": subclass,
        "gender": gender,
        "background": background,
        "appearance": appearance,
        "theme": theme,
        "level": level,
        "stats": stats,
        "max_stats": max_stats,
        "hp_range": hp_range,
        "max_level_preview": {
            "level": max_level,
            "hp_range": max_hp_range
        },
        "con_mod": con_mod,
        "max_con_mod":max_con_mod,
        "personal_item": personal_item,
        "backstory": backstory
    })  
    
@app.route("/download_pdf", methods=["POST"])
def download_pdf():
    data = request.get_json()

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    margin_x = 50
    y = height - 50
    line_height = 14
    section_spacing = 24
    max_line_width = 90  # wrap long lines

    def draw_wrapped(text, indent=0, bold=False):
        nonlocal y
        if not text:
            y -= line_height
            return
        font_size = 14 if bold else 12
        font = "Helvetica-Bold" if bold else "Helvetica"
        c.setFont(font, font_size)
        lines = wrap(text, width=max_line_width)
        for line in lines:
            if y < 60:
                c.showPage()
                y = height - 50
            c.drawString(margin_x + indent, y, line)
            y -= line_height

    def draw_section(title, content, indent=0):
        nonlocal y
        draw_wrapped(title, bold=True)

        if isinstance(content, list):
            for item in content:
                draw_wrapped(f"- {item}", indent=indent)

        elif isinstance(content, str):
            paragraphs = content.strip().split("\n")
            for para in paragraphs:
                wrapped = para.strip()
                if wrapped:
                    draw_wrapped(wrapped, indent=indent)

        y -= section_spacing

    # --- HEADER ---
    draw_wrapped(data["name"], bold=True)
    draw_wrapped(f"Race: {data['race']}")
    draw_wrapped(f"Class: {data['class']} ({data['subclass']})")
    draw_wrapped(f"Gender: {data['gender']}")
    draw_wrapped(f"Background: {data['background']}")
    draw_wrapped(f"Theme: {data['theme']['name']}")
    draw_wrapped(f"Personal Item: {data['personal_item']}")
    y -= section_spacing

    # --- STATS ---
    stat_lines = [f"{stat}: {val}" for stat, val in data["stats"].items()]
    draw_section("Stats:", stat_lines, indent=20)

    # --- Appearance ---
    draw_section("Appearance:", data["appearance"], indent=20)

    # --- Backstory ---
    draw_section("Backstory:", data["backstory"], indent=20)

    c.save()
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name="character_sheet.pdf", mimetype='application/pdf')


if __name__ == "__main__":
    app.run(debug=True)
