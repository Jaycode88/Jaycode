// AJAX Form Submission
document.querySelector(".contact-form").addEventListener("submit", function (e) {
    e.preventDefault(); // Prevent the default form submission
    const form = this;  // Define the form element
    const formData = new FormData(form);

    fetch("/", {
        method: "POST",
        body: formData,
    })
        .then((response) => response.json())
        .then((data) => {
            if (data.status === "success") {
                showFlashMessageModal("Success", data.message, "success");

                // RESET FORM AFTER SUCCESSFUL SUBMISSION
                setTimeout(() => {
                    form.reset();  // Clears input fields
                    grecaptcha.reset(); // Reset the reCAPTCHA after success
                }, 1000);  // Delay to allow user to see the success message

            } else {
                showFlashMessageModal("Error", data.message, "error");
            }
        })
        .catch((error) => {
            showFlashMessageModal("Error", "An unexpected error occurred.", "error");
            console.error("Error:", error);
        });
});

// Show Flash Message Modal
function showFlashMessageModal(title, message, category) {
    const modal = document.getElementById("flashMessageModal");
    const titleElement = document.getElementById("flashMessageTitle");
    const messageElement = document.getElementById("flashMessageText");

    titleElement.textContent = title;
    messageElement.textContent = message;

    // Style based on category
    titleElement.style.color = category === "success" ? "#4caf50" : "#f44336";

    modal.style.display = "block";
}

// Close Modal
function closeModal() {
    document.getElementById("flashMessageModal").style.display = "none";
}


// Ensure the reset button also resets reCAPTCHA
document.querySelector(".reset-button").addEventListener("click", function () {
    const form = document.querySelector(".contact-form");
    form.reset(); // Reset form fields

    // Check if reCAPTCHA exists before attempting to reset
    if (typeof grecaptcha !== "undefined") {
        grecaptcha.reset(); // Reset reCAPTCHA
    }
});
