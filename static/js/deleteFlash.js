document.addEventListener('DOMContentLoaded', function () {
    // Get the flash element
    const flashElements = document.querySelectorAll('.flash');

    // Set a timeout to remove the element after 7 seconds (same duration as the animation)
    flashElements.forEach(function (flashElement) {
        setTimeout(function () {
            flashElement.remove();
        }, 6500); // 7 seconds in milliseconds
    });
});
