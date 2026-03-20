let currentMonster = null;

// Attach JSON to selected token
async function attachToToken() {
    const text = document.getElementById("jsonInput").value;

    if (!text) {
        alert("Paste JSON first");
        return;
    }

    const monster = JSON.parse(text);

    const selected = await OBR.scene.items.getSelection();

    if (selected.length === 0) {
        alert("Select a token first");
        return;
    }

    await OBR.scene.items.updateItems(selected, (items) => {
        for (let item of items) {
            item.metadata["monster"] = monster;
        }
    });

    alert("Monster attached!");
}

// Show sheet
async function showSheet() {
    const selected = await OBR.scene.items.getSelection();
    if (selected.length === 0) return;

    const item = selected[0];
    const monster = item.metadata["monster"];

    if (!monster) {
        document.getElementById("sheet").innerHTML = "No monster";
        return;
    }

    currentMonster = monster;

    document.getElementById("sheet").innerHTML = `
    <h2>${monster.name}</h2>
    <p>HP: ${monster.hp}</p>
    <p>DM: ${monster.dm}</p>
    <p>OM: ${monster.om}</p>
    <p>CM: ${monster.cm}</p>
  `;
}

// Damage button
async function damage() {
    if (!currentMonster) return;

    currentMonster.hp -= 10;

    const selected = await OBR.scene.items.getSelection();
    const item = selected[0];

    await OBR.scene.items.updateItems([item.id], (items) => {
        items[0].metadata["monster"] = currentMonster;

        items[0].bar1 = {
            value: currentMonster.hp,
            max: currentMonster.hp
        };
    });

    showSheet();
}