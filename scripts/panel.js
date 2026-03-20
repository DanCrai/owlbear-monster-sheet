import { getSelectedMonster } from "./token.js";

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
}
/*import { getSelectedMonster } from "./token.js";
import { loadMonster } from "./storage.js";

export function setupPanel() {
    const app = document.getElementById("app");
    console.log("app element:", document.getElementById("app"));

    app.innerHTML = `
        <h3>Monster Sheet</h3>
        <div id="sheet">Select a token</div>
    `;

    // Listen to selection changes
    OBR.scene.items.onChange(async () => {
        const monsterName = await getSelectedMonster();

        if (!monsterName) {
            document.getElementById("sheet").innerHTML = "No monster";
            return;
        }

        const monster = await loadMonster(monsterName);

        renderMonster(monster);
    });
}

function renderMonster(monster) {
    document.getElementById("sheet").innerHTML = `
        <h2>${monster.name}</h2>
        <p>HP: ${monster.hp}</p>
        <p>DM: ${monster.dm}</p>
        <p>OM: ${monster.om}</p>
        <p>CM: ${monster.cm}</p>
    `;
}*/