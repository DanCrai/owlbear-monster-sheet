/*import OBR from "https://cdn.jsdelivr.net/npm/@owlbear-rodeo/sdk@latest/+esm";
console.log("MAIN JS LOADED");
OBR.onReady(() => {
    // Create a simple UI panel
    const div = document.createElement("div");
    div.style.padding = "10px";
    div.style.color = "white";
    div.innerHTML = `
    <h3>Monster Sheet</h3>
    <button id="testBtn">Test Button</button>
  `;

    document.body.appendChild(div);

    document.getElementById("testBtn").onclick = () => {
        alert("Extension is working!");
    };
});*/

import OBR from "https://cdn.jsdelivr.net/npm/@owlbear-rodeo/sdk@latest/+esm";
import { setupContextMenu } from "./scripts/contextMenu.js";
import { setupPanel } from "./scripts/panel.js";

console.log("MAIN JS LOADED");

window.OBR = OBR;

OBR.onReady(() => {
    console.log("OBR READY");
    window.OBR_READY = true;

    setupContextMenu();
    setupPanel();
});