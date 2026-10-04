/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        appBg: 'var(--color-appBg)',
        cardBg: 'var(--color-cardBg)',
        cardBorder: 'var(--color-cardBorder)',
        primaryText: 'var(--color-primaryText)',
        secondaryText: 'var(--color-secondaryText)',
        primaryBlue: '#0B5FFF',
        logoAccent: '#F59E0B',
        positiveGreen: '#16A34A',
        negativeRed: '#EF4444',
      },
      fontFamily: {
        inter: ['Inter', 'sans-serif'],
      },
      borderRadius: {
        'card': '16px',
        'btn': '10px',
      },
      boxShadow: {
        'soft': '0 8px 24px rgba(16,24,40,.06)',
        'soft-dark': '0 8px 24px rgba(0,0,0,.2)',
      }
    },
  },
  plugins: [],
}
