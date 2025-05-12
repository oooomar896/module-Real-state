/** @odoo-module **/

import { registry } from "@web/core/registry";

console.log("Custom JS Loaded");

registry.category("actions").add("custom_action", {
    name: "My Custom Action",
    async execute(env) {
        alert("This is a custom JS action in Odoo 18!");
    },
});

// إضافة وظيفة جديدة لإظهار/إخفاء عنصر
document.addEventListener("DOMContentLoaded", function() {
    const toggleButton = document.getElementById("toggleButton");
    const content = document.getElementById("toggleContent");

    toggleButton.addEventListener("click", function() {
        content.classList.toggle("hidden");
    });
});
