import { getMonsterList } from "./storage.js";
import { getSelectedToken, getSelectedMonsterData, assignMonsterToToken } from "./token.js";

const DAMAGE_TYPES = {
    slashing: "physical",
    piercing: "physical",
    crushing: "physical",
    fire: "magical",
    ice: "magical",
    poison: "magical",
    lightning: "magical",
    thunder: "magical",
    force: "magical",
    shadow: "magical",
    light: "magical",
    spectral: "magical",
    pure: "magical"
};

export function setupPanel() {
    updatePanel();

    OBR.player.onChange(() => {
        updatePanel();
    });

    OBR.scene.items.onChange(() => {
        updatePanel();
    });
}

export async function updatePanel() {
    const sheet = document.getElementById("sheet");
    if (!sheet) return;

    const token = await getSelectedToken();

    if (!token) {
        sheet.innerHTML = "No token selected";
        return;
    }

    const monsterMeta = token.metadata?.monsterSheet;

    if (!monsterMeta) {
        sheet.innerHTML = "Token not tracked (use context menu)";
        return;
    }

    const monsters = await getMonsterList();

    // --- TOP SECTION ---
    let html = `
    <div class="topbar">
        <strong>${token.name || "Unnamed Token"}</strong>

        <select id="monsterDropdown">
            <option value="">Select Monster</option>
            ${monsters.map(m =>
                `<option value="${m.file}" ${monsterMeta?.name === m.name ? "selected" : ""}>
        ${m.name} (Might ${m.might})
     </option>`
            ).join("")}
        </select>
    </div>
    <hr/>
`;

    var hp = 0;
    if (monsterMeta.data) {
        hp = monsterMeta.data.hp;
    }
    html += `
    <div class="sheet">
        <div style="display:flex; align-items:center; gap:8px; flex-wrap:wrap;">
            
            <strong>HP:</strong>
            <input id="hpInput" type="number" value="${hp}" style="width:60px;">

            <span style="margin-left:10px;">Take damage</span>

            <input id="dmgInput" type="number" placeholder="amount" style="width:60px;">

            <select id="dmgType">
                ${Object.keys(DAMAGE_TYPES).map(t => `<option value="${t}">${t}</option>`).join("")}
            </select>

            <button id="applyDmg">Apply</button>

        </div>
    </div>
`;

    if (monsterMeta.data) {
        const m = monsterMeta?.data;

        if (!m) {
            html += "<div>No monster selected</div>";
        } else {

            html += `
<div class="sheet">

<h2>${m.name}</h2>
<p><i>${m.type || ""}</i></p>

<p><b>HP:</b> ${monsterMeta.hp ?? m.hp} | 
<b>AC:</b> ${m.ac} | 
<b>PA:</b> ${m.pa} | 
<b>MA:</b> ${m.ma}</p>

<p><b>Speed:</b> ${m.ms || "-"} ft</p>

${m.extra_movement?.length ? `
<p><b>Movement:</b> ${m.extra_movement.map(e => `${e.name} ${e.value}ft`).join(", ")}</p>
` : ""}

${m.senses?.length ? `
<p><b>Senses:</b> ${m.senses.join(", ")}</p>
` : ""}

<p><b>Resist:</b> ${m.resistances?.join(", ") || "-"}</p>
<p><b>Immune:</b> ${m.immunities?.join(", ") || "-"}</p>
<p><b>Vulnerable:</b> ${m.vulnerabilities?.join(", ") || "-"}</p>
<p><b>Absorb:</b> ${m.absorb?.join(", ") || "-"}</p>
<p><b>Frail:</b> ${m.frail?.join(", ") || "-"}</p>

<p><b>Might:</b> ${m.might} 
(OM: ${m.om || "-"} / DM: ${m.dm || "-"} / CM: ${m.cm || "-"})</p>

<hr/>

<h3>Abilities</h3>

${m.abilities.map(ab => `
<div style="margin-bottom:8px;">
    <b>${ab.name}</b> (${ab.ap || "-"} AP${ab.cooldown ? `; CD ${ab.cooldown}` : ""})<br/>

    ${ab.damage ? `[${ab.damage}] ${ab.damage_type || ""}<br/>` : ""}

    ${ab.hit_type === "attack" ? `+${ab.hit_value} to hit<br/>` : ""}
    ${ab.hit_type === "save" ? `DC ${ab.hit_value} ${ab.damage_type || ""}<br/>` : ""}

    ${ab.range ? `Range: ${ab.range} ft<br/>` : ""}

    ${ab.desc ? `${ab.desc}<br/>` : ""}

    ${ab.effects?.length ? `
        Effects: ${ab.effects.map(e => `${e.type}(${e.stacks})`).join(", ")}<br/>
    ` : ""}
</div>
`).join("")}

</div>
`;
        }
    }

    sheet.innerHTML = html;

    // --- HP MANUAL EDIT ---
    document.getElementById("hpInput").onchange = async (e) => {
        const newHp = Number(e.target.value);

        await OBR.scene.items.updateItems([token.id], (items) => {
            items[0].metadata.monsterSheet.hp = newHp;
        });

        updatePanel();
    };

    // --- APPLY DAMAGE ---
    document.getElementById("applyDmg").onclick = async () => {
        const dmg = Number(document.getElementById("dmgInput").value);
        const type = document.getElementById("dmgType").value;

        if (!dmg || dmg <= 0) return;

        const newHp = calculateDamage(monsterMeta, dmg, type);

        await OBR.scene.items.updateItems([token.id], (items) => {
            items[0].metadata.monsterSheet.hp = newHp;
        });

        updatePanel();
    };

    // --- DROPDOWN EVENT ---
    document.getElementById("monsterDropdown").onchange = async (e) => {
        const value = e.target.value;
        if (!value) return;

        await assignMonsterToToken(token.id, value);
        updatePanel();
    };
}

function calculateDamage(monsterMeta, dmg, type) {
    const m = monsterMeta.data;

    let final = dmg;

    // --- RESIST / IMMUNE / VULN ---
    const resist = m.resistances || [];
    const immune = m.immunities || [];
    const vuln = m.vulnerabilities || [];

    if (immune.includes(type)) {
        final = 0;
    } else {
        if (resist.includes(type)) final *= 0.5;
        if (vuln.includes(type)) final *= 2;
    }

    // --- ARMOR (PA / MA) ---
    const category = DAMAGE_TYPES[type]; // physical / magical

    if (category === "physical") {
        final = final - (m.pa || 0);
    } else {
        final = final - (m.ma || 0);
    }

    final = Math.max(0, Math.floor(final));

    const currentHp = monsterMeta.hp ?? m.hp;

    return Math.max(0, currentHp - final);
}

/*import { getSelectedMonster } from "./token.js";

export function setupPanel() {
    const sheet = document.getElementById("sheet");
    if (!sheet) return;

    // Update whenever selection changes
    OBR.player.onChange(() => {
        updatePanel();
    });
}

export async function updatePanel() {
    const sheet = document.getElementById("sheet");
    if (!sheet) return;

    const monster = await getSelectedMonster();

    if (!monster) {
        sheet.innerHTML = "No monster selected";
        return;
    }

    sheet.innerHTML = `
        <h2>${monster.name}</h2>
        <p>HP: ${monster.hp}</p>
        <p>DM: ${monster.dm}</p>
        <p>OM: ${monster.om}</p>
        <p>CM: ${monster.cm}</p>
    `;
}*/