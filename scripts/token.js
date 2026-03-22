import { loadMonster } from "./storage.js";

let selectedIds = [];

export function setupSelectionListener() {
    OBR.player.onChange((player) => {
        selectedIds = player.selection || [];
    });
}

export async function getSelectedToken() {
    if (selectedIds.length === 0) return null;

    const items = await OBR.scene.items.getItems((item) =>
        selectedIds.includes(item.id)
    );

    return items[0] || null;
}

// MARK TOKEN AS TRACKED
export async function markTokenAsTracked(items) {
    await OBR.scene.items.updateItems(items, (updated) => {
        for (let item of updated) {
            item.metadata["monsterSheet"] = item.metadata["monsterSheet"] || {};
        }
    });
}

// ASSIGN MONSTER FROM DROPDOWN
export async function assignMonsterToToken(tokenId, fileName) {
    const monster = await loadMonster(fileName);

    await OBR.scene.items.updateItems([tokenId], (items) => {
        const item = items[0];

        item.metadata["monsterSheet"] = {
            name: monster.name,
            file: fileName,
            data: monster,
            hp: monster.hp
        };
    });
}

export async function getSelectedMonsterData() {
    const token = await getSelectedToken();
    if (!token) return null;

    return token.metadata?.monsterSheet || null;
}

/*import { loadMonster } from "./storage.js";

let selectedIds = [];

export function setupSelectionListener() {
    // Track selection changes
    OBR.player.onChange((player) => {
        selectedIds = player.selection || [];
    });
}

export async function getSelectedToken() {
    if (selectedIds.length === 0) return null;

    const items = await OBR.scene.items.getItems((item) =>
        selectedIds.includes(item.id)
    );

    return items[0] || null;
}

export async function getSelectedMonster() {
    const token = await getSelectedToken();
    if (!token) return null;

    return token.metadata?.monster || null;
}

export async function attachMonsterToToken(items, monsterName) {
    const monster = await loadMonster(monsterName);

    await OBR.scene.items.updateItems(items, (updated) => {
        for (let item of updated) {
            item.metadata["monster"] = monster;
        }
    });
}

*//*export async function attachMonsterToToken(items, monsterName) {
    await OBR.scene.items.updateItems(items, (objs) => {
        for (let obj of objs) {
            obj.metadata["monsterName"] = monsterName;
        }
    });

    console.log("Attached:", monsterName);
}

export async function getSelectedMonster() {
    const selected = await OBR.scene.items.getItems({ selected: true });
    if (!selected.length) return null;

    return selected[0].metadata["monsterName"];
}*/