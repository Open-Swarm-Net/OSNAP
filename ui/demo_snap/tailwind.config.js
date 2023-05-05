/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  daisyui: {
    themes: [
      {
        mytheme: {
        
          "primary": "#a78bfa",
          "secondary": "#9333ea",
          "accent": "#6b7280",
          "neutral": "#292524",
          "base-100": "#171212",
          "info": "#3ABFF8",
          "success": "#36D399",
          "warning": "#FBBD23",
          "error": "#F87272",
        },
      },
    ],
  },
  theme: {
    extend: {

    },
  },
  plugins: [require("daisyui")],
}
