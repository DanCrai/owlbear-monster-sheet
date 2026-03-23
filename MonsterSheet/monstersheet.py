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
		# print("Saving throws: " + saves.items())
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

		# --- ABILITIES + PASSIVES ---
		tk.Label(frame, text="Abilities", font=("Arial", 12, "bold")).pack(anchor="w", pady=5)

		ability_box = tk.Text(frame, height=20, wrap="word")
		ability_box.pack(fill="both", expand=True)

		# --- ACTIVE ABILITIES ---
		for ab in monster_data.get("abilities", []):
			name = ab.get("name", "Ability")

			om = (ab.get("per_ap") or 0) * (ab.get("ap") or 1)

			ability_box.insert(tk.END, f"{name} (OM: {om:.1f})\n")

			if ab.get("desc"):
				ability_box.insert(tk.END, f"{ab['desc']}\n")

			details = []
			if ab.get("damage"):
				details.append(f"DMG: {ab['damage']}")
			if ab.get("range"):
				details.append(f"RNG: {ab['range']}")
			if ab.get("ap"):
				details.append(f"AP: {ab['ap']}")
			if ab.get("cooldown"):
				details.append(f"CD: {ab['cooldown']}")

			if details:
				ability_box.insert(tk.END, " | ".join(details) + "\n")

			if ab.get("effects"):
				effect_lines = []

				for e in ab["effects"]:
					if "stacks" in e:
						effect_lines.append(f"{e['type']}({e['stacks']})")
					else:
						effect_lines.append(
							f"{e['type']} [{e['value']} x {e['duration']}]"
						)

				ability_box.insert(tk.END, f"Effects: {', '.join(effect_lines)}\n")

			ability_box.insert(tk.END, "-" * 40 + "\n")

		# --- PASSIVES ---
		for p in monster_data.get("passives", []):
			name = p.get("name", "Passive")

			ability_box.insert(tk.END, f"{name} (passive)\n")

			if p.get("desc"):
				ability_box.insert(tk.END, f"{p['desc']}\n")

			if p["type"] == "add":
				ability_box.insert(tk.END, f"+{p['value']} OM per turn\n")
			elif p["type"] == "mult":
				ability_box.insert(tk.END, f"x{p['value']} total OM\n")

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
