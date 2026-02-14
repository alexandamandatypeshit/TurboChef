// Automatic calorie estimation for recipes
const CALORIE_DB = {};
fetch('/assets/calorie-db.json')
  .then(res => res.json())
  .then(data => Object.assign(CALORIE_DB, data));

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
  const el = document.getElementById('calorie-estimate');
  if (!el) return;
  // Get ingredients from DOM
  const items = Array.from(document.querySelectorAll('ul li')).map(li => li.textContent.trim());
  const { total, details } = estimateCalories(items);
  el.innerHTML = `<b>Estimated Calories (entire recipe):</b> ${total} kcal` +
    (details.length ? `<details style='margin-top:0.5em;'><summary>Breakdown</summary><ul style='margin:0.5em 0 0 1em;'>${details.map(d=>`<li>${d}</li>`).join('')}</ul></details>` : '');
});
