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