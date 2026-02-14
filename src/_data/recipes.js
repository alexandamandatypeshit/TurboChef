const fs = require('fs');
const path = require('path');

module.exports = function() {
  // Dynamically find all recipe markdown files
  const walk = (dir) => {
    let results = [];
    fs.readdirSync(dir).forEach(file => {
      const full = path.join(dir, file);
      if (fs.statSync(full).isDirectory()) results = results.concat(walk(full));
      else if (file.endsWith('.md')) results.push(full);
    });
    return results;
  };
  const recipeFiles = walk(path.join(__dirname, '..', 'recipes'));
  const recipes = recipeFiles.map(file => {
    const content = fs.readFileSync(file, 'utf8');
    const match = content.match(/---([\s\S]*?)---/);
    if (!match) return null;
    const frontmatter = match[1];
    const data = {};
    frontmatter.split('\n').forEach(line => {
      const [key, ...rest] = line.split(':');
      if (!key.trim()) return;
      const value = rest.join(':').trim();
      if (key.trim() === 'tags') {
        data.tags = [];
      } else if (key.trim() && value) {
        data[key.trim()] = value;
      }
    });
    // crude tags parse
    if (frontmatter.includes('tags:')) {
      const tags = [];
      let tagLines = frontmatter.split('tags:')[1].split('\n');
      for (let l of tagLines) {
        if (l.trim().startsWith('- ')) tags.push(l.trim().slice(2));
        else break;
      }
      data.tags = tags;
    }
    // crude excerpt
    let excerpt = '';
    if (content.split('---').length > 2) {
      excerpt = content.split('---')[2].replace(/\n/g, ' ').slice(0, 120).trim();
    }
    return {
      title: data.title || '',
      section: data.section || '',
      tags: data.tags || [],
      url: file.replace(/.*src/, '').replace(/\\/g, '/').replace('.md', '/'),
      excerpt
    };
  }).filter(Boolean);
  return recipes;
};
