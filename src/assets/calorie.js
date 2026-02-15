// Automatic calorie estimation for recipes
const CALORIE_DB = {};

function parseIngredient(ingredient) {
  // Simple parser: "115g butter" or "2 large eggs"
  const gMatch = ingredient.match(/(\d+)(?:g| grams?)?\s+([a-zA-Z ]+)/);
  if (gMatch) {
    const amount = parseFloat(gMatch[1]);
    const name = gMatch[2].trim().toLowerCase();
    return { name, amount, unit: 'g' };
  }
  const eggMatch = ingredient.match(/(\d+)\s+(?:large |medium |)eggs?/);
  if (eggMatch) {
    return { name: 'egg', amount: parseInt(eggMatch[1]), unit: 'egg' };
  }
  // fallback: try to match by name
  const name = ingredient.replace(/[^a-zA-Z ]/g, '').trim().toLowerCase();
  return { name, amount: 0, unit: '' };
}

function estimateCalories(ingredients) {
  let total = 0;
  let details = [];
  for (const ing of ingredients) {
    const parsed = parseIngredient(ing);
    let cal = 0;
    if (parsed.unit === 'g' && CALORIE_DB[parsed.name]) {
      cal = parsed.amount * CALORIE_DB[parsed.name];
    } else if (parsed.unit === 'egg' && CALORIE_DB['egg']) {
      cal = parsed.amount * CALORIE_DB['egg'];
    }
    if (cal > 0) {
      details.push(`${ing}: ~${Math.round(cal)} kcal`);
    }
    total += cal;
  }
  return { total: Math.round(total), details };
}

window.addEventListener('DOMContentLoaded', function() {
  const el = document.getElementById('calorie-estimate-inline');
  if (!el) return;
  // Load calorie DB then compute using the ingredients in the DOM
  fetch('/assets/calorie-db.json')
    .then(res => res.json())
    .then(data => Object.assign(CALORIE_DB, data))
    .then(() => {
      const items = Array.from(document.querySelectorAll('ul li')).map(li => li.textContent.trim());
      const { total } = estimateCalories(items);
      el.textContent = total && total > 0 ? `${total} kcal` : '—';
    })
    .catch(() => { el.textContent = '—'; });
});
