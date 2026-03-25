import { markTokenAsTracked } from "./token.js";
import { updatePanel } from "./panel.js";

export function setupContextMenu() {
    OBR.contextMenu.create({
        id: "monster-menu",
        icons: [
            {
                icon: "https://dancrai.github.io/owlbear-monster-sheet/context-menu-monster-icon-original.svg",
                label: "Attach Monster",
                filter: {
                    every: [
                        { key: "layer", value: "CHARACTER" },
                        () => OBR.player.role === "GM"
                    ]
                }
            }
        ],
        onClick: async (context) => {
            await markTokenAsTracked(context.items);

            updatePanel();

            /*OBR.popover.open({
                id: "monster-sheet",
                url: window.location.href,
                height: 400,
                width: 300
            });*/
        }
    });
}
