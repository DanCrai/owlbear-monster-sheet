export async function attachMonsterToToken(items, monsterName) {
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
}