/* Carousel */
const track = document.querySelector('.carousel-track');
const indicators = document.querySelectorAll('.indicator');
let currentSlide = 0;
const totalSlides = document.querySelectorAll('.card').length;
let autoSlideInterval;

// Update the carousel position
const updateCarousel = (index) => {
    const offset = index * -100;
    track.style.transform = `translateX(${offset}%)`;

    // Update active indicator
    indicators.forEach((ind, i) => {
        ind.classList.toggle('active', i === index);
    });
};

// Go to next slide
const nextSlide = () => {
    currentSlide = (currentSlide + 1) % totalSlides;
    updateCarousel(currentSlide);
};

// Go to previous slide (optional for swipe gesture)
const prevSlide = () => {
    currentSlide = (currentSlide - 1 + totalSlides) % totalSlides;
    updateCarousel(currentSlide);
};

// Add click event to indicators
indicators.forEach((indicator, index) => {
    indicator.addEventListener('click', () => {
        currentSlide = index;
        updateCarousel(currentSlide);
    });
});

// Add swipe functionality
let startX = 0;
let isSwiping = false;

track.addEventListener('touchstart', (e) => {
    startX = e.touches[0].clientX;
    isSwiping = true;
});

track.addEventListener('touchmove', (e) => {
    if (!isSwiping) return;
    const diffX = e.touches[0].clientX - startX;

    if (diffX > 50) {
        prevSlide(); // Swipe right
        isSwiping = false;
    } else if (diffX < -50) {
        nextSlide(); // Swipe left
        isSwiping = false;
    }
});

track.addEventListener('touchend', () => {
    isSwiping = false;
});

// Auto-slide every 5 seconds
const startAutoSlide = () => {
    autoSlideInterval = setInterval(nextSlide, 5000);
};

// Stop auto-slide on interaction
const stopAutoSlide = () => {
    clearInterval(autoSlideInterval);
};

// Start the carousel
updateCarousel(currentSlide);
startAutoSlide();

// Pause auto-slide when interacting with the carousel
document.querySelector('.carousel').addEventListener('mouseover', stopAutoSlide);
document.querySelector('.carousel').addEventListener('mouseout', startAutoSlide);

/* Portfolio text image overlay */

document.querySelectorAll('.portfolio-image').forEach(image => {
    image.addEventListener('mousemove', e => {
        const bounds = image.getBoundingClientRect();
        const x = e.clientX - bounds.left;
        const half = bounds.width / 2;

        if (x < half) {
            image.querySelector('.tech-overlay').style.opacity = '1';
            image.querySelector('.tech-overlay').style.transform = 'translateX(0)';
            image.querySelector('.desc-overlay').style.opacity = '0';
            image.querySelector('.desc-overlay').style.transform = 'translateX(100%)';
        } else {
            image.querySelector('.desc-overlay').style.opacity = '1';
            image.querySelector('.desc-overlay').style.transform = 'translateX(0)';
            image.querySelector('.tech-overlay').style.opacity = '0';
            image.querySelector('.tech-overlay').style.transform = 'translateX(-100%)';
        }
    });

    image.addEventListener('mouseleave', () => {
        image.querySelector('.tech-overlay').style.opacity = '0';
        image.querySelector('.tech-overlay').style.transform = 'translateX(-100%)';
        image.querySelector('.desc-overlay').style.opacity = '0';
        image.querySelector('.desc-overlay').style.transform = 'translateX(100%)';
    });
});
