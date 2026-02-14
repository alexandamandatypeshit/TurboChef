module.exports = {
  content: ["src/**/*.{html,md,njk}"],
  theme: {
    extend: {
      colors: {
        accent: '#D97706'
      }
    }
  },
  plugins: [require('@tailwindcss/typography')]
}
