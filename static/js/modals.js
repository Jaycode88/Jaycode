// Open Modal
document.querySelectorAll('.modal-trigger').forEach(trigger => {
    trigger.addEventListener('click', function (e) {
        e.preventDefault(); // Prevent the default link behavior
        const modalId = this.getAttribute('data-modal'); // Get modal ID
        document.getElementById(modalId).style.display = 'block'; // Show modal
    });
});

// Close Modal
document.querySelectorAll('.close').forEach(closeButton => {
    closeButton.addEventListener('click', function () {
        const modalId = this.getAttribute('data-modal'); // Get modal ID
        document.getElementById(modalId).style.display = 'none'; // Hide modal
    });
});

// Close Modal on Background Click
window.addEventListener('click', function (e) {
    if (e.target.classList.contains('modal')) {
        e.target.style.display = 'none'; // Hide modal
    }
});


// AJAX Form Submission
document.querySelector(".contact-form").addEventListener("submit", function (e) {
    e.preventDefault(); // Prevent the default form submission
    const formData = new FormData(this);

    fetch("/", {
        method: "POST",
        body: formData,
    })
        .then((response) => response.json())
        .then((data) => {
            if (data.status === "success") {
                showFlashMessageModal("Success", data.message, "success");
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
