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

function makeSection(title, content, defaultOpen = true) {
    const id = "sec_" + Math.random().toString(36).substring(2, 9);

    return `
        <div class="section">
            <div class="section-header" data-target="${id}" style="cursor:pointer; font-weight:bold;">
                ▶ ${title}
            </div>
            <div id="${id}" style="display:${defaultOpen ? "block" : "none"}; margin-top:5px;">
                ${content}
            </div>
        </div>
    `;
}

function formatMod(stat) {
    if (stat === undefined || stat === null) return "";
    let mod = Math.floor((stat - 10) / 2);
    return mod >= 0 ? `+${mod}` : `${mod}`;
}

export function setupPanel() {
    const sheet = document.getElementById("sheet");
    if (!sheet) return;

    OBR.player.getRole().then((role) => {
        if (role !== "GM") {
            sheet.innerHTML = "<i>DM only</i>";
            return;
        }

        // Only GM gets updates
        OBR.player.onChange(() => {
            updatePanel();
        });

        updatePanel();
    });
}

function formatEffects(effects) {
    if (!effects || effects.length === 0) return "";

    const parts = effects.map(e => {
        if (e.stacks !== undefined) {
            return `${e.type}(${e.stacks})`;
        } else if (e.value !== undefined && e.duration !== undefined) {
            return `${e.type} [${e.value} x ${e.duration}]`;
        }
        return e.type;
    });

    return `<div class="effects">Effects: ${parts.join(", ")}</div>`;
}

function renderPassives(passives) {
    if (!passives || passives.length === 0) return "";

    return `
        <div class="section">
            <h4>Passives</h4>
            ${passives.map(p => `
                <div class="ability">
                    <div><strong>${p.name}</strong> (passive)</div>
                    ${p.desc ? `<div class="desc">${p.desc}</div>` : ""}
                    <div>
                        ${p.type === "add"
            ? `+${p.value} OM per turn`
            : `x${p.value} total OM`}
                    </div>
                </div>
            `).join("")}
        </div>
    `;
}

export async function updatePanel() {
    const role = await OBR.player.getRole();
    if (role !== "GM") return;

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

    //  TOP SECTION 
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

    let hp = 0;
    if (token.metadata) {
        hp = token.metadata.hp;
    }
    console.log("Hp is: " + hp);
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

            //  STATS SECTION 
            const statsSection = `
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

${m.attributes ? `
<p>
<b>STR</b> ${m.attributes.str} (${formatMod(m.attributes.str)}) &nbsp;
<b>DEX</b> ${m.attributes.dex} (${formatMod(m.attributes.dex)}) &nbsp;
<b>CON</b> ${m.attributes.con} (${formatMod(m.attributes.con)}) &nbsp;<br/>
<b>INT</b> ${m.attributes.int} (${formatMod(m.attributes.int)}) &nbsp;
<b>WIS</b> ${m.attributes.wis} (${formatMod(m.attributes.wis)}) &nbsp;
<b>WILL</b> ${m.attributes.will} (${formatMod(m.attributes.will)}) &nbsp;
<b>CHA</b> ${m.attributes.cha} (${formatMod(m.attributes.cha)})
</p>
` : ""}

${m.saving_throws && Object.keys(m.saving_throws).length ? `
<p><b>Saving Throws:</b> 
${Object.entries(m.saving_throws).map(([k, v]) => `${k} +${v}`).join(", ")}
</p>
` : ""}

${m.skills && Object.keys(m.skills).length ? `
<p><b>Skills:</b> 
${Object.entries(m.skills).map(([k, v]) => `${k} +${v}`).join(", ")}
</p>
` : ""}

${m.senses?.length ? `
<p><b>Senses:</b> ${m.senses.join(", ")}</p>
` : ""}

<p><b>Might:</b> ${m.might} 
(OM: ${m.om || "-"} / DM: ${m.dm || "-"} / CM: ${m.cm || "-"})</p>
`;

            //  DEFENSE SECTION 
            const defenseSection = `
<p><b>Resist:</b> ${m.resistances?.join(", ") || "-"}</p>
<p><b>Immune:</b> ${m.immunities?.join(", ") || "-"}</p>
<p><b>Vulnerable:</b> ${m.vulnerabilities?.join(", ") || "-"}</p>
<p><b>Absorb:</b> ${m.absorb?.join(", ") || "-"}</p>
<p><b>Frail:</b> ${m.frail?.join(", ") || "-"}</p>

<p>
<b>AP:</b>
Start ${m.starting_ap ?? "-"} | 
Recovery ${m.recovery_ap ?? "-"} | 
Max ${m.max_ap ?? "-"}
</p>
`;

            //  ABILITIES + PASSIVES 
            const abilitiesSection = `
${m.abilities.map(ab => `
<div style="margin-bottom:8px;">
    <b>${ab.name}</b> (${ab.ap || "-"} AP${ab.cooldown ? `; CD ${ab.cooldown}` : ""})<br/>

    ${ab.damage ? `[${ab.damage}] ${ab.damage_type || ""}<br/>` : ""}

    ${ab.hit_type === "attack" ? `+${ab.hit_value} to hit<br/>` : ""}
    ${ab.hit_type === "save" ? `DC ${ab.hit_value} ${ab.damage_type || ""}<br/>` : ""}

    ${ab.range ? `Range: ${ab.range} ft<br/>` : ""}

    ${ab.desc ? `${ab.desc}<br/>` : ""}

    ${formatEffects(ab.effects)}
</div>
`).join("")}

${m.passives?.map(p => `
<div style="margin-bottom:8px;">
    <b>${p.name}</b> (passive)<br/>
    ${p.desc ? `${p.desc}<br/>` : ""}
    ${p.type === "add"
                    ? `+${p.value} OM per turn`
                    : `x${p.value} total OM`}
</div>
`).join("") || ""}
`;

            html += `
<div class="sheet">
    ${makeSection("Stats", statsSection, true)}
    ${makeSection("Defenses", defenseSection, false)}
    ${makeSection("Abilities & Passives", abilitiesSection, true)}
</div>
`;
        }
    }

    sheet.innerHTML = html;

    //  COLLAPSIBLE LOGIC 
    document.querySelectorAll(".section-header").forEach(header => {
        header.onclick = () => {
            const target = document.getElementById(header.dataset.target);
            const isOpen = target.style.display === "block";

            target.style.display = isOpen ? "none" : "block";
            header.textContent = (isOpen ? "▶ " : "▼ ") + header.textContent.slice(2);
        };
    });

    //  HP MANUAL EDIT 
    document.getElementById("hpInput").onchange = async (e) => {
        const newHp = Number(e.target.value);

        await OBR.scene.items.updateItems([token.id], (items) => {
            items[0].metadata.monsterSheet.hp = newHp;
        });

        updatePanel();
    };

    //  APPLY DAMAGE 
    document.getElementById("applyDmg").onclick = async () => {
        const dmg = Number(document.getElementById("dmgInput").value);
        const type = document.getElementById("dmgType").value;

        if (!dmg || dmg <= 0) return;

        const newHp = calculateDamage(monsterMeta, dmg, type, hp);

        await OBR.scene.items.updateItems([token.id], (items) => {
            //items[0].metadata.monsterSheet.hp = newHp;
            items[0].metadata.hp = newHp;
        });

        updatePanel();
    };

    //  DROPDOWN EVENT 
    document.getElementById("monsterDropdown").onchange = async (e) => {
        const value = e.target.value;
        if (!value) return;

        await assignMonsterToToken(token.id, value);
        updatePanel();
    };
}

function calculateDamage(monsterMeta, dmg, type, currentHp) {
    const m = monsterMeta.data;

    let final = dmg;

    //  RESIST / IMMUNE / VULN 
    const resist = m.resistances || [];
    const immune = m.immunities || [];
    const vuln = m.vulnerabilities || [];
    const absorb = m.absorb || [];
    const frail = m.frail || [];

    if (immune.includes(type)) {
        final = 0;
    } else if (absorb.includes(type)) {
        final *= -1;
    } else if (frail.includes(type)) {
        final *= 4;
    } else {
        if (resist.includes(type)) final *= 0.5;
        if (vuln.includes(type)) final *= 2;
    }

    //  ARMOR (PA / MA) 
    const category = DAMAGE_TYPES[type]; // physical / magical

    if (category === "physical") {
        final = final - (m.pa || 0);
    } else {
        final = final - (m.ma || 0);
    }

    final = Math.max(0, Math.floor(final));

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