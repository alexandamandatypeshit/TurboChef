module.exports = {
  content: [
    './src/**/*.njk',
    './src/**/*.md',
    './src/**/*.html',
    './src/_includes/**/*.njk',
    './src/_includes/**/*.html',
    './src/index.md',
  ],
  theme: {
    extend: {
      colors: {
        accent: '#fbbf24',
      },
    },
  },
  plugins: [],
};
