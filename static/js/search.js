document.addEventListener("DOMContentLoaded", () => {

    const form = document.querySelector("form");
    const button = document.getElementById("searchBtn");

    if (form && button) {

        form.addEventListener("submit", () => {

            button.disabled = true;

            button.innerHTML = "Searching...";

        });

    }

});