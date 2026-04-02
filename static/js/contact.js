document.addEventListener("DOMContentLoaded", function () {
    const forms = document.querySelectorAll(".contact-form");

    forms.forEach((form) => {
        form.addEventListener("submit", function (e) {
            e.preventDefault();

            const formData = new FormData(form);
            const action = form.getAttribute("action") || window.location.pathname;

            fetch(action, {
                method: "POST",
                body: formData,
            })
                .then((response) => response.json())
                .then((data) => {
                    if (data.status === "success") {
                        showFlashMessageModal("Success", data.message, "success");

                        setTimeout(() => {
                            form.reset();

                            if (typeof grecaptcha !== "undefined") {
                                grecaptcha.reset();
                            }
                        }, 1000);
                    } else {
                        showFlashMessageModal("Error", data.message, "error");
                    }
                })
                .catch((error) => {
                    showFlashMessageModal("Error", "An unexpected error occurred.", "error");
                    console.error("Error:", error);
                });
        });
    });

    const resetButtons = document.querySelectorAll(".reset-button");

    resetButtons.forEach((button) => {
        button.addEventListener("click", function () {
            const form = button.closest("form");

            if (form) {
                form.reset();
            }

            if (typeof grecaptcha !== "undefined") {
                grecaptcha.reset();
            }
        });
    });

    const closeButton = document.querySelector("#flashMessageModal .close");
    if (closeButton) {
        closeButton.addEventListener("click", closeModal);
    }
});

function showFlashMessageModal(title, message, category) {
    const modal = document.getElementById("flashMessageModal");
    const titleElement = document.getElementById("flashMessageTitle");
    const messageElement = document.getElementById("flashMessageText");

    if (!modal || !titleElement || !messageElement) {
        alert(message);
        return;
    }

    titleElement.textContent = title;
    messageElement.textContent = message;
    titleElement.style.color = category === "success" ? "#4caf50" : "#f44336";

    modal.style.display = "block";
}

function closeModal() {
    const modal = document.getElementById("flashMessageModal");
    if (modal) {
        modal.style.display = "none";
    }
}