// This file is used to add recapture to the contact form and submit the form with the token.
document.querySelector(".contact-form").addEventListener("submit", function (e) {
    e.preventDefault(); // Prevent default form submission
    grecaptcha.ready(function () {
        grecaptcha.execute("YOUR_SITE_KEY", { action: "submit" }).then(function (token) {
            // Append token to form data
            const form = document.querySelector(".contact-form");
            const hiddenInput = document.createElement("input");
            hiddenInput.type = "hidden";
            hiddenInput.name = "g-recaptcha-response";
            hiddenInput.value = token;
            form.appendChild(hiddenInput);

            // Submit the form
            form.submit();
        });
    });
});
