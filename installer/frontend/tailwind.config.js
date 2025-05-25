/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        'alata': ['Alata', 'sans-serif'],
        'roboto-slab': ['Roboto Slab', 'serif'],
      },
      colors: {
        'thinkube': {
          50: '#e6f2f5',
          100: '#cce5eb',
          200: '#99cbd7',
          300: '#80d4e6',
          400: '#4db3cc',
          500: '#008fb3',
          600: '#006680',
          700: '#004d5c',
          800: '#003340',
          900: '#001a20',
        }
      }
    },
  },
  plugins: [
    require('daisyui'),
  ],
  daisyui: {
    themes: [
      {
        thinkube: {
          "primary": "#006680",
          "primary-content": "#ffffff",
          "secondary": "#4db3cc",
          "secondary-content": "#ffffff",
          "accent": "#80d4e6",
          "accent-content": "#001a20",
          "neutral": "#2a323c",
          "neutral-content": "#a6adbb",
          "base-100": "#ffffff",
          "base-200": "#f2f2f2",
          "base-300": "#e5e6e6",
          "base-content": "#1f2937",
          "info": "#2196F3",
          "success": "#4CAF50",
          "warning": "#FFC107",
          "error": "#FF5252",
        },
        thinkubeDark: {
          "primary": "#006680",
          "primary-content": "#ffffff",
          "secondary": "#4db3cc",
          "secondary-content": "#ffffff",
          "accent": "#80d4e6",
          "accent-content": "#001a20",
          "neutral": "#1d232a",
          "neutral-content": "#a6adbb",
          "base-100": "#1d232a",
          "base-200": "#191e24",
          "base-300": "#15191e",
          "base-content": "#a6adbb",
          "info": "#2196F3",
          "success": "#4CAF50",
          "warning": "#FFC107",
          "error": "#FF5252",
        }
      }
    ],
  },
}