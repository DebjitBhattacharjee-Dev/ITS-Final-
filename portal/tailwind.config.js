/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        surface: {
          950: '#0b0f17',
          900: '#111827',
          850: '#151e30',
          800: '#1f2937',
          700: '#374151',
          600: '#4b5563',
        },
        brand: {
          blue: '#2563eb',
          light: '#38bdf8',
          accent: '#1d4ed8'
        }
      }
    },
  },
  plugins: [],
}
