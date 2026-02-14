// search.js - TurboChef site search

document.addEventListener('DOMContentLoaded', () => {
  const searchBox = document.getElementById('site-search-box');
  const resultsBox = document.getElementById('site-search-results');
  if (!searchBox || !resultsBox) return;

  let recipes = [];

  // Fetch all recipes (title, url, section, tags, excerpt)
  fetch('/recipes.json')
    .then(res => res.json())
    .then(data => { recipes = data; });

  searchBox.addEventListener('input', (e) => {
    const q = e.target.value.trim().toLowerCase();
    if (!q) {
      resultsBox.innerHTML = '';
      resultsBox.style.display = 'none';
      return;
    }
    const matches = recipes.filter(r =>
      r.title.toLowerCase().includes(q) ||
      (r.tags && r.tags.some(tag => tag.toLowerCase().includes(q))) ||
      (r.section && r.section.toLowerCase().includes(q)) ||
      (r.excerpt && r.excerpt.toLowerCase().includes(q))
    ).slice(0, 8);
    if (matches.length === 0) {
      resultsBox.innerHTML = '<div class="p-2 text-gray-500">No results</div>';
      resultsBox.style.display = 'block';
      return;
    }
    resultsBox.innerHTML = matches.map(r =>
      `<a href="${r.url}" class="block px-4 py-2 hover:bg-accent hover:text-white rounded transition">
        <span class="font-bold">${r.title}</span>
        <span class="ml-2 text-xs text-gray-500">${r.section || ''}</span><br>
        <span class="text-xs text-gray-600">${r.excerpt || ''}</span>
      </a>`
    ).join('');
    resultsBox.style.display = 'block';
  });

  // Hide results on blur
  searchBox.addEventListener('blur', () => {
    setTimeout(() => { resultsBox.style.display = 'none'; }, 200);
  });
  searchBox.addEventListener('focus', () => {
    if (resultsBox.innerHTML) resultsBox.style.display = 'block';
  });
});
