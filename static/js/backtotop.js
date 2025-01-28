// Back to Top Button Functionality
const backToTopButton = document.getElementById("backToTop");

// Show or hide the button based on scroll position
window.addEventListener("scroll", () => {
    if (window.scrollY > 300) { // Show button after 300px scroll
        backToTopButton.style.display = "block";
    } else {
        backToTopButton.style.display = "none";
    }
});

// Smooth scroll to top on button click
backToTopButton.addEventListener("click", () => {
    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });
});
