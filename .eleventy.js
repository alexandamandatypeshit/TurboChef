const fs = require('fs');
const path = require('path');

module.exports = function(eleventyConfig) {

  eleventyConfig.addPassthroughCopy("src/assets");
  // Output recipes.json for search
  eleventyConfig.on('afterBuild', () => {
    const recipes = require('./src/_data/recipes.js')();
    fs.writeFileSync(path.join(__dirname, '_site', 'recipes.json'), JSON.stringify(recipes, null, 2));
  });

  // English recipes (default)
  eleventyConfig.addCollection("recipes_en", function(collectionApi) {
    return collectionApi.getFilteredByGlob("src/recipes/**/*.md").filter(item => !item.inputPath.endsWith('.fr.md'));
  });
  // French recipes
  eleventyConfig.addCollection("recipes_fr", function(collectionApi) {
    return collectionApi.getFilteredByGlob("src/recipes/**/*.fr.md");
  });

  // NOTE: do not set a global `lang` here — prefer per-page front-matter `lang` and
  // detect language from `page.inputPath` when computing permalinks.

  // Ensure French markdown files are output under /fr/... instead of keeping the ".fr" in filenames
  eleventyConfig.addGlobalData('eleventyComputed', function(data) {
    try {
      if (!data || !data.page || !data.page.inputPath) return {};
      // Don't override an explicit permalink set in front matter
      if (data.permalink) return {};
      // Use the input path or front-matter `lang` to decide whether to prefix with /fr
      const isFrByPath = /\.fr\.(md|njk|html)$/.test(data.page.inputPath || '');
      if (!isFrByPath && data.lang !== 'fr') return {};

      const inputPath = data.page.inputPath;
      // Compute path relative to project src directory and strip extension
      const rel = inputPath.replace(/\\/g, '/').replace(/.*\/src/, '/src');
      const withoutSrc = rel.replace(/^\/src/, '');
      let cleanPath = withoutSrc.replace(/\.(md|njk|html)$/, '');
      // If the source filename includes a language marker like `.fr`, strip it
      // so URLs become /fr/recipes/slug/ rather than /fr/recipes/slug.fr/
      cleanPath = cleanPath.replace(/\.fr$/, '');
      // Remove trailing /index (we want /fr/recipes/foo/ rather than /fr/recipes/foo/index)
      cleanPath = cleanPath.replace(/\/index$/, '');
      if (cleanPath === '') cleanPath = '/';
      if (!cleanPath.startsWith('/')) cleanPath = '/' + cleanPath;
      const permalink = '/fr' + (cleanPath === '/' ? '/' : cleanPath + '/');
      return { permalink };
    } catch (e) {}
    return {};
  });

  // Load keywords from JSON for filter
  let keywords = {};
  try {
    const keywordsPath = path.join(__dirname, 'src', 'assets', 'keywords.json');
    if (fs.existsSync(keywordsPath)) {
      keywords = JSON.parse(fs.readFileSync(keywordsPath, 'utf8'));
    }
  } catch (e) {}

  // Helper to wrap keywords in HTML spans
  function keywordifyStr(str) {
    if (!str || typeof str !== 'string') return str;
    let result = str;
    Object.keys(keywords).forEach(kw => {
      const safeKw = kw.replace(/[-/\\^$*+?.()|[\]{}]/g, '\\$&');
      const re = new RegExp(`\\b(${safeKw})\\b`, 'gi');
      result = result.replace(re, (match) => `<span class="keyword-link" data-keyword="${kw}">${match}</span>`);
    });
    return result;
  }

  eleventyConfig.addNunjucksFilter('keywordify', function(str) {
    return keywordifyStr(str);
  });

  // Pretty-print a step (string or object) into HTML for nicer step UI
  eleventyConfig.addNunjucksFilter('prettyStep', function(step) {
    if (!step) return '';
    // If it's a string, try to split a short title from the rest on the first colon
    if (typeof step === 'string') {
      const idx = step.indexOf(':');
      if (idx !== -1) {
        const title = step.slice(0, idx).trim();
        const body = step.slice(idx + 1).trim();
        return `<div class="step-block"><div class="step-title font-semibold">${keywordifyStr(title)}</div><div class="step-body text-sm text-gray-700 mt-1">${keywordifyStr(body)}</div></div>`;
      }
      return `<div class="step-body text-sm text-gray-700">${keywordifyStr(step)}</div>`;
    }
    // If it's an object/map, iterate keys
    if (typeof step === 'object') {
      let out = '';
      for (const k in step) {
        if (!Object.prototype.hasOwnProperty.call(step, k)) continue;
        const v = step[k];
        out += `<div class="step-block"><div class="step-title font-semibold">${keywordifyStr(k)}</div><div class="step-body text-sm text-gray-700 mt-1">${keywordifyStr(String(v))}</div></div>`;
      }
      return out;
    }
    return String(step);
  });

  return {
    dir: {
      input: "src",
      includes: "_includes",
      data: "_data",
      output: "_site"
    },
    templateFormats: ["md","njk","html"],
    htmlTemplateEngine: "njk"
  };
};
