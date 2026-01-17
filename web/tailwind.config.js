/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'cpliege-blue': '#1e40af',
        'cpliege-orange': '#f97316'
      }
    },
  },
  plugins: [],
}
