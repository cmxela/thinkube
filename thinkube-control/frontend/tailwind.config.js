// tailwind.config.js
/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
      "./index.html",
      "./src/**/*.{vue,js,ts,jsx,tsx}",
    ],
    theme: {
      extend: {},
    },
    plugins: [require("daisyui")],
    daisyui: {
      themes: [
        {
          light: {
            ...require("daisyui/src/theming/themes")["light"],
            primary: "#3B82F6",
            secondary: "#6B7280",
            accent: "#10B981",
            neutral: "#1F2937",
            "base-100": "#F9FAFB",
          },
          dark: {
            ...require("daisyui/src/theming/themes")["dark"],
            primary: "#3B82F6",
            secondary: "#6B7280",
            accent: "#10B981",
            neutral: "#1F2937",
            "base-100": "#111827",
          },
        },
      ],
      darkTheme: "dark",
    },
  };