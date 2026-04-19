// script.js

document.addEventListener("DOMContentLoaded", () => {
  // 1. Smooth Scrolling for Navbar Links
  const navLinks = document.querySelectorAll('nav a, .btn-primary[href^="#"]');

  navLinks.forEach((link) => {
    link.addEventListener("click", function (e) {
      const targetId = this.getAttribute("href");

      // Only do smooth scrolling if the link is an internal anchor
      if (targetId && targetId.startsWith("#")) {
        if (targetId === "#") return;

        const targetElement = document.querySelector(targetId);
        if (targetElement) {
          e.preventDefault();
          // Offset for fixed navbar
          const navbarHeight = document.querySelector(".navbar").offsetHeight;
          const elementPosition = targetElement.getBoundingClientRect().top;
          const offsetPosition =
            elementPosition + window.pageYOffset - navbarHeight;

          window.scrollTo({
            top: offsetPosition,
            behavior: "smooth",
          });
        }
      }
    });
  });

  // 2. Intersection Observer for Fade-In Animations
  const fadeElements = document.querySelectorAll(".fade-in-section");

  const appearOptions = {
    threshold: 0, // Trigger as soon as 0% of the element is visible, fixing tall elements
    rootMargin: "0px 0px -50px 0px",
  };

  const appearOnScroll = new IntersectionObserver(function (entries, observer) {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) {
        return;
      } else {
        entry.target.classList.add("is-visible");
        observer.unobserve(entry.target);
      }
    });
  }, appearOptions);

  fadeElements.forEach((el) => {
    appearOnScroll.observe(el);
  });

  // 3. Navbar scroll effect (shrink/shadow)
  const navbar = document.querySelector(".navbar");
  window.addEventListener("scroll", () => {
    if (window.scrollY > 50) {
      navbar.style.padding = "0.5rem 5%";
      navbar.style.boxShadow = "0 10px 15px rgba(0, 0, 0, 0.1)";
    } else {
      navbar.style.padding = "1rem 5%";
      navbar.style.boxShadow = "0 4px 6px rgba(0, 0, 0, 0.05)";
    }
  });
});
