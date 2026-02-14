const fs = require('fs');
const path = require('path');

module.exports = function(eleventyConfig) {

  eleventyConfig.addPassthroughCopy("src/assets");
  // Output recipes.json for search
  eleventyConfig.on('afterBuild', () => {
    const recipes = require('./src/_data/recipes.js')();
    fs.writeFileSync(path.join(__dirname, '_site', 'recipes.json'), JSON.stringify(recipes, null, 2));
  });

  eleventyConfig.addCollection("recipes", function(collectionApi) {
    return collectionApi.getFilteredByGlob("src/recipes/**/*.md");
  });

  // Load keywords from JSON for filter
  let keywords = {};
  try {
    const keywordsPath = path.join(__dirname, 'src', 'assets', 'keywords.json');
    if (fs.existsSync(keywordsPath)) {
      keywords = JSON.parse(fs.readFileSync(keywordsPath, 'utf8'));
    }
  } catch (e) {}

  eleventyConfig.addNunjucksFilter('keywordify', function(str) {
    if (!str || typeof str !== 'string') return str;
    let result = str;
    Object.keys(keywords).forEach(kw => {
      // Only match whole words, case-insensitive
      const re = new RegExp(`\\b(${kw.replace(/[-/\\^$*+?.()|[\]{}]/g, '\\$&')})\\b`, 'gi');
      result = result.replace(re, (match) => `<span class="keyword-link" data-keyword="${kw}">${match}</span>`);
    });
    return result;
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
