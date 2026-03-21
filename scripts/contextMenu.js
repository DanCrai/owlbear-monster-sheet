import { attachMonsterToToken } from "./token.js";
import { getMonsterList } from "./storage.js";

export function setupContextMenu() {
    console.log("Setuping context menu!");
    OBR.contextMenu.create({
        id: "monster-menu",

        icons: [
            {
                icon: "https://dancrai.github.io/owlbear-monster-sheet/context-menu-monster-icon.svg",
                label: "Attach Monster",
                filter: {
                    every: [
                        { key: "layer", value: "CHARACTER" }
                    ]
                }
            }
        ],

        onClick: async (context) => {
            console.log("awaiting monster!");
            const monsters = await getMonsterList();
            console.log("got monster");
            const choice = prompt(
                "Attach monster:\n" + monsters.join("\n")
            );

            if (!choice) return;

            await attachMonsterToToken(context.items, choice);
        }
    });
}