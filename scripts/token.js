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

/*export async function attachMonsterToToken(items, monsterName) {
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