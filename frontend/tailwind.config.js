/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                primary: '#F37254',
                secondary: '#4472C4',
                success: '#28A745',
                warning: '#FFC107',
                danger: '#DC3545',
            },
            fontFamily: {
                tamil: ['Noto Sans Tamil', 'sans-serif'],
                ui: ['Inter', 'Roboto', 'sans-serif'],
            },
        },
    },
    plugins: [],
}
