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
        `<option value="${m}" ${monsterMeta.name === m ? "selected" : ""}>${m}</option>`
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
        const m = monsterMeta.data;

        html += `
        <div class="sheet">
            <h3>${m.name}</h3>
            <p>HP: ${m.hp}</p>
            <p>DM: ${m.dm}</p>
            <p>OM: ${m.om}</p>
            <p>CM: ${m.cm}</p>
        </div>
    `;

        // abilties
        if (m.abilities && m.abilities.length > 0) {
            html += `<div class="sheet"><h3>Abilities</h3>`;

            for (let ab of m.abilities) {
                html += `
                <div class="ability">
                    <div class="ability-name">${ab.name}</div>
                    ${ab.desc ? `<div class="small">${ab.desc}</div>` : ""}
                    ${ab.damage ? `<div class="small">Damage: ${ab.damage}</div>` : ""}
                    ${ab.ap ? `<div class="small">AP: ${ab.ap}</div>` : ""}
                    ${ab.cooldown ? `<div class="small">CD: ${ab.cooldown}</div>` : ""}
                </div>
            `;
            }

            html += `</div>`;
        }
    } else {
        html += `<p>No monster selected</p>`;
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