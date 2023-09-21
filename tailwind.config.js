/** @type {import('tailwindcss').Config} */
module.exports = {
  mode: "jit",
  content: ["./app/templates/**/*.html"],
  theme: {
    extend: {},
  },
  daisyui: {
    themes: ["dracula", "winter", "cmyk"],
  },
  plugins: [require("daisyui")],
};
