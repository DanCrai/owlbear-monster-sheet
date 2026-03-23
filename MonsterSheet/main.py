import tkinter as tk
from tkinter import ttk
import re
import os
import json
from tkinter import filedialog
from monstersheet import MonsterSheet

# -------------------------
# Type Definitions
# -------------------------

DAMAGE_TYPES = {
    "slashing": "physical",
    "piercing": "physical",
    "crushing": "physical",
    "fire": "magical",
    "ice": "magical",
    "poison": "magical",
    "lightning": "magical",
    "thunder": "magical",
    "force": "magical",
    "shadow": "magical",
    "light": "magical",
    "spectral": "magical",
    "pure": "magical"
}

PHYS_CHANCE = 1 / 6
MAGIC_CHANCE = 1 / 20

DAMAGE_TYPE_LIST = list(DAMAGE_TYPES.keys())

HIT_TYPES = ["attack", "save", "auto"]

ABILITY_TYPES = ["weapon", "spell", "other"]

AOE_TYPES = {
    "none": 1.0,
    "cone": 1.5,
    "line": 1.3,
    "self_aoe": 1.4,
    "point_aoe": 1.5,
    "multi": 1.2,
    "bounce": 1.25
}

AOE_TABLE = {
    "cone": lambda r: 1.2 + min(r / 100, 0.5),
    "line": lambda r: 1.1 + min(r / 120, 0.4),
    "self_aoe": lambda r: 1.3,
    "point_aoe": lambda r: 1.4,
    "multi": lambda r: 1.2,
    "bounce": lambda r: 1.25
}

NEGATIVE_EFFECTS = [
    "Rooted", "Snared", "Disarmed", "Poisoned", "Paralyzed",
    "Taunted", "Prone", "Dazed", "Stunned", "Silenced",
    "Terrified", "Petrified", "Crystallized", "Sleeping",
    "Blinded", "Mad", "Charmed", "Maimed", "Cursed",
    "Decaying", "Ethereal", "Weakened", "Suffocating",
    "Impaired", "Exposed", "Corroded"
]

DOT_EFFECTS = [
    "Burning", "Envenomed", "Wounded"
]

EFFECT_BASE_AP = {
    "Stunned": 8,
    "Paralyzed": 6,
    "Petrified": 4.25,
    "Crystallized": 4.25,
    "Sleeping": 3,

    "Rooted": 3,
    "Snared": 3,
    "Prone": 3,
    "Maimed": 1,

    "Silenced": 4,
    "Disarmed": 4.5,

    "Blinded": 4.5,
    "Dazed": 3,
    "Weakened": 2.5,

    "Poisoned": 2,
    "Decaying": 2.5,
    "Corroded": 2,

    "Terrified": 5,
    "Taunted": 1,

    "Cursed": 2,
    "Exposed": 2,
    "Impaired": 1.5,

    "Mad": 6,
    "Charmed": 6.5,

    "Ethereal": 3,
    "Suffocating": 1.5
}

BASELINE_PLAYER_OM = 65  # example, you decide this
BASELINE_AP = 6
BASE_STACK_VALUE = BASELINE_PLAYER_OM / BASELINE_AP

passives = []


# -------------------------
# Classes
# -------------------------

def parse_list_field(entry):
    if not entry:
        return []
    return [x.strip() for x in entry.split(",") if x.strip()]


def parse_dict_field(entry):
    result = {}

    if not entry:
        return result

    parts = entry.split(",")

    for p in parts:
        p = p.strip()
        if not p:
            continue

        tokens = p.split()

        if len(tokens) < 2:
            continue  # skip invalid

        val = tokens[-1]
        name = " ".join(tokens[:-1])

        try:
            result[name] = int(val.replace("+", ""))
        except:
            continue  # skip invalid values safely

    return result


def parse_movement_field(entry):
    result = []

    if not entry:
        return result

    parts = entry.split(",")

    for p in parts:
        p = p.strip()
        if not p:
            continue

        tokens = p.split()

        if len(tokens) < 2:
            continue

        value = tokens[-1]
        name = " ".join(tokens[:-1])

        try:
            result.append({
                "type": name,
                "value": int(value)
            })
        except:
            continue

    return result


def build_monster_data():
    return {
        "name": entry_name.get(),

        "type": entry_type.get(),
        "size": entry_size.get(),
        "description": text_description.get("1.0", tk.END).strip(),

        "hp": entry_hp.get(),
        "ac": entry_ac.get(),
        "pa": entry_pa.get(),
        "ma": entry_ma.get(),
        "ms": entry_ms.get(),
        "extra_movement": parse_movement_field(entry_extra_movement.get()),

        "attributes": {
            "str": entry_str.get(),
            "dex": entry_dex.get(),
            "con": entry_con.get(),
            "int": entry_int.get(),
            "wis": entry_wis.get(),
            "will": entry_will.get(),
            "cha": entry_cha.get()
        },

        "skills": parse_dict_field(entry_skills.get()),
        "saving_throws": parse_dict_field(entry_saves.get()),

        "condition_immunities": parse_list_field(entry_cond_imm.get()),

        "resistances": [lb_resist.get(i) for i in lb_resist.curselection()],
        "immunities": [lb_immune.get(i) for i in lb_immune.curselection()],
        "vulnerabilities": [lb_vuln.get(i) for i in lb_vuln.curselection()],
        "absorb": [lb_absorb.get(i) for i in lb_absorb.curselection()],
        "frail": [lb_frail.get(i) for i in lb_frail.curselection()],

        "abilities": abilities,
        "passives": passives,

        "starting_ap": entry_start_ap.get(),
        "recovery_ap": entry_recovery_ap.get(),
        "max_ap": entry_max_ap.get(),

        "might": entry_might.get() or 1,

        "dm": result_var.get(),
        "om": om_result_var.get(),
        "cm": cm_var.get()
    }


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MONSTER_DIR = os.path.join(BASE_DIR, "..", "monsters")
LIST_FILE = os.path.join(MONSTER_DIR, "monsterList.json")


def save_monster():
    data = build_monster_data()

    name = data.get("name", "").lower().strip() or "monster"
    filename = re.sub(r'[\\/*?:"<>|]', "", name) + ".json"

    # Ensure folder exists
    os.makedirs(MONSTER_DIR, exist_ok=True)

    file_path = os.path.join(MONSTER_DIR, filename)

    # Save monster file
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

    print(f"Saved: {file_path}")

    # Update monster list
    update_monster_list(data, filename)


def update_monster_list(monster_data, filename):
    entry = {
        "name": monster_data.get("name"),
        "file": filename,
        "type": monster_data.get("type", "unknown"),
        "might": monster_data.get("might", 1)
    }

    # Load existing list
    if os.path.exists(LIST_FILE):
        with open(LIST_FILE, "r") as f:
            try:
                monster_list = json.load(f)
            except:
                monster_list = []
    else:
        monster_list = []

    # Replace if exists
    updated = False
    for i, m in enumerate(monster_list):
        if m["name"].lower() == entry["name"].lower():
            monster_list[i] = entry
            updated = True
            break

    if not updated:
        monster_list.append(entry)

    # Save list
    with open(LIST_FILE, "w") as f:
        json.dump(monster_list, f, indent=4)


def load_monster():
    file = filedialog.askopenfilename(
        filetypes=[("JSON files", "*.json")]
    )

    if not file:
        return

    with open(file, "r") as f:
        data = json.load(f)

    # --- BASIC FIELDS ---
    entry_name.delete(0, tk.END)
    entry_name.insert(0, data.get("name", ""))

    entry_hp.delete(0, tk.END)
    entry_hp.insert(0, data.get("hp", ""))

    entry_ac.delete(0, tk.END)
    entry_ac.insert(0, data.get("ac", ""))

    entry_pa.delete(0, tk.END)
    entry_pa.insert(0, data.get("pa", ""))

    entry_ma.delete(0, tk.END)
    entry_ma.insert(0, data.get("ma", ""))

    entry_type.insert(0, data.get("type", ""))
    entry_size.insert(0, data.get("size", ""))
    text_description.insert("1.0", data.get("description", ""))

    entry_ms.insert(0, data.get("ms", ""))
    entry_extra_movement.insert(0, data.get("extra_movement", ""))

    attrs = data.get("attributes", {})
    entry_str.insert(0, attrs.get("str", ""))
    entry_dex.insert(0, attrs.get("dex", ""))
    entry_con.insert(0, attrs.get("con", ""))
    entry_int.insert(0, attrs.get("int", ""))
    entry_wis.insert(0, attrs.get("wis", ""))
    entry_will.insert(0, attrs.get("will", ""))
    entry_cha.insert(0, attrs.get("cha", ""))

    entry_skills.insert(0, data.get("skills", ""))
    entry_saves.insert(0, data.get("saving_throws", ""))
    entry_cond_imm.insert(0, data.get("condition_immunities", ""))

    entry_start_ap.insert(0, data.get("starting_ap", ""))
    entry_max_ap.insert(0, data.get("max_ap", ""))
    entry_might.insert(0, data.get("might", "1"))

    # --- LISTBOXES ---
    def restore_selection(lb, values):
        for i in range(lb.size()):
            if lb.get(i) in values:
                lb.selection_set(i)

    lb_resist.selection_clear(0, tk.END)
    lb_immune.selection_clear(0, tk.END)
    lb_vuln.selection_clear(0, tk.END)
    lb_absorb.selection_clear(0, tk.END)
    lb_frail.selection_clear(0, tk.END)

    restore_selection(lb_resist, data.get("resistances", []))
    restore_selection(lb_immune, data.get("immunities", []))
    restore_selection(lb_vuln, data.get("vulnerabilities", []))
    restore_selection(lb_absorb, data.get("absorb", []))
    restore_selection(lb_frail, data.get("frail", []))

    update_selected_display()

    # --- ABILITIES ---
    global abilities
    abilities = data.get("abilities", [])
    update_ability_list()

    global passives
    passives = data.get("passives", [])
    update_passive_list()

    # --- OTHER ---
    entry_recovery_ap.delete(0, tk.END)
    entry_recovery_ap.insert(0, data.get("recovery_ap", ""))

    result_var.set(data.get("dm", ""))
    om_result_var.set(data.get("om", ""))
    cm_var.set(data.get("cm", ""))


def update_passive_list():
    passive_listbox.delete(0, tk.END)

    for p in passives:
        if p["type"] == "additive":
            passive_listbox.insert(tk.END, f"{p['name']} (+{p['value']} OM)")
        else:
            passive_listbox.insert(tk.END, f"{p['name']} (x{p['value']})")


def remove_passive():
    selection = passive_listbox.curselection()
    if selection:
        passives.pop(selection[0])
        update_passive_list()


def view_sheet():
    data = build_monster_data()
    MonsterSheet(root, data)


class PassiveEditor(tk.Toplevel):
    def __init__(self, master, passive=None, index=None):
        super().__init__(master)

        self.title("Passive Editor")
        self.geometry("300x250")

        self.index = index

        tk.Label(self, text="Name").pack()
        self.entry_name = tk.Entry(self)
        self.entry_name.pack()

        tk.Label(self, text="Description").pack()
        self.entry_desc = tk.Text(self, height=3)
        self.entry_desc.pack()

        tk.Label(self, text="Type").pack()
        self.type_box = ttk.Combobox(self, values=["additive", "multiplier"])
        self.type_box.pack()

        tk.Label(self, text="Value").pack()
        self.entry_value = tk.Entry(self)
        self.entry_value.pack()

        tk.Button(self, text="Save", command=self.save).pack(pady=5)

        if passive:
            self.entry_name.insert(0, passive.get("name", ""))
            self.type_box.set(passive.get("type", "additive"))
            self.entry_value.insert(0, passive.get("value", ""))

    def save(self):
        passive = {
            "name": self.entry_name.get(),
            "desc": self.entry_desc.get("1.0", tk.END).strip() or None,
            "type": self.type_box.get(),
            "value": float(self.entry_value.get()) if self.entry_value.get() else 0
        }

        if self.index is not None:
            passives[self.index] = passive
        else:
            passives.append(passive)

        update_passive_list()
        self.destroy()


class AbilityEditor(tk.Toplevel):
    def __init__(self, master, ability=None, index=None):
        super().__init__(master)

        self.title("Ability Editor")
        self.geometry("400x750")

        self.ability = ability
        self.index = index

        # --- Fields ---
        # NAME
        tk.Label(self, text="Name").pack()
        self.entry_name = tk.Entry(self)
        self.entry_name.pack()

        tk.Label(self, text="Description").pack()
        self.entry_desc = tk.Text(self, height=4)
        self.entry_desc.pack()

        # DAMAGE
        tk.Label(self, text="Damage").pack()
        self.entry_dmg = tk.Entry(self)
        self.entry_dmg.pack()

        tk.Label(self, text="Damage Type").pack()
        self.damage_type = ttk.Combobox(self, values=DAMAGE_TYPE_LIST)
        self.damage_type.pack()

        # HIT TYPE
        tk.Label(self, text="Hit Type").pack()
        self.hit_type = ttk.Combobox(self, values=HIT_TYPES)
        self.hit_type.pack()

        tk.Label(self, text="Hit Value (ATK / DC)").pack()
        self.entry_hit = tk.Entry(self)
        self.entry_hit.pack()

        # RANGE
        tk.Label(self, text="Range").pack()
        self.entry_range = tk.Entry(self)
        self.entry_range.pack()

        # AP
        tk.Label(self, text="AP Cost").pack()
        self.entry_ap = tk.Entry(self)
        self.entry_ap.pack()

        # COOLDOWN
        tk.Label(self, text="Cooldown").pack()
        self.entry_cd = tk.Entry(self)
        self.entry_cd.pack()

        # AOE
        tk.Label(self, text="AOE Type").pack()
        self.aoe_type = ttk.Combobox(self, values=list(AOE_TYPES.keys()))
        self.aoe_type.pack()

        self.aoe_radius_label = tk.Label(self, text="AOE Radius")
        self.aoe_radius_label.pack()

        self.entry_aoe_radius = tk.Entry(self)
        self.entry_aoe_radius.pack()

        self.aoe_type.bind("<<ComboboxSelected>>", self.update_aoe_label)

        # TYPE
        tk.Label(self, text="Ability Type").pack()
        self.ability_type = ttk.Combobox(self, values=ABILITY_TYPES)
        self.ability_type.pack()

        # PROJECTILE
        self.projectile_var = tk.BooleanVar()
        tk.Checkbutton(self, text="Projectile", variable=self.projectile_var).pack()

        self.effects = []

        tk.Button(self, text="Add Effect", command=self.add_effect).pack()
        self.effects_label = tk.Label(self, text="")
        self.effects_label.pack()

        # OM Override
        tk.Label(self, text="Total Ability OM Override").pack()
        self.entry_om_override = tk.Entry(self)
        self.entry_om_override.pack()

        # --- Buttons ---
        tk.Button(self, text="Save", command=self.save).pack(pady=5)

        # Load existing ability if editing
        if ability:
            self.load_ability()

    def update_effects_display(self):
        parts = []

        for e in self.effects:
            if "stacks" in e:
                parts.append(f"{e['type']}({e['stacks']})")
            else:
                parts.append(f"{e['type']}({e['value']} for {e['duration']})")

        self.effects_label.config(text=", ".join(parts))

    def update_aoe_label(self, event=None):
        if self.aoe_type.get() == "multi":
            self.aoe_radius_label.config(text="Number of Targets")
        else:
            self.aoe_radius_label.config(text="AOE Radius")

    def add_effect(self):
        win = tk.Toplevel(self)

        tk.Label(win, text="Effect Type").pack()
        effect_type = ttk.Combobox(
            win,
            values=NEGATIVE_EFFECTS + DOT_EFFECTS
        )
        effect_type.pack()

        # --- STACK INPUT ---
        stack_frame = tk.Frame(win)
        tk.Label(stack_frame, text="Stacks").pack()
        stacks_entry = tk.Entry(stack_frame)
        stacks_entry.pack()

        # --- DOT INPUT ---
        dot_frame = tk.Frame(win)

        tk.Label(dot_frame, text="Value (DoT)").pack()
        value_entry = tk.Entry(dot_frame)
        value_entry.pack()

        tk.Label(dot_frame, text="Duration").pack()
        duration_entry = tk.Entry(dot_frame)
        duration_entry.pack()

        # --- SWITCH LOGIC ---
        def update_fields(event=None):
            t = effect_type.get()

            # Clear both
            stack_frame.pack_forget()
            dot_frame.pack_forget()

            if t in DOT_EFFECTS:
                dot_frame.pack()
            elif t:
                stack_frame.pack()

        effect_type.bind("<<ComboboxSelected>>", update_fields)

        # --- SAVE ---
        def save_effect():
            t = effect_type.get()

            try:
                if t in DOT_EFFECTS:
                    self.effects.append({
                        "type": t,
                        "value": float(value_entry.get()),
                        "duration": float(duration_entry.get())
                    })
                else:
                    self.effects.append({
                        "type": t,
                        "stacks": int(stacks_entry.get())
                    })

                self.update_effects_display()
                win.destroy()

            except Exception as e:
                print("Effect save error:", e)

        tk.Button(win, text="Save", command=save_effect).pack()

    def load_ability(self):
        ab = self.ability

        # Clear everything first
        self.entry_name.delete(0, tk.END)
        self.entry_dmg.delete(0, tk.END)
        self.entry_hit.delete(0, tk.END)
        self.entry_range.delete(0, tk.END)
        self.entry_ap.delete(0, tk.END)
        self.entry_cd.delete(0, tk.END)

        self.entry_desc.delete("1.0", tk.END)

        # Fill fields safely
        self.entry_name.insert(0, ab.get("name", ""))
        self.entry_desc.insert("1.0", ab.get("desc", "") or "")

        if ab.get("damage"):
            self.entry_dmg.insert(0, ab["damage"])

        if ab.get("hit_value") is not None:
            self.entry_hit.insert(0, ab["hit_value"])

        if ab.get("range") is not None:
            self.entry_range.insert(0, ab["range"])

        if ab.get("ap") is not None:
            self.entry_ap.insert(0, ab["ap"])

        if ab.get("cooldown") is not None:
            self.entry_cd.insert(0, ab["cooldown"])

        # Dropdowns
        self.damage_type.set(ab.get("damage_type", "") or "")
        self.hit_type.set(ab.get("hit_type", "") or "")
        self.aoe_type.set(ab.get("aoe", "none") or "")
        self.ability_type.set(ab.get("type", "other") or "")
        self.entry_aoe_radius.delete(0, tk.END)

        if ab.get("aoe_radius") is not None:
            self.entry_aoe_radius.insert(0, ab["aoe_radius"])

        self.aoe_type.set(ab.get("aoe", "none") or "")
        self.update_aoe_label()

        # Checkbox
        self.projectile_var.set(ab.get("projectile", False) or False)

        # Effects
        self.effects = ab.get("effects", [])
        self.update_effects_display()

    def save(self):

        print("begin save")

        try:
            om_override = float(self.entry_om_override.get()) if self.entry_om_override.get() else None
            ability = {
                "name": self.entry_name.get(),
                "desc": self.entry_desc.get("1.0", tk.END).strip() or None,

                "damage": self.entry_dmg.get() or None,
                "damage_type": self.damage_type.get() or None,

                "hit_type": self.hit_type.get() or None,
                "hit_value": float(self.entry_hit.get()) if self.entry_hit.get() else None,

                "range": float(self.entry_range.get()) if self.entry_range.get() else None,
                "ap": float(self.entry_ap.get()) if self.entry_ap.get() else None,
                "cooldown": float(self.entry_cd.get()) if self.entry_cd.get() else None,

                "aoe": self.aoe_type.get() or "none",
                "type": self.ability_type.get() or "other",
                "aoe_radius": float(self.entry_aoe_radius.get()) if self.entry_aoe_radius.get() else None,
                "projectile": self.projectile_var.get(),

                "effects": list(self.effects),

                "om_override": om_override
            }

            print("ability:", ability)

            # --- CALCULATE OM ---
            if ability["om_override"] is not None:
                print("in if")
                per_ap = ability["om_override"] / (ability["ap"] if ability["ap"] else 1)
                weight = 1 / ability["cooldown"] if ability["cooldown"] else 1
            else:
                print("in else")
                per_ap, weight = calculate_ability_om(ability)

            print("after")
            ability["per_ap"] = per_ap
            ability["weight"] = weight

            print("after2")
            # --- ADD OR REPLACE ---
            if self.index is not None:
                abilities[self.index] = ability
            else:
                abilities.append(ability)
            print("after3")
            # --- UPDATE UI ---
            update_ability_list()
            print("after4")
            # --- CLOSE WINDOW ---
            self.destroy()

        except Exception as e:
            print("SAVE ERROR:", e)


# -------------------------
# Core Logic - offensive
# -------------------------

def parse_damage(damage_str):
    damage_str = damage_str.replace(" ", "")

    # Case 1: flat damage (e.g. "40")
    if re.fullmatch(r"\d+", damage_str):
        return float(damage_str)

    # Case 2: X + YdZ
    match = re.fullmatch(r"(\d+)\+(\d+)d(\d+)", damage_str)
    if match:
        flat = int(match.group(1))
        dice_count = int(match.group(2))
        dice_size = int(match.group(3))

        avg_dice = dice_count * (dice_size + 1) / 2
        return flat + avg_dice

    raise ValueError("Invalid damage format")


def range_modifier(range_val):
    if range_val < 30:
        return 1.0
    elif range_val < 60:
        return 1.1
    elif range_val < 90:
        return 1.2
    else:
        return 1.3


def duration_multiplier(duration):
    if duration <= 1:
        return 1
    return 1/(2**(duration-1)) + duration_multiplier(duration - 1)


def calculate_effect_om(ability):
    total = 0

    for effect in ability.get("effects", []):

        # --- STACK EFFECTS ---
        if "stacks" in effect:
            effect_type = effect["type"]
            stacks = effect["stacks"]

            effect_ap = EFFECT_BASE_AP.get(effect_type, 2)
            total += stacks * effect_ap * BASE_STACK_VALUE

        # --- DOT EFFECTS ---
        elif "value" in effect and "duration" in effect:
            val = effect["value"]
            dur = effect["duration"]

            mult = duration_multiplier(dur)
            dot_value = val * mult

            # wounded = double trigger
            if effect["type"] == "wounded":
                dot_value *= 2

            total += dot_value

    return total


def calculate_ability_om(ability):
    base = 0

    # --- DAMAGE ---
    if ability.get("damage"):
        base = parse_damage(ability["damage"])
    else:
        base = 0
    print("damage: " + base.__str__())
    # --- HIT TYPE ---
    if ability.get("hit_type") == "attack" and ability.get("hit_value") is not None:
        base *= (1 + (ability["hit_value"] - 5) * 0.05) / 2

    elif ability.get("hit_type") == "save" and ability.get("hit_value") is not None:
        base *= (1 + (ability["hit_value"] - 13) * 0.05) / 2

    # auto hit = no change

    # --- RANGE ---
    if ability.get("range") is not None:
        base *= range_modifier(ability["range"])

    # --- AOE ---
    base *= get_aoe_multiplier(ability)

    # --- EFFECTS
    base += calculate_effect_om(ability)

    # --- AP ---
    if ability.get("ap") is not None and ability["ap"] > 0:
        per_ap = base / ability["ap"]
    else:
        per_ap = base  # no AP → treated as full value

    # --- COOLDOWN ---
    if ability.get("cooldown") is not None and ability["cooldown"] > 0:
        weight = 1 / ability["cooldown"]
    else:
        weight = 1
    print("per ap: " + per_ap.__str__())
    return per_ap, weight


def calculate_total_om():
    try:
        recovery_ap = float(entry_recovery_ap.get())

        total_weighted = 0
        total_weights = 0

        for ab in abilities:
            total_weighted += ab["per_ap"] * ab["weight"]
            total_weights += ab["weight"]

        if total_weights == 0:
            om = 0
        else:
            avg_per_ap = total_weighted / total_weights if total_weights else 0
            base_om = avg_per_ap * recovery_ap

            # --- ADDITIVE PASSIVES ---
            additive_bonus = sum(
                p["value"] for p in passives if p["type"] == "additive"
            )

            # --- MULTIPLIERS ---
            multiplier = 1
            for p in passives:
                if p["type"] == "multiplier":
                    multiplier *= p["value"]

            # --- FINAL OM ---
            om = (base_om + additive_bonus) * multiplier

        om_result_var.set(f"Total OM: {om:.2f}")

        # --- UPDATE CM ---
        try:
            dm = float(result_var.get().split(":")[1])
            cm = dm * om
            cm_var.set(f"Combat Might: {cm:.2f}")
        except:
            pass

    except:
        om_result_var.set("Invalid OM calculation")


def get_aoe_multiplier(ability):
    aoe = ability.get("aoe", "none")
    radius = ability.get("aoe_radius", 0) or 0
    rng = ability.get("range", 0) or 0

    if aoe == "none":
        return 1.0

    # CONE
    if aoe == "cone":
        steps = max(1, int(radius // 15))
        return 1 + 0.15 * steps

    # LINE
    if aoe == "line":
        steps = max(1, int(radius // 5))
        return 1 + 0.1 * steps

    # SELF AOE
    if aoe == "self_aoe":
        if radius <= 10:
            return 1.25
        elif radius <= 30:
            return 1.5
        elif radius <= 60:
            return 2
        else:
            return 3

    # POINT AOE
    if aoe == "point_aoe":
        if radius <= 5:
            return 1.25
        elif radius <= 10:
            return 1.4
        elif radius <= 20:
            return 2
        elif radius <= 30:
            return 2.5
        else:
            return 3

    # MULTI TARGET
    if aoe == "multi":
        targets = radius

        if targets <= 0:
            return 1

        range_factor = max(1, int(rng / 10))
        scaling = 0.5 * (targets + 1)

        return min(range_factor * scaling, targets)

    # BOUNCE
    if aoe == "bounce":
        return 1.25 + min(radius / 30, 1)

    return 1.0


# -------------------------
# Core Logic - defensive
# -------------------------


def get_trigger_chance(dmg_type):
    if DAMAGE_TYPES[dmg_type] == "physical":
        return PHYS_CHANCE
    else:
        return MAGIC_CHANCE


def remove_from_other_lists(selected_listbox, value):
    for lb in [lb_resist, lb_immune, lb_vuln, lb_absorb, lb_frail]:
        if lb == selected_listbox:
            continue

        for i in range(lb.size()):
            if lb.get(i) == value:
                lb.selection_clear(i)


def calculate_resistance_multiplier(resistances, immunities, vulnerabilities):
    total_resist = 0
    total_immune = 0
    total_vuln = 0

    for r in resistances:
        chance = get_trigger_chance(r)
        total_resist += chance * 0.5

    for i in immunities:
        chance = get_trigger_chance(i)
        total_immune += chance * 1

    for v in vulnerabilities:
        chance = get_trigger_chance(v)
        total_vuln += chance * 1

    resist_mult = 1 - total_resist
    immune_mult = 1 - total_immune
    vuln_mult = 1 + total_vuln

    result = resist_mult * immune_mult * vuln_mult

    print("multiplier: " + result.__str__())

    return result


def calculate_dm():
    try:
        hp = float(entry_hp.get())
        ac = float(entry_ac.get())
        pa = float(entry_pa.get())
        ma = float(entry_ma.get())

        avg_armor = (pa + ma) / 2
        base_reduction = 1 - 0.05 * (ac - 16)

        resistances = [lb_resist.get(i) for i in lb_resist.curselection()]
        immunities = [lb_immune.get(i) for i in lb_immune.curselection()]
        vulnerabilities = [lb_vuln.get(i) for i in lb_vuln.curselection()]

        res_mult = calculate_resistance_multiplier(
            resistances, immunities, vulnerabilities
        )

        total_reduction = base_reduction * res_mult

        dm = (hp / total_reduction) + 16 * avg_armor

        result_var.set(f"Defensive Might: {dm:.2f}")

    except Exception as e:
        result_var.set("Invalid input")


def create_listbox(parent, column, title):
    tk.Label(parent, text=title).grid(row=0, column=column)

    lb = tk.Listbox(
        parent,
        selectmode=tk.MULTIPLE,
        height=13,
        exportselection=False,  # <-- IMPORTANT FIX
        selectbackground="lightblue",
        selectforeground="black"
    )
    lb.grid(row=1, column=column, rowspan=3, padx=5)

    return lb


def update_ability_list():
    ability_listbox.delete(0, tk.END)

    for ab in abilities:
        om = (ab.get("per_ap") or 0) * (ab.get("ap") or 1)
        ability_listbox.insert(tk.END, f"{ab['name']}  (OM: {om:.1f})")


def update_selected_display(event=None):
    if event:
        widget = event.widget

        selected_indices = widget.curselection()
        selected_values = [widget.get(i) for i in selected_indices]

        # Remove duplicates from other lists
        for val in selected_values:
            remove_from_other_lists(widget, val)

    # Always rebuild display (this part should ALWAYS run)
    resistances = [lb_resist.get(i) for i in lb_resist.curselection()]
    immunities = [lb_immune.get(i) for i in lb_immune.curselection()]
    vulnerabilities = [lb_vuln.get(i) for i in lb_vuln.curselection()]
    absorb = [lb_absorb.get(i) for i in lb_absorb.curselection()]
    frail = [lb_frail.get(i) for i in lb_frail.curselection()]

    text = (
        f"Resist: {', '.join(resistances)} | "
        f"Immune: {', '.join(immunities)} | "
        f"Vuln: {', '.join(vulnerabilities)} | "
        f"Absorb: {', '.join(absorb)} | "
        f"Frail: {', '.join(frail)}"
    )
    selected_var.set(text)


def on_ability_select(event):
    selection = ability_listbox.curselection()
    if not selection:
        return

    index = selection[0]
    AbilityEditor(root, abilities[index], index)


def remove_selected():
    selection = ability_listbox.curselection()
    if selection:
        abilities.pop(selection[0])
        update_ability_list()


# -------------------------
# UI Setup
# -------------------------

root = tk.Tk()
root.title("Monster Calculator")

# =========================
# LEFT PANEL (DEFENSIVE)
# =========================


frame_left = tk.Frame(root, padx=10, pady=10)
frame_left.grid(row=0, column=0, sticky="n")

tk.Label(frame_left, text="Monster Name").grid(row=0, column=0, sticky="w")
entry_name = tk.Entry(frame_left, width=15)
entry_name.grid(row=0, column=1)

tk.Label(frame_left, text="Type").grid(row=0, column=2)
entry_type = tk.Entry(frame_left, width=10)
entry_type.grid(row=0, column=3)

tk.Label(frame_left, text="Size").grid(row=1, column=2)
entry_size = tk.Entry(frame_left, width=10)
entry_size.grid(row=1, column=3)

tk.Label(frame_left, text="Description").grid(row=2, column=2)
text_description = tk.Text(frame_left, height=3, width=20)
text_description.grid(row=3, column=2, columnspan=2)

tk.Label(frame_left, text="DEFENSIVE", font=("Arial", 10, "bold")).grid(row=1, column=0, columnspan=2)

# Base stats
tk.Label(frame_left, text="HP").grid(row=2, column=0, sticky="w")
entry_hp = tk.Entry(frame_left, width=10)
entry_hp.grid(row=2, column=1)

tk.Label(frame_left, text="AC").grid(row=3, column=0, sticky="w")
entry_ac = tk.Entry(frame_left, width=10)
entry_ac.grid(row=3, column=1)

tk.Label(frame_left, text="PA").grid(row=4, column=0, sticky="w")
entry_pa = tk.Entry(frame_left, width=10)
entry_pa.grid(row=4, column=1)

tk.Label(frame_left, text="MA").grid(row=5, column=0, sticky="w")
entry_ma = tk.Entry(frame_left, width=10)
entry_ma.grid(row=5, column=1)

tk.Label(frame_left, text="Effect Threshold").grid(row=6, column=0, sticky="w")
entry_threshold = tk.Entry(frame_left, width=10)
entry_threshold.grid(row=6, column=1)

tk.Label(frame_left, text="MS").grid(row=7, column=0)
entry_ms = tk.Entry(frame_left, width=10)
entry_ms.grid(row=7, column=1)

tk.Label(frame_left, text="Extra Movement").grid(row=8, column=0, sticky="w")
entry_extra_movement = tk.Entry(frame_left, width=25)
entry_extra_movement.grid(row=8, column=1)

tk.Label(frame_left, text="STR").grid(row=9, column=0)
entry_str = tk.Entry(frame_left, width=5)
entry_str.grid(row=9, column=1)

tk.Label(frame_left, text="DEX").grid(row=9, column=2)
entry_dex = tk.Entry(frame_left, width=5)
entry_dex.grid(row=9, column=3)

tk.Label(frame_left, text="CON").grid(row=10, column=0)
entry_con = tk.Entry(frame_left, width=5)
entry_con.grid(row=10, column=1)

tk.Label(frame_left, text="INT").grid(row=10, column=2)
entry_int = tk.Entry(frame_left, width=5)
entry_int.grid(row=10, column=3)

tk.Label(frame_left, text="WIS").grid(row=11, column=0)
entry_wis = tk.Entry(frame_left, width=5)
entry_wis.grid(row=11, column=1)

tk.Label(frame_left, text="WILL").grid(row=11, column=2)
entry_will = tk.Entry(frame_left, width=5)
entry_will.grid(row=11, column=3)

tk.Label(frame_left, text="CHA").grid(row=12, column=0)
entry_cha = tk.Entry(frame_left, width=5)
entry_cha.grid(row=12, column=1)

tk.Label(frame_left, text="Skills").grid(row=13, column=0)
entry_skills = tk.Entry(frame_left, width=25)
entry_skills.grid(row=13, column=1, columnspan=3)

tk.Label(frame_left, text="Saving Throws").grid(row=14, column=0)
entry_saves = tk.Entry(frame_left, width=25)
entry_saves.grid(row=14, column=1, columnspan=3)

tk.Label(frame_left, text="Cond Immunities").grid(row=15, column=0)
entry_cond_imm = tk.Entry(frame_left, width=25)
entry_cond_imm.grid(row=15, column=1, columnspan=3)

entry_hp.insert(0, "1000")
entry_ac.insert(0, "16")
entry_pa.insert(0, "0")
entry_ma.insert(0, "0")
entry_threshold.insert(0, "1")

# Resistances block
frame_res = tk.Frame(root, padx=10)
frame_res.grid(row=0, column=1, sticky="n")

lb_resist = create_listbox(frame_res, 0, "Resist")
lb_immune = create_listbox(frame_res, 1, "Immune")
lb_vuln = create_listbox(frame_res, 2, "Vuln")
lb_absorb = create_listbox(frame_res, 3, "Absorb")
lb_frail = create_listbox(frame_res, 4, "Frail")

for dmg in DAMAGE_TYPES.keys():
    lb_resist.insert(tk.END, dmg)
    lb_immune.insert(tk.END, dmg)
    lb_vuln.insert(tk.END, dmg)
    lb_absorb.insert(tk.END, dmg)
    lb_frail.insert(tk.END, dmg)

lb_resist.bind("<<ListboxSelect>>", update_selected_display)
lb_immune.bind("<<ListboxSelect>>", update_selected_display)
lb_vuln.bind("<<ListboxSelect>>", update_selected_display)
lb_absorb.bind("<<ListboxSelect>>", update_selected_display)
lb_frail.bind("<<ListboxSelect>>", update_selected_display)

selected_var = tk.StringVar()
tk.Label(frame_res, textvariable=selected_var, wraplength=300, justify="left") \
    .grid(row=6, column=1, columnspan=3, pady=5)

# DM Button + result
btn_calc = tk.Button(frame_left, text="Calculate DM", command=calculate_dm)
btn_calc.grid(row=5, column=2, columnspan=2, pady=5)

result_var = tk.StringVar()
tk.Label(frame_left, textvariable=result_var, font=("Arial", 10)).grid(row=6, column=2, columnspan=2)

# =========================
# RIGHT PANEL (ABILITIES)
# =========================
abilities = []

frame_right = tk.Frame(root, padx=10, pady=10)
frame_right.grid(row=0, column=2, sticky="n")

tk.Label(frame_right, text="Recovery AP").grid(row=6, column=0, sticky="w")
entry_recovery_ap = tk.Entry(frame_right, width=10)
entry_recovery_ap.grid(row=6, column=1)
entry_recovery_ap.insert(0, "6")

# Buttons
# tk.Button(frame_right, text="Add Ability", command=add_ability).grid(row=7, column=0, columnspan=2, pady=3)
tk.Button(frame_right, text="Calculate OM", command=calculate_total_om).grid(row=8, column=0, columnspan=2)

om_result_var = tk.StringVar()
tk.Label(frame_right, textvariable=om_result_var).grid(row=9, column=0, columnspan=2)

cm_var = tk.StringVar()
tk.Label(frame_right, textvariable=cm_var, font=("Arial", 11, "bold")) \
    .grid(row=10, column=0, columnspan=2)

tk.Label(frame_right, text="Abilities").grid(row=0, column=0)

ability_listbox = tk.Listbox(frame_right, width=40, height=12)
ability_listbox.grid(row=1, column=0, columnspan=2, pady=5)
ability_listbox.bind("<<ListboxSelect>>", on_ability_select)

tk.Button(frame_right, text="Add Ability",
          command=lambda: AbilityEditor(root)).grid(row=2, column=0)
tk.Button(frame_right, text="Remove", command=remove_selected).grid(row=2, column=1)

tk.Label(frame_right, text="Passives").grid(row=11, column=0)

passive_listbox = tk.Listbox(frame_right, width=40, height=6)
passive_listbox.grid(row=12, column=0, columnspan=2)

tk.Button(frame_right, text="Add Passive",
          command=lambda: PassiveEditor(root)).grid(row=13, column=0)

tk.Button(frame_right, text="Remove Passive",
          command=lambda: remove_passive()).grid(row=13, column=1)

tk.Button(root, text="Save Monster", command=save_monster) \
    .grid(row=1, column=0, columnspan=1)

tk.Button(root, text="Load Monster", command=load_monster) \
    .grid(row=1, column=1, columnspan=1)

tk.Button(root, text="View Sheet", command=view_sheet) \
    .grid(row=1, column=2)

tk.Label(frame_right, text="Starting AP").grid(row=3, column=0)
entry_start_ap = tk.Entry(frame_right, width=10)
entry_start_ap.grid(row=3, column=1)

tk.Label(frame_right, text="Max AP").grid(row=4, column=0)
entry_max_ap = tk.Entry(frame_right, width=10)
entry_max_ap.grid(row=4, column=1)

tk.Label(frame_right, text="Might").grid(row=5, column=0)
entry_might = tk.Entry(frame_right, width=10)
entry_might.insert(0, "1")
entry_might.grid(row=5, column=1)

root.mainloop()
