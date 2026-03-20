import { attachMonsterToToken } from "./token.js";
import { getMonsterList } from "./storage.js";

export function setupContextMenu() {
    OBR.contextMenu.create({
        id: "monster-menu",
        icons: [],
        onClick: async (context) => {
            const monsters = await getMonsterList();

            const choice = prompt(
                "Attach monster:\n" + monsters.join("\n")
            );

            if (!choice) return;

            attachMonsterToToken(context.items, choice);
        }
    });
}