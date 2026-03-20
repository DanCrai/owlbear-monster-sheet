const BASE_URL = "https://dancrai.github.io/owlbear-monster-sheet/monsters/";

export async function getMonsterList() {
    // For now hardcoded (GitHub can't list directory easily)
    return ["goblin", "dragon"];
}

export async function loadMonster(name) {
    const res = await fetch(BASE_URL + name + ".json");
    return await res.json();
}