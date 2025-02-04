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
