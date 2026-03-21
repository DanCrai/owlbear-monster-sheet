import { getMonsterList } from "./storage.js";
import { getSelectedToken, getSelectedMonsterData, assignMonsterToToken } from "./token.js";

export function setupPanel() {
    updatePanel();

    OBR.player.onChange(() => {
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
        <div style="display:flex; gap:10px; align-items:center;">
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

    // --- SHEET ---
    if (monsterMeta.data) {
        const m = monsterMeta.data;

        html += `
            <h3>${m.name}</h3>
            <p>HP: ${m.hp}</p>
            <p>DM: ${m.dm}</p>
            <p>OM: ${m.om}</p>
            <p>CM: ${m.cm}</p>
        `;
    } else {
        html += `<p>No monster selected</p>`;
    }

    sheet.innerHTML = html;

    // --- DROPDOWN EVENT ---
    document.getElementById("monsterDropdown").onchange = async (e) => {
        const value = e.target.value;
        if (!value) return;

        await assignMonsterToToken(token.id, value);
        updatePanel();
    };
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