// Floating recipe tips panel logic
document.addEventListener('DOMContentLoaded', () => {
  const tips = document.getElementById('recipe-tips');
  if (!tips) return;
  const key = `tipsClosed_${location.pathname}`;
  const closeBtn = document.getElementById('tips-close');
  const toggleBtn = document.getElementById('tips-toggle');

  function showTips(animated = true) {
    toggleBtn.style.display = 'none';
    tips.style.display = 'block';
    if (animated) {
      tips.style.transform = 'translateX(20px)';
      tips.style.opacity = '0';
      tips.style.transition = 'transform 240ms ease, opacity 240ms ease';
      requestAnimationFrame(() => {
        tips.style.transform = 'translateX(0)';
        tips.style.opacity = '1';
      });
    } else {
      tips.style.opacity = '1';
      tips.style.transform = 'none';
    }
    localStorage.setItem(key, '0');
    tips.setAttribute('aria-hidden', 'false');
  }

  function hideTips(animated = true) {
    if (animated) {
      tips.style.transform = 'translateX(20px)';
      tips.style.opacity = '0';
      setTimeout(() => { tips.style.display = 'none'; toggleBtn.style.display = 'inline-flex'; }, 240);
    } else {
      tips.style.display = 'none';
      toggleBtn.style.display = 'inline-flex';
    }
    localStorage.setItem(key, '1');
    tips.setAttribute('aria-hidden', 'true');
  }

  // Initialize: show unless closed
  if (localStorage.getItem(key) === '1') {
    tips.style.display = 'none';
    if (toggleBtn) toggleBtn.style.display = 'inline-flex';
  } else {
    showTips(false);
  }

  closeBtn.addEventListener('click', (e) => {
    e.preventDefault();
    hideTips(true);
  });

  if (toggleBtn) {
    toggleBtn.addEventListener('click', (e) => {
      e.preventDefault();
      showTips(true);
    });
  }
});
