const BASE_URL = "https://dancrai.github.io/owlbear-monster-sheet/monsters/";

export async function getMonsterList() {
    const res = await fetch(BASE_URL + "monsterList.json");
    return await res.json(); // returns full objects now
}

export async function loadMonster(fileName) {
    const res = await fetch(BASE_URL + fileName);
    return await res.json();
}