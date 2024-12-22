$(document).ready(function() {
    $("a").on('click', function(event) {
        if (this.hash !== "") {
            event.preventDefault();
            var hash = this.hash;
            $('html, body').animate({
                scrollTop: $(hash).offset().top
            }, 800);
        }
    });

    $(window).scroll(function() {
        if ($(this).scrollTop() > 200) {
            $("#backToTop").fadeIn();
        } else {
            $("#backToTop").fadeOut();
        }
    });

    $("#backToTop").click(function() {
        $("html, body").animate({ scrollTop: 0 }, 800);
    });
});

const words = ["Tech Enthusiast", "Coder", "Developer", "Problem Solver", "Innovator"];
let i = 0;
let j = 0;
let isDeleting = false;
const speed = 100;
const pauseTime = 1500;

function typeWriter() {
    const dynamicText = document.querySelector(".dynamic-text");
    const cursor = document.querySelector(".cursor");
    let currentWord = words[i];
    let displayText = currentWord.slice(0, j);

    dynamicText.textContent = displayText;

    if (!isDeleting && j < currentWord.length) {
        j++;
        setTimeout(typeWriter, speed);
    } else if (isDeleting && j > 0) {
        j--;
        setTimeout(typeWriter, speed);
    } else if (!isDeleting && j === currentWord.length) {
        setTimeout(() => {
            isDeleting = true;
            setTimeout(typeWriter, speed);
        }, pauseTime);
    } else if (isDeleting && j === 0) {
        isDeleting = false;
        i = (i + 1) % words.length;
        setTimeout(typeWriter, speed);
    }
}
typeWriter();

document.addEventListener("DOMContentLoaded", function() {
    const lines = document.querySelectorAll(".about-me-content .line");
    const typingSpeed = 25;
    const pauseTime = 1000;
    
    function typeLine(line, typingSpeed) {
        line.style.opacity = 1;
        let text = line.getAttribute('data-text');
        line.textContent = '';
        let i = 0;

        function type() {
            if (i < text.length) {
                line.textContent += text.charAt(i);
                i++;
                setTimeout(type, typingSpeed);
            }
        }

        type();
    }

    function typeAllLines() {
        lines.forEach(line => {
            typeLine(line, typingSpeed);
        });
    }

    const aboutSection = document.getElementById("about");
    let observerTriggered = false;
    
    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                if (!observerTriggered) {
                    observerTriggered = true;
                    typeAllLines();
                }
            }
        });
    }, { threshold: 0.5 });

    observer.observe(aboutSection);
});
