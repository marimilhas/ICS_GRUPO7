/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Montserrat'],
      },
      colors: {
        "green-dark": "#134611",
        "green-forest": "#3E8914",
        "green-medium": "#3DA35D",
        "green-light": "#96E072",
        "green-pale": "#E8FCCF",
        "green-dark-bold": "#0d300cff",
        "green-forest-bold": "#2f660fff",
        "green-medium-bold": "#2e7c47ff",
        "green-light-bold": "#77b15aff",
        "green-pale-bold": "#c1d3acff",
      },
    },
  },
  plugins: [],
}

