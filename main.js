import OBR from "https://cdn.jsdelivr.net/npm/@owlbear-rodeo/sdk@latest/+esm";

import { setupContextMenu } from "./scripts/contextMenu.js";
import { setupPanel } from "./scripts/panel.js";
import { setupSelectionListener } from "./scripts/token.js";


console.log("MAIN JS LOADED");
window.OBR = OBR;
OBR.onReady(() => {

    console.log("Monster extension loaded");
    window.OBR_READY = true;
    setupContextMenu();
    setupSelectionListener();

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", setupPanel);
    } else {
        setupPanel();
    }
});

/*
import OBR from "https://cdn.jsdelivr.net/npm/@owlbear-rodeo/sdk@latest/+esm";
import { setupContextMenu } from "./scripts/contextMenu.js";
import { setupPanel } from "./scripts/panel.js";
import { setupSelectionListener } from "./scripts/token.js";

console.log("MAIN JS LOADED");

window.OBR = OBR;

*//*OBR.onReady(() => {
    console.log("OBR READY");
    window.OBR_READY = true;

    setupContextMenu();
    setupPanel();
});*//*

OBR.onReady(() => {
    console.log("Monster extension loaded");
    window.OBR_READY = true;

    setupContextMenu();
    setupSelectionListener(); 

    // Wait for DOM
    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", setupPanel);
    } else {
        setupPanel();
    }
});*/