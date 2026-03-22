import tkinter as tk

class MonsterSheet(tk.Toplevel):
    def __init__(self, master, monster_data):
        super().__init__(master)

        self.title("Monster Sheet")
        self.geometry("800x1000")

        frame = tk.Frame(self, padx=10, pady=10)
        frame.pack(fill="both", expand=True)

        # --- NAME + TYPE ---
        tk.Label(
            frame,
            text=monster_data.get("name", "Unnamed Monster"),
            font=("Arial", 16, "bold")
        ).pack(anchor="center", pady=5)

        subtype = monster_data.get("type", "")
        size = monster_data.get("size", "")
        if subtype or size:
            tk.Label(frame, text=f"{subtype}, {size}").pack(anchor="center")

        # --- DESCRIPTION ---
        if monster_data.get("description"):
            tk.Label(
                frame,
                text=monster_data["description"],
                wraplength=550,
                justify="left"
            ).pack(anchor="w", pady=5)

        # --- CORE STATS ---
        stats = (
            f"HP: {monster_data.get('hp')}   "
            f"AC: {monster_data.get('ac')}   "
            f"PA: {monster_data.get('pa')}   "
            f"MA: {monster_data.get('ma')}   "
            f"MS: {monster_data.get('ms', '-')}"
        )
        tk.Label(frame, text=stats).pack(anchor="w", pady=5)
        extra_movement = monster_data.get("extra_movement", [])
        if extra_movement:
            tk.Label(frame, text="Extra Movement:", font=("Arial", 10, "bold")).pack(anchor="w")
            for m in extra_movement:
                tk.Label(frame, text=f"{m['type']}: {m['value']} ft").pack(anchor="w")

        # --- RESISTANCE TYPES ---
        def line(label, values):
            if not values:
                return

            if isinstance(values, str):
                values = [values]

            tk.Label(frame, text=f"{label}: {', '.join(values)}").pack(anchor="w")

        line("Vulnerabilities", monster_data.get("vulnerabilities", []))
        line("Resistances", monster_data.get("resistances", []))
        line("Immunities", monster_data.get("immunities", []))
        line("Absorb", monster_data.get("absorb", []))
        line("Frail", monster_data.get("frail", []))

        # --- CONDITIONS ---
        line("Condition Immunities", monster_data.get("condition_immunities", []))

        # --- SKILLS ---
        skills = monster_data.get("skills")
        if skills:
            tk.Label(frame, text="Skills:", font=("Arial", 10, "bold")).pack(anchor="w")

            if isinstance(skills, dict):
                for k, v in skills.items():
                    tk.Label(frame, text=f"{k}: +{v}").pack(anchor="w")
            else:
                tk.Label(frame, text=str(skills)).pack(anchor="w")

        # --- SAVES ---
        print(monster_data)
        saves = monster_data.get("saving_throws")
        #print("Saving throws: " + saves.items())
        if saves:
            tk.Label(frame, text="Saving Throws:", font=("Arial", 10, "bold")).pack(anchor="w")

            if isinstance(saves, dict):
                for k, v in saves.items():
                    tk.Label(frame, text=f"{k}: +{v}").pack(anchor="w")
            else:
                tk.Label(frame, text=str(saves)).pack(anchor="w")

        # --- ATTRIBUTES ---
        if monster_data.get("attributes"):
            attrs = monster_data["attributes"]
            attr_line = "   ".join([
                f"{k.upper()} {v}" for k, v in attrs.items()
            ])
            tk.Label(frame, text=attr_line).pack(anchor="w", pady=5)

        # --- AP ---
        ap_line = (
            f"Starting AP: {monster_data.get('starting_ap', '-')}   "
            f"Recovery AP: {monster_data.get('recovery_ap', '-')}   "
            f"Max AP: {monster_data.get('max_ap', '-')}"
        )
        tk.Label(frame, text=ap_line).pack(anchor="w", pady=5)

        # --- ABILITIES ---
        tk.Label(frame, text="Abilities", font=("Arial", 12, "bold")).pack(anchor="w", pady=5)

        ability_box = tk.Text(frame, height=20, wrap="word")
        ability_box.pack(fill="both", expand=True)

        for ab in monster_data.get("abilities", []):
            line = f"{ab.get('name', 'Ability')}"

            # AP / cooldown inline
            parts = []
            if ab.get("ap"):
                parts.append(f"{int(ab['ap'])} AP")
            if ab.get("cooldown"):
                parts.append(f"recharge {int(ab['cooldown'])}")

            if parts:
                line += " (" + "; ".join(parts) + ")"

            ability_box.insert(tk.END, line + "\n")

            # description
            if ab.get("desc"):
                ability_box.insert(tk.END, f"{ab['desc']}\n")

            # hit info
            if ab.get("hit_type") and ab.get("hit_value") is not None:
                if ab["hit_type"] == "attack":
                    ability_box.insert(tk.END, f"+{int(ab['hit_value'])} to hit\n")
                elif ab["hit_type"] == "save":
                    ability_box.insert(tk.END, f"DC {int(ab['hit_value'])} save\n")

            # damage
            details = []

            if ab.get("range"):
                details.append(f"{int(ab['range'])} ft")

            if ab.get("damage"):
                details.append(f"{ab['damage']} {ab.get('damage_type', '')}")

            if details:
                ability_box.insert(tk.END, " | ".join(details) + "\n")

            # effects
            if ab.get("effects"):
                effects_text = ", ".join(
                    f"{e['type']}({e['stacks']})" for e in ab["effects"]
                )
                ability_box.insert(tk.END, f"Effects: {effects_text}\n")

            ability_box.insert(tk.END, "-" * 40 + "\n")

        ability_box.config(state="disabled")

        # --- MIGHT ---
        tk.Label(
            frame,
            text=f"Might: {monster_data.get('might', 1)} "
                 f"(OM: {monster_data.get('om')} / "
                 f"DM: {monster_data.get('dm')} / "
                 f"CM: {monster_data.get('cm')})",
            font=("Arial", 11, "bold")
        ).pack(anchor="center", pady=10)