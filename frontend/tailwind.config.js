/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Montserrat', 'Pretendard', 'sans-serif'],
      },
      colors: {
        primary: {
          50: '#F5F9FC',
          100: '#EAF3F9',
          200: '#CDE3F3',
          300: '#A4CBE6',
          400: '#7AAEDA',
          500: '#507B9B', // Base Color
          600: '#406585',
          700: '#324F6A',
          800: '#273C50',
          900: '#1D2A37',
        }
      }
    },
  },
  plugins: [],
}