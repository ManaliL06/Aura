/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        aura: {
          gold: "#d4af37",
          goldLight: "#e5c567",
          dark1: "#0b0b0b",
          dark2: "#141414",
          dark3: "#1e1e1e",
          dark4: "#2a2a2a",
        }
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        serif: ['Playfair Display', 'serif'],
      }
    },
  },
  plugins: [],
}
