document.querySelector(".review-form").addEventListener("submit", function (e) {
    e.preventDefault();
    const form = this;
    const formData = new FormData(form);

    fetch("/free-review", {
        method: "POST",
        body: formData,
    })
    .then((res) => res.json())
    .then((data) => {
        showFlashMessageModal(data.status === "success" ? "Success" : "Error", data.message, data.status);
        if (data.status === "success") {
            setTimeout(() => {
                form.reset();
                if (typeof grecaptcha !== "undefined") grecaptcha.reset();
            }, 1000);
        }
    })
    .catch(() => {
        showFlashMessageModal("Error", "Something went wrong. Please try again.", "error");
    });
});

function showFlashMessageModal(title, message, category) {
    const modal = document.getElementById("flashMessageModal");
    document.getElementById("flashMessageTitle").textContent = title;
    document.getElementById("flashMessageText").textContent = message;
    document.getElementById("flashMessageTitle").style.color = category === "success" ? "#4caf50" : "#f44336";
    modal.style.display = "block";
}

function closeModal() {
    document.getElementById("flashMessageModal").style.display = "none";
}

document.addEventListener("DOMContentLoaded", function () {
    const closeBtn = document.querySelector("#flashMessageModal .close");
    if (closeBtn) closeBtn.addEventListener("click", closeModal);
});
