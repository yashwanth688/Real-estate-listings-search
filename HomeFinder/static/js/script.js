document.addEventListener('DOMContentLoaded', function () {

  /* ── 1. Lucide Icons ──────────────────────────────────────── */
  lucide.createIcons();

  /* ── 2. Sticky Navbar shadow on scroll ───────────────────── */
  const navbar = document.getElementById('navbar');
  window.addEventListener('scroll', () => {
    if (window.scrollY > 20) {
      navbar && navbar.classList.add('scrolled');
    } else {
      navbar && navbar.classList.remove('scrolled');
    }
  });

  /* ── 3. Mobile Menu Toggle ───────────────────────────────── */
  const menuBtn = document.getElementById('mobileMenuBtn');
  const navLinks = document.getElementById('navLinks');
  if (menuBtn && navLinks) {
    menuBtn.addEventListener('click', () => {
      navLinks.classList.toggle('active');
    });
    // Close menu when a link is clicked
    navLinks.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => navLinks.classList.remove('active'));
    });
  }

  /* ── 4. Auto-dismiss Flash Messages ─────────────────────── */
  document.querySelectorAll('.alert').forEach(alert => {
    setTimeout(() => {
      alert.style.transition = 'opacity 0.5s, transform 0.5s';
      alert.style.opacity = '0';
      alert.style.transform = 'translateY(-10px)';
      setTimeout(() => alert.remove(), 500);
    }, 5000);
  });

  /* ── 5. Hero Search Tab Switcher ─────────────────────────── */
  window.setTab = function (btn, value) {
    document.querySelectorAll('.search-tab').forEach(t => t.classList.remove('active'));
    btn.classList.add('active');
    const input = document.getElementById('statusInput');
    if (input) input.value = value;
  };

  /* ── 6. Scroll Reveal Animation ─────────────────────────── */
  const revealEls = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry, i) => {
        if (entry.isIntersecting) {
          setTimeout(() => {
            entry.target.classList.add('visible');
          }, i * 80);
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12 });
    revealEls.forEach(el => observer.observe(el));
  } else {
    revealEls.forEach(el => el.classList.add('visible'));
  }

  /* ── 7. Animated Counter ─────────────────────────────────── */
  const counters = document.querySelectorAll('.counter');
  if (counters.length && 'IntersectionObserver' in window) {
    const counterObs = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          animateCounter(entry.target);
          counterObs.unobserve(entry.target);
        }
      });
    }, { threshold: 0.5 });
    counters.forEach(c => counterObs.observe(c));
  }

  function animateCounter(el) {
    const target = parseInt(el.dataset.target);
    const duration = 1500;
    const step = target / (duration / 16);
    let current = 0;
    const timer = setInterval(() => {
      current += step;
      if (current >= target) {
        el.textContent = target + '+';
        clearInterval(timer);
      } else {
        el.textContent = Math.floor(current);
      }
    }, 16);
  }

  /* ── 8. Frontend form validation ────────────────────────── */
  const propertyForm = document.querySelector('form.form-grid');
  if (propertyForm) {
    propertyForm.addEventListener('submit', function (e) {
      const price = parseFloat(this.querySelector('[name="price"]')?.value);
      const area  = parseInt(this.querySelector('[name="area"]')?.value);
      if (isNaN(price) || price <= 0) {
        e.preventDefault();
        showToast('Please enter a valid price greater than zero.', 'error');
      } else if (isNaN(area) || area <= 0) {
        e.preventDefault();
        showToast('Please enter a valid area greater than zero.', 'error');
      }
    });
  }

  /* ── 9. Simple Toast Notification helper ─────────────────── */
  window.showToast = function (msg, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `alert alert-${type}`;
    toast.style.cssText = 'position:fixed;bottom:1.5rem;right:1.5rem;z-index:9999;max-width:360px;animation:slideDown .3s ease;';
    toast.innerHTML = `<span>${msg}</span><button class="close-btn" onclick="this.parentElement.remove()">&times;</button>`;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 4000);
  };

});
